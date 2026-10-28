import pytest
from fastapi.testclient import TestClient

from accounting_copilot.api import create_app


@pytest.fixture
def invoice():
    return {"supplier_id": "synthetic-office", "invoice_number": "SYNTH-001", "invoice_date": "2026-01-01",
            "currency": "EUR", "net": "100.00", "vat": "21.00", "total": "121.00",
            "description": "Synthetic paper supplies"}


@pytest.fixture
def client(tmp_path):
    keys = {role + "-key-for-synthetic-tests": {"actor": role, "tenant": "demo", "role": role}
            for role in ("operator", "reviewer", "exporter", "auditor")}
    keys["other-tenant-test-key-long"] = {"actor": "other", "tenant": "other", "role": "reviewer"}
    keys["same-actor-reviewer-test-key"] = {"actor": "operator", "tenant": "demo", "role": "reviewer"}
    app = create_app(tmp_path / "test.sqlite3", keys)
    app.state.store.seed()
    with TestClient(app) as result:
        yield result


def auth(role):
    return {"X-API-Key": role + "-key-for-synthetic-tests"}


def submit(client, invoice, key="test-request-001"):
    return client.post("/invoices", json=invoice, headers={**auth("operator"), "Idempotency-Key": key})
