"""Repeatable full workflow through the public REST API, using isolated temporary storage."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from .api import create_app


def main():
    roles = {role: (role + "-synthetic-demo-key-2026") for role in ("operator", "reviewer", "exporter", "auditor")}
    keys = {key: {"actor": role, "tenant": "demo", "role": role} for role, key in roles.items()}
    with TemporaryDirectory() as temp:
        app = create_app(Path(temp) / "demo.sqlite3", keys)
        app.state.store.seed()
        client = TestClient(app)
        def headers(role):
            return {"X-API-Key": roles[role]}
        invoice = {"supplier_id": "synthetic-office", "invoice_number": "SYNTHETIC-2026-001",
                   "invoice_date": "2026-01-10", "currency": "EUR", "net": "100.00", "vat": "21.00",
                   "total": "121.00", "description": "Synthetic office supplies; no real transaction"}
        submitted = client.post("/invoices", json=invoice,
                                headers={**headers("operator"), "Idempotency-Key": "demo-invoice-001"})
        submitted.raise_for_status()
        identifier = submitted.json()["id"]
        approved = client.post(f"/invoices/{identifier}/decision", json={"approve": True,
                               "reason": "Synthetic source and totals checked", "expected_version": 1},
                               headers=headers("reviewer"))
        approved.raise_for_status()
        exported = client.post("/exports/run", headers=headers("exporter"))
        exported.raise_for_status()
        retry = client.post("/exports/run", headers=headers("exporter"))
        retry.raise_for_status()
        audit = client.get(f"/invoices/{identifier}/audit", headers=headers("auditor"))
        audit.raise_for_status()
        print(json.dumps({"invoice": identifier, "approval": approved.json()["status"],
                          "export": exported.json(), "retry": retry.json(), "audit": audit.json()}, indent=2))


if __name__ == "__main__":
    main()
