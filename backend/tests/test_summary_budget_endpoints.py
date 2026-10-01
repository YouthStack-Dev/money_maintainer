import uuid
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def login():
    email=f"summary-budget-{uuid.uuid4().hex[:10]}@example.com"
    assert client.post("/api/v1/auth/register",params={"email":email,"full_name":"Budget Test","password":"StrongPass123!"}).status_code==201
    r=client.post("/api/v1/auth/login",params={"email":email,"password":"StrongPass123!"})
    assert r.status_code==200
    return {"Authorization":f"Bearer {r.json()['access_token']}"}

def category(h):
    r=client.post("/api/v1/categories",headers=h,json={"name":"Food","category_type":"EXPENSE"})
    assert r.status_code==201,r.text
    return r.json()["id"]

def test_summary_requires_auth_and_returns_financial_shape():
    h=login()
    assert client.get("/api/v1/summary").status_code==401
    r=client.get("/api/v1/summary",headers=h)
    assert r.status_code==200,r.text
    body=r.json()
    assert {"income","expenses","refunds","net_cash_flow","total_assets","credit_card_debt","net_worth","accounts"}<=set(body)

def test_budget_full_lifecycle_and_progress():
    h=login(); category_id=category(h)
    start=datetime.now(timezone.utc)-timedelta(days=2)
    end=start+timedelta(days=30)
    payload={"category_id":category_id,"name":"Food budget","amount":"10000.00","period_start":start.isoformat(),"period_end":end.isoformat()}
    r=client.post("/api/v1/budgets",headers=h,json=payload)
    assert r.status_code==201,r.text
    bid=r.json()["id"]
    assert client.get(f"/api/v1/budgets/{bid}",headers=h).status_code==200
    assert any(x["id"]==bid for x in client.get("/api/v1/budgets",headers=h).json())
    r=client.get(f"/api/v1/budgets/{bid}/progress",headers=h)
    assert r.status_code==200 and r.json()["budget_id"]==bid
    r=client.patch(f"/api/v1/budgets/{bid}",headers=h,json={"name":"Updated food budget","amount":"12000.00"})
    assert r.status_code==200 and r.json()["name"]=="Updated food budget"
    assert client.delete(f"/api/v1/budgets/{bid}",headers=h).status_code==200
    assert client.get(f"/api/v1/budgets/{bid}",headers=h).json()["is_active"] is False

def test_budget_validation_and_user_isolation():
    h=login(); category_id=category(h)
    now=datetime.now(timezone.utc)
    base={"category_id":category_id,"name":"Bad","amount":"100","period_start":now.isoformat(),"period_end":(now-timedelta(days=1)).isoformat()}
    assert client.post("/api/v1/budgets",headers=h,json=base).status_code==422
    base["period_end"]=(now+timedelta(days=1)).isoformat()
    base["name"]=""
    assert client.post("/api/v1/budgets",headers=h,json=base).status_code==422
    assert client.get("/api/v1/budgets/999999999",headers=h).status_code==404
    assert client.get("/api/v1/budgets").status_code==401
