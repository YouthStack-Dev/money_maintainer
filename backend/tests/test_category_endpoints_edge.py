import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def register_and_login():
    email = f'category-edge-{uuid.uuid4().hex[:10]}@example.com'
    assert client.post('/api/v1/auth/register', params={'email': email, 'full_name': 'Category Edge', 'password': 'StrongPass123!'}).status_code == 201
    r = client.post('/api/v1/auth/login', params={'email': email, 'password': 'StrongPass123!'})
    assert r.status_code == 200
    return {'Authorization': f"Bearer {r.json()['access_token']}"}

def create(h, name='Food', category_type='EXPENSE', parent_id=None):
    body = {'name': name, 'category_type': category_type}
    if parent_id is not None:
        body['parent_id'] = parent_id
    r = client.post('/api/v1/categories', headers=h, json=body)
    assert r.status_code == 201, r.text
    return r.json()['id']

def test_category_get_update_delete_lifecycle():
    h = register_and_login()
    parent_id = create(h, 'Food')
    child_id = create(h, 'Restaurant', parent_id=parent_id)
    r = client.get(f'/api/v1/categories/{child_id}', headers=h)
    assert r.status_code == 200 and r.json()['parent_id'] == parent_id
    r = client.patch(f'/api/v1/categories/{child_id}', headers=h, json={'name': 'Dining'})
    assert r.status_code == 200 and r.json()['name'] == 'Dining'
    r = client.patch(f'/api/v1/categories/{child_id}', headers=h, json={'parent_id': None})
    assert r.status_code == 200 and r.json()['parent_id'] is None
    r = client.delete(f'/api/v1/categories/{child_id}', headers=h)
    assert r.status_code == 200 and r.json()['message'] == 'Category deactivated'
    r = client.get(f'/api/v1/categories/{child_id}', headers=h)
    assert r.status_code == 200 and r.json()['is_active'] is False

def test_category_validation_and_auth():
    h = register_and_login()
    parent_id = create(h, 'Food')
    income_id = create(h, 'Salary', category_type='INCOME')
    category_id = create(h, 'Restaurant', parent_id=parent_id)
    assert client.get('/api/v1/categories/999999999', headers=h).status_code == 404
    assert client.patch('/api/v1/categories/999999999', headers=h, json={'name': 'x'}).status_code == 404
    assert client.delete('/api/v1/categories/999999999', headers=h).status_code == 404
    assert client.patch(f'/api/v1/categories/{category_id}', headers=h, json={'name': ''}).status_code == 422
    assert client.patch(f'/api/v1/categories/{category_id}', headers=h, json={'parent_id': income_id}).status_code == 400
    assert client.patch(f'/api/v1/categories/{category_id}', headers=h, json={'parent_id': category_id}).status_code == 400
    assert client.get(f'/api/v1/categories/{category_id}').status_code == 401
    assert client.patch(f'/api/v1/categories/{category_id}', json={'name': 'No Auth'}).status_code == 401
    assert client.delete(f'/api/v1/categories/{category_id}').status_code == 401
