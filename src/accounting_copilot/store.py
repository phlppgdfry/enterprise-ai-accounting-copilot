import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .models import Invoice, Principal


class Conflict(Exception):
    pass


class Missing(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS suppliers (
                  tenant TEXT NOT NULL, id TEXT NOT NULL, name TEXT NOT NULL,
                  approved INTEGER NOT NULL, PRIMARY KEY(tenant,id));
                CREATE TABLE IF NOT EXISTS invoices (
                  id TEXT PRIMARY KEY, tenant TEXT NOT NULL, supplier TEXT NOT NULL,
                  number TEXT NOT NULL, payload TEXT NOT NULL, status TEXT NOT NULL,
                  flags TEXT NOT NULL, creator TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1,
                  created TEXT NOT NULL, UNIQUE(tenant,supplier,number));
                CREATE TABLE IF NOT EXISTS requests (
                  tenant TEXT NOT NULL, key TEXT NOT NULL, digest TEXT NOT NULL, invoice TEXT NOT NULL,
                  PRIMARY KEY(tenant,key));
                CREATE TABLE IF NOT EXISTS outbox (
                  id TEXT PRIMARY KEY, tenant TEXT NOT NULL, invoice TEXT NOT NULL UNIQUE,
                  payload TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', attempts INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS erp_bookings (
                  outbox TEXT PRIMARY KEY, tenant TEXT NOT NULL, invoice TEXT NOT NULL UNIQUE,
                  payload TEXT NOT NULL, created TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS audit (
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT, tenant TEXT NOT NULL, object TEXT NOT NULL,
                  action TEXT NOT NULL, actor TEXT NOT NULL, timestamp TEXT NOT NULL, detail TEXT NOT NULL);
            """)

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def seed(self, tenant="demo"):
        """Explicit synthetic supplier bootstrap; never called automatically by the API."""
        with self.connection() as db:
            db.execute("INSERT OR IGNORE INTO suppliers VALUES (?,?,?,?)",
                       (tenant, "synthetic-office", "Synthetic Office BV (fictional)", 1))

    @staticmethod
    def event(db, p, object_id, action, detail):
        db.execute("INSERT INTO audit(tenant,object,action,actor,timestamp,detail) VALUES (?,?,?,?,?,?)",
                   (p.tenant, object_id, action, p.actor, now(), json.dumps(detail)))

    def submit(self, invoice: Invoice, key: str, p: Principal):
        payload = invoice.model_dump_json()
        digest = hashlib.sha256(payload.encode()).hexdigest()
        with self.connection() as db:
            existing = db.execute("SELECT * FROM requests WHERE tenant=? AND key=?", (p.tenant, key)).fetchone()
            if existing:
                if existing["digest"] != digest:
                    raise Conflict("Idempotency key already used with a different payload")
                return self._get(db, existing["invoice"], p.tenant), False
            supplier = db.execute("SELECT * FROM suppliers WHERE tenant=? AND id=?",
                                  (p.tenant, invoice.supplier_id)).fetchone()
            flags = []
            if not supplier or not supplier["approved"]:
                flags.append("supplier_not_approved")
            if invoice.invoice_date > datetime.now(timezone.utc).date():
                flags.append("future_invoice_date")
            if invoice.total > 10000:
                flags.append("high_value")
            identifier = str(uuid4())
            try:
                db.execute("""INSERT INTO invoices(id,tenant,supplier,number,payload,status,flags,creator,created)
                              VALUES (?,?,?,?,?,?,?,?,?)""",
                           (identifier, p.tenant, invoice.supplier_id, invoice.invoice_number, payload,
                            "blocked" if flags else "pending_review", json.dumps(flags), p.actor, now()))
            except sqlite3.IntegrityError as exc:
                raise Conflict("Supplier invoice number already exists") from exc
            db.execute("INSERT INTO requests VALUES (?,?,?,?)", (p.tenant, key, digest, identifier))
            self.event(db, p, identifier, "invoice.submitted", {"flags": flags})
            return self._get(db, identifier, p.tenant), True

    @staticmethod
    def _get(db, identifier, tenant):
        row = db.execute("SELECT * FROM invoices WHERE id=? AND tenant=?", (identifier, tenant)).fetchone()
        if not row:
            raise Missing("Invoice not found")
        result = dict(row)
        result["payload"] = json.loads(result["payload"])
        result["flags"] = json.loads(result["flags"])
        return result

    def get(self, identifier, p):
        with self.connection() as db:
            return self._get(db, identifier, p.tenant)

    def list_invoices(self, p, limit=100):
        with self.connection() as db:
            ids = db.execute("SELECT id FROM invoices WHERE tenant=? ORDER BY created DESC LIMIT ?",
                             (p.tenant, limit)).fetchall()
            return [self._get(db, row["id"], p.tenant) for row in ids]

    def decide(self, identifier, decision, p):
        with self.connection() as db:
            item = self._get(db, identifier, p.tenant)
            if item["creator"] == p.actor:
                raise Conflict("Four-eyes policy: submitter cannot review their own invoice")
            if item["version"] != decision.expected_version:
                raise Conflict("Version conflict; reload before reviewing")
            if item["status"] not in ("pending_review", "blocked"):
                raise Conflict("Invoice already decided")
            if decision.approve and item["flags"]:
                raise Conflict("Blocked invoices require correction and a new submission; no override")
            status = "approved" if decision.approve else "rejected"
            db.execute("UPDATE invoices SET status=?,version=version+1 WHERE id=?", (status, identifier))
            if decision.approve:
                db.execute("INSERT INTO outbox(id,tenant,invoice,payload) VALUES (?,?,?,?)",
                           (str(uuid4()), p.tenant, identifier, json.dumps(item["payload"])))
            self.event(db, p, identifier, "invoice." + status, {"reason": decision.reason})
            return self._get(db, identifier, p.tenant)

    def export_mock(self, p, fail=False):
        """One atomic local transaction models an idempotent ERP consumer, not a remote ERP guarantee."""
        with self.connection() as db:
            rows = db.execute("SELECT * FROM outbox WHERE tenant=? AND status='pending' LIMIT 100",
                              (p.tenant,)).fetchall()
            exported = []
            for row in rows:
                db.execute("UPDATE outbox SET attempts=attempts+1 WHERE id=?", (row["id"],))
                if fail:
                    self.event(db, p, row["invoice"], "export.failed", {"reason": "synthetic_failure"})
                    continue
                db.execute("INSERT OR IGNORE INTO erp_bookings VALUES (?,?,?,?,?)",
                           (row["id"], p.tenant, row["invoice"], row["payload"], now()))
                db.execute("UPDATE outbox SET status='sent' WHERE id=?", (row["id"],))
                db.execute("UPDATE invoices SET status='exported',version=version+1 WHERE id=?", (row["invoice"],))
                self.event(db, p, row["invoice"], "export.mock_sent", {"outbox": row["id"]})
                exported.append(row["invoice"])
            return {"exported": exported, "failed": len(rows) if fail else 0, "target": "local_mock_erp"}

    def audit(self, identifier, p):
        with self.connection() as db:
            self._get(db, identifier, p.tenant)
            rows = db.execute("SELECT * FROM audit WHERE tenant=? AND object=? ORDER BY sequence",
                              (p.tenant, identifier)).fetchall()
            return [dict(r) for r in rows]

    def metrics(self, p):
        with self.connection() as db:
            counts = db.execute("SELECT status,COUNT(*) count FROM invoices WHERE tenant=? GROUP BY status",
                                (p.tenant,)).fetchall()
            pending = db.execute("SELECT COUNT(*) FROM outbox WHERE tenant=? AND status='pending'",
                                 (p.tenant,)).fetchone()[0]
            return {"invoices_by_status": {r["status"]: r["count"] for r in counts}, "pending_exports": pending,
                    "provider_cost": "not_measured", "data_classification": "synthetic_demo"}
