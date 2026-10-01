from datetime import datetime, timedelta, timezone
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.models import OneTimeToken
from app.core.database import SessionLocal
from app.main import app
from app.users.models import User

client = TestClient(app)


def unique_email(label):
    return f'{label}-{uuid.uuid4().hex[:10]}@example.com'

def register(email):
    return client.post('/api/v1/auth/register', params={
        'email': email,
        'full_name': 'Auth Edge User',
        'password': 'StrongPass123!',
    })


def login(email, password='StrongPass123!'):
    return client.post('/api/v1/auth/login', params={'email': email, 'password': password})


def token_for(email, purpose):
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        row = db.scalar(select(OneTimeToken).where(OneTimeToken.user_id == user.id, OneTimeToken.purpose == purpose))
        return row


def test_refresh_invalid_missing_and_rotation():
    email = unique_email('\1'.split('@')[0])
    assert register(email).status_code == 201
    first = login(email).json()['refresh_token']
    assert client.post('/api/v1/auth/refresh', params={'refresh_token_value': ''}).status_code == 401
    rotated = client.post('/api/v1/auth/refresh', params={'refresh_token_value': first})
    assert rotated.status_code == 200
    second = rotated.json()['refresh_token']
    assert second and second != first
    assert client.post('/api/v1/auth/refresh', params={'refresh_token_value': first}).status_code == 401
    assert client.post('/api/v1/auth/refresh', params={'refresh_token_value': second}).status_code == 401


def test_verify_email_success_and_reuse(monkeypatch):
    captured = {}
    monkeypatch.setattr('app.auth.router.send_email', lambda to, subject, body: captured.update(body=body))
    email = unique_email('\1'.split('@')[0])
    assert register(email).status_code == 201
    token = captured['body'].split('token=', 1)[1]
    assert client.post('/api/v1/auth/verify-email', params={'token': token}).status_code == 200
    assert client.post('/api/v1/auth/verify-email', params={'token': token}).status_code == 400
    assert client.post('/api/v1/auth/verify-email', params={'token': ''}).status_code == 400

def test_forgot_password_is_non_enumerating_and_creates_reset_token():
    email = unique_email('\1'.split('@')[0])
    assert register(email).status_code == 201
    known = client.post('/api/v1/auth/forgot-password', params={'email': email})
    unknown = client.post('/api/v1/auth/forgot-password', params={'email': 'missing-auth-edge@example.com'})
    assert known.status_code == unknown.status_code == 200
    assert known.json()['message'] == unknown.json()['message']
    assert token_for(email, 'password_reset') is not None


def test_reset_password_rejects_invalid_and_expired_tokens(monkeypatch):
    captured = {}
    monkeypatch.setattr('app.auth.router.send_email', lambda to, subject, body: captured.update(body=body))
    email = unique_email('\1'.split('@')[0])
    assert register(email).status_code == 201
    assert client.post('/api/v1/auth/reset-password', params={'token': '', 'password': 'StrongPass456!'}).status_code == 400
    assert client.post('/api/v1/auth/reset-password', params={'token': 'bad-token', 'password': 'StrongPass456!'}).status_code == 400
    assert client.post('/api/v1/auth/forgot-password', params={'email': email}).status_code == 200
    token = captured['body'].split('token=', 1)[1]
    assert client.post('/api/v1/auth/reset-password', params={'token': token, 'password': 'short'}).status_code == 422
    assert client.post('/api/v1/auth/reset-password', params={'token': token, 'password': 'StrongPass456!'}).status_code == 200
    assert client.post('/api/v1/auth/reset-password', params={'token': token, 'password': 'StrongPass789!'}).status_code == 400

def test_change_password_requires_auth_and_revokes_sessions():
    email = unique_email('\1'.split('@')[0])
    assert register(email).status_code == 201
    logged = login(email)
    assert logged.status_code == 200
    access = logged.json()['access_token']
    refresh = logged.json()['refresh_token']
    headers = {'Authorization': f'Bearer {access}'}
    assert client.post('/api/v1/auth/change-password', params={'password': 'StrongPass456!'}, headers=headers).status_code == 200
    assert client.post('/api/v1/auth/me', headers=headers).status_code in (404, 405)
    assert client.post('/api/v1/auth/refresh', params={'refresh_token_value': refresh}).status_code == 401
    assert login(email, 'StrongPass123!').status_code == 401
    assert login(email, 'StrongPass456!').status_code == 200


def test_change_password_rejects_weak_password():
    email = unique_email('\1'.split('@')[0])
    assert register(email).status_code == 201
    logged = login(email)
    assert logged.status_code == 200
    headers = {'Authorization': f"Bearer {logged.json()['access_token']}"}
    assert client.post('/api/v1/auth/change-password', params={'password': 'short'}, headers=headers).status_code == 422
    assert client.post('/api/v1/auth/change-password', params={'password': 'StrongPass456!'}, headers={}).status_code == 401
