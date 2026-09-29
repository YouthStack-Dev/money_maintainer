from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.users.models import User
from app.audit.models import AuditLog

client=TestClient(app)


def register(email):
    return client.post("/api/v1/auth/register",params={"email":email,"full_name":"Security User","password":"StrongPass123!"})


def test_register_never_returns_one_time_token():
    r=register("security-token@example.com")
    assert r.status_code==201
    assert "verification_token" not in r.json()


def test_weak_password_rejected():
    r=client.post("/api/v1/auth/register",params={"email":"weak@example.com","full_name":"Weak","password":"password"})
    assert r.status_code==422


def test_refresh_rotation_and_reuse_detection():
    email="rotation@example.com"; assert register(email).status_code==201
    r=client.post("/api/v1/auth/login",params={"email":email,"password":"StrongPass123!"}); assert r.status_code==200
    first=r.json()["refresh_token"]
    r=client.post("/api/v1/auth/refresh",params={"refresh_token_value":first}); assert r.status_code==200
    second=r.json()["refresh_token"]
    r=client.post("/api/v1/auth/refresh",params={"refresh_token_value":first}); assert r.status_code==401
    r=client.post("/api/v1/auth/refresh",params={"refresh_token_value":second}); assert r.status_code==401


def test_login_lockout_and_audit():
    email="lockout@example.com"; assert register(email).status_code==201
    for _ in range(5):
        assert client.post("/api/v1/auth/login",params={"email":email,"password":"WrongPass123!"}).status_code==401
    assert client.post("/api/v1/auth/login",params={"email":email,"password":"StrongPass123!"}).status_code==429
    with SessionLocal() as db:
        assert db.query(AuditLog).filter(AuditLog.action=="REGISTER",AuditLog.target_id==str(db.query(User).filter(User.email==email).one().id)).first()
