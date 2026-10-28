from fastapi.testclient import TestClient
from accounting_copilot.api import create_app


def test_console_has_no_embedded_credentials_or_invoice_data(tmp_path):
    key = "private-test-credential-12345"
    client = TestClient(create_app(tmp_path / "console.db", keys={key:{"actor":"tester","tenant":"secret-tenant","role":"operator"}}))
    response = client.get("/console")
    assert response.status_code == 200
    assert "Factuurwerkbank" in response.text
    assert key not in response.text
    assert "secret-tenant" not in response.text
    assert "localStorage" not in response.text
    assert response.headers["cache-control"] == "no-store"
    assert client.get("/invoices").status_code == 401
