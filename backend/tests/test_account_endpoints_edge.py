import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def register_and_login():
    email = f'account-edge-{uuid.uuid4().hex[:10]}@example.com'
    assert client.post('/api/v1/auth/register', params={'email': email, 'full_name': 'Account Edge', 'password': 'StrongPass123!'}).status_code == 201
    r = client.post('/api/v1/auth/login', params={'email': email, 'password': 'StrongPass123!'})
    assert r.status_code == 200
    return {'Authorization': f"Bearer {r.json()['access_token']}"}

def create(headers, name='Test Cash'):
    r = client.post('/api/v1/accounts', headers=headers, json={'name': name, 'account_type': 'CASH', 'currency': 'INR', 'opening_balance': 100})
    assert r.status_code == 201
    return r.json()['id']

def test_get_update_delete_account_lifecycle():
    h = register_and_login(); account_id = create(h)
    r = client.get(f'/api/v1/accounts/{account_id}', headers=h)
    assert r.status_code == 200 and r.json()['id'] == account_id
    r = client.patch(f'/api/v1/accounts/{account_id}', headers=h, json={'name': 'Updated Cash', 'institution_name': 'Test Bank', 'opening_balance': 250.50})
    assert r.status_code == 200 and r.json()['name'] == 'Updated Cash' and float(r.json()['opening_balance']) == 250.50
    r = client.delete(f'/api/v1/accounts/{account_id}', headers=h)
    assert r.status_code == 200 and r.json()['message'] == 'Account deactivated'
    r = client.get(f'/api/v1/accounts/{account_id}', headers=h)
    assert r.status_code == 200 and r.json()['is_active'] is False
    r = client.delete(f'/api/v1/accounts/{account_id}', headers=h)
    assert r.status_code == 200

def test_account_endpoints_validate_owner_and_input():
    h = register_and_login()
    assert client.get('/api/v1/accounts/999999999', headers=h).status_code == 404
    assert client.patch('/api/v1/accounts/999999999', headers=h, json={'name': 'x'}).status_code == 404
    assert client.delete('/api/v1/accounts/999999999', headers=h).status_code == 404
    account_id = create(h)
    assert client.patch(f'/api/v1/accounts/{account_id}', headers=h, json={'name': ''}).status_code == 422
    assert client.patch(f'/api/v1/accounts/{account_id}', headers=h, json={'currency': 'US'}).status_code == 422
    assert client.patch(f'/api/v1/accounts/{account_id}', headers=h, json={'opening_balance': 'not-money'}).status_code == 422
    assert client.get(f'/api/v1/accounts/{account_id}').status_code == 401
    assert client.patch(f'/api/v1/accounts/{account_id}', json={'name': 'No Auth'}).status_code == 401
    assert client.delete(f'/api/v1/accounts/{account_id}').status_code == 401
