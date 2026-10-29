from conftest import auth, submit


def test_non_ascii_credential_fails_closed(client):
    assert client.get('/invoices', headers={'X-API-Key': b'\xc3\xa9-invalid'}).status_code == 401


def test_approval_requires_boolean(client, invoice):
    identifier = submit(client, invoice).json()['id']
    response = client.post(f'/invoices/{identifier}/decision', headers=auth('reviewer'),
                           json={'approve': 'false', 'reason': 'Review synthetic invoice', 'expected_version': 1})
    assert response.status_code == 422
    assert client.get(f'/invoices/{identifier}', headers=auth('reviewer')).json()['status'] == 'pending_review'
