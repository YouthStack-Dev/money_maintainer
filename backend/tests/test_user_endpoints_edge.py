import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.main import app
from app.users.models import Role, User

client = TestClient(app)


def unique_email(label):
    return f"{label}-{uuid.uuid4().hex[:10]}@example.com"


def create_admin():
    email = unique_email("user-admin")
    with SessionLocal() as db:
        admin = User(
            email=email,
            full_name="User Endpoint Admin",
            password_hash=hash_password("AdminPass123!"),
            role=Role.ADMIN,
            is_email_verified=True,
        )
        db.add(admin)
        db.commit()
    response = client.post(
        "/api/v1/auth/login",
        params={"email": email, "password": "AdminPass123!"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_normal_user():
    email = unique_email("managed")
    with SessionLocal() as db:
        user = User(
            email=email,
            full_name="Managed User",
            password_hash=hash_password("UserPass123!"),
            role=Role.USER,
            is_email_verified=True,
        )
        db.add(user)
        db.commit()
        return user.id, email


def test_user_crud_endpoints():
    headers = create_admin()
    email = unique_email("crud")

    created = client.post(
        "/api/v1/users",
        params={
            "email": email,
            "full_name": "CRUD User",
            "password": "StrongPass123!",
        },
        headers=headers,
    )
    assert created.status_code == 201
    body = created.json()
    user_id = body["id"]
    assert body["email"] == email
    assert body["full_name"] == "CRUD User"
    assert body["role"] == "USER"
    assert body["is_active"] is True
    assert "password_hash" not in body
    assert body["role"] == "USER"
    fetched = client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["id"] == user_id

    updated = client.patch(
        f"/api/v1/users/{user_id}",
        params={"full_name": "Updated User", "is_active": "false"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Updated User"
    assert updated.json()["is_active"] is False

    deleted = client.delete(f"/api/v1/users/{user_id}", headers=headers)
    assert deleted.status_code == 200
    assert deleted.json()["message"] == "User deactivated"

    fetched_after_delete = client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert fetched_after_delete.status_code == 200
    assert fetched_after_delete.json()["is_active"] is False


def test_user_list_contains_user_accounts_only():
    headers = create_admin()
    user_id, email = create_normal_user()

    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200
    rows = response.json()
    ids = {row["id"] for row in rows}
    assert user_id in ids
    assert all(row["role"] == "USER" for row in rows)
    assert any(row["email"] == email for row in rows)


def test_user_duplicate_and_missing_ids():
    headers = create_admin()
    email = unique_email("duplicate")
    params = {"email": email, "full_name": "Duplicate User", "password": "StrongPass123!"}

    assert client.post("/api/v1/users", params=params, headers=headers).status_code == 201
    duplicate = client.post("/api/v1/users", params=params, headers=headers)
    assert duplicate.status_code == 409

    assert client.get("/api/v1/users/999999999", headers=headers).status_code == 404
    assert client.patch(
        "/api/v1/users/999999999",
        params={"full_name": "Missing"},
        headers=headers,
    ).status_code == 404
    assert client.delete("/api/v1/users/999999999", headers=headers).status_code == 404
def test_user_endpoints_require_admin_and_authentication():
    unauthenticated = client.get("/api/v1/users")
    assert unauthenticated.status_code == 401

    user_id, _ = create_normal_user()
    with SessionLocal() as db:
        user = db.get(User, user_id)
        email = user.email

    logged = client.post(
        "/api/v1/auth/login",
        params={"email": email, "password": "UserPass123!"},
    )
    assert logged.status_code == 200
    headers = {"Authorization": f"Bearer {logged.json()['access_token']}"}

    assert client.get("/api/v1/users", headers=headers).status_code == 403
    assert client.get(f"/api/v1/users/{user_id}", headers=headers).status_code == 403
    assert client.patch(
        f"/api/v1/users/{user_id}",
        params={"full_name": "Blocked"},
        headers=headers,
    ).status_code == 403
    assert client.delete(f"/api/v1/users/{user_id}", headers=headers).status_code == 403


def test_user_create_validation():
    headers = create_admin()
    assert client.post(
        "/api/v1/users",
        params={"email": unique_email("invalid"), "full_name": "", "password": "StrongPass123!"},
        headers=headers,
    ).status_code == 422

    bad_password = client.post(
        "/api/v1/users",
        params={"email": unique_email("weak"), "full_name": "Weak", "password": "short"},
        headers=headers,
    )
    assert bad_password.status_code == 422
def test_user_response_does_not_expose_password_hash():
    headers = create_admin()
    _, email = create_normal_user()
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200
    row = next(item for item in response.json() if item["email"] == email)
    assert "password_hash" not in row
    assert row["role"] == "USER"

    with SessionLocal() as db:
        db_user = db.scalar(select(User).where(User.email == email))
        assert db_user is not None
        assert db_user.password_hash
