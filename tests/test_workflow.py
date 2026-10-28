from concurrent.futures import ThreadPoolExecutor

import pytest

from accounting_copilot.models import Invoice, Principal
from accounting_copilot.store import Store
from conftest import auth, submit


def review(client, identifier, approve=True, version=1, headers=None):
    return client.post(f"/invoices/{identifier}/decision", json={"approve": approve,
                       "reason": "Checked synthetic source", "expected_version": version},
                       headers=headers or auth("reviewer"))


def test_end_to_end_persistence_and_exactly_once_mock(client, invoice):
    created = submit(client, invoice)
    assert created.status_code == 201
    identifier = created.json()["id"]
    assert created.json()["payload"]["total"] == "121.00"
    assert review(client, identifier).json()["status"] == "approved"
    exported = client.post("/exports/run", headers=auth("exporter")).json()
    assert exported["exported"] == [identifier]
    assert client.post("/exports/run", headers=auth("exporter")).json()["exported"] == []
    store = Store(client.app.state.store.path)
    p = Principal(actor="auditor", tenant="demo", role="auditor")
    assert store.get(identifier, p)["status"] == "exported"
    assert [x["action"] for x in store.audit(identifier, p)] == [
        "invoice.submitted", "invoice.approved", "export.mock_sent"]


def test_idempotent_submit_and_payload_conflict(client, invoice):
    first = submit(client, invoice)
    assert submit(client, invoice).status_code == 200
    assert submit(client, invoice).json()["id"] == first.json()["id"]
    invoice["description"] = "Different payload"
    assert submit(client, invoice).status_code == 409


def test_duplicate_business_key_with_new_request(client, invoice):
    assert submit(client, invoice).status_code == 201
    assert submit(client, invoice, "different-request-key").status_code == 409


@pytest.mark.parametrize("changes", [
    {"net": "100.005"}, {"total": "122"}, {"net": "NaN"}, {"vat": "-1"},
    {"currency": "USD"}, {"total": "Infinity"}, {"net": "0"},
    {"supplier_id": "../../secret"}, {"bank_account": "forbidden"},
])
def test_invalid_invoice_rejected(client, invoice, changes):
    invoice.update(changes)
    assert submit(client, invoice).status_code == 422


def test_unknown_supplier_cannot_be_approved(client, invoice):
    invoice["supplier_id"] = "unverified"
    result = submit(client, invoice).json()
    assert result["status"] == "blocked"
    assert review(client, result["id"]).status_code == 409
    assert review(client, result["id"], approve=False).json()["status"] == "rejected"
    assert client.post("/exports/run", headers=auth("exporter")).json()["exported"] == []


def test_four_eyes_and_version_control(client, invoice):
    identifier = submit(client, invoice).json()["id"]
    assert review(client, identifier, headers={"X-API-Key": "same-actor-reviewer-test-key"}).status_code == 409
    assert review(client, identifier, version=2).status_code == 409
    assert review(client, identifier).status_code == 200
    assert review(client, identifier).status_code == 409


def test_auth_and_tenant_boundary(client, invoice):
    assert client.get("/invoices").status_code == 401
    assert client.post("/exports/run", headers=auth("operator")).status_code == 403
    identifier = submit(client, invoice).json()["id"]
    other = {"X-API-Key": "other-tenant-test-key-long"}
    assert client.get(f"/invoices/{identifier}", headers=other).status_code == 404
    assert review(client, identifier, headers=other).status_code == 404
    assert client.get("/invoices", headers=other).json() == []


def test_export_failure_keeps_pending_and_retries(client, invoice):
    identifier = submit(client, invoice).json()["id"]
    review(client, identifier)
    p = Principal(actor="exporter", tenant="demo", role="exporter")
    store = client.app.state.store
    assert store.export_mock(p, fail=True)["failed"] == 1
    assert store.metrics(p)["pending_exports"] == 1
    assert store.export_mock(p)["exported"] == [identifier]
    assert store.export_mock(p)["exported"] == []


def test_concurrent_idempotency_has_one_record(client, invoice):
    store = client.app.state.store
    p = Principal(actor="operator", tenant="demo", role="operator")
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: store.submit(Invoice(**invoice), "concurrent-key", p), range(8)))
    assert len({r[0]["id"] for r in results}) == 1
    assert sum(created for _, created in results) == 1


def test_ai_disabled_fails_closed(client, monkeypatch):
    monkeypatch.delenv("ACCOUNTING_AI_MODE", raising=False)
    assert client.post("/ai/classify", json={"description": "paper"}, headers=auth("operator")).status_code == 503


def test_openapi_documents_security(client):
    schema = client.get("/openapi.json").json()
    assert "APIKeyHeader" in schema["components"]["securitySchemes"]
    assert schema["paths"]["/invoices"]["post"]["security"]
