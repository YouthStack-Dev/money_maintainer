from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.users.models import User

client = TestClient(app)


def auth_user(email, name="Test User"):
    r = client.post("/api/v1/auth/register", params={"email": email, "full_name": name, "password": "StrongPass123!"})
    assert r.status_code == 201, r.text
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).one()
        user.is_email_verified = True
        db.commit()
    r = client.post("/api/v1/auth/login", params={"email": email, "password": "StrongPass123!"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_postgres_full_financial_flow_and_edge_cases():
    u1 = auth_user("pg-u1@example.com", "User One")
    u2 = auth_user("pg-u2@example.com", "User Two")

    cash = client.post("/api/v1/accounts", json={"name":"Cash","account_type":"CASH","opening_balance":"1000.00"}, headers=u1)
    bank = client.post("/api/v1/accounts", json={"name":"Bank","account_type":"BANK_ACCOUNT","opening_balance":"5000.00"}, headers=u1)
    cc = client.post("/api/v1/accounts", json={"name":"Card","account_type":"CREDIT_CARD","opening_balance":"0.00"}, headers=u1)
    assert all(r.status_code == 201 for r in (cash, bank, cc))
    cash_id, bank_id, cc_id = [r.json()["id"] for r in (cash, bank, cc)]

    assert client.get(f"/api/v1/accounts/{cash_id}", headers=u2).status_code == 404
    assert client.patch(f"/api/v1/accounts/{cash_id}", json={"name":"Hijack"}, headers=u2).status_code == 404

    food = client.post("/api/v1/categories", json={"name":"Food","category_type":"EXPENSE"}, headers=u1)
    salary = client.post("/api/v1/categories", json={"name":"Salary","category_type":"INCOME"}, headers=u1)
    assert food.status_code == salary.status_code == 201
    food_id, salary_id = food.json()["id"], salary.json()["id"]

    child = client.post("/api/v1/categories", json={"name":"Groceries","category_type":"EXPENSE","parent_id":food_id}, headers=u1)
    assert child.status_code == 201
    child_id = child.json()["id"]
    assert client.post("/api/v1/categories", json={"name":"Bad","category_type":"INCOME","parent_id":food_id}, headers=u1).status_code == 400
    assert client.patch(f"/api/v1/categories/{food_id}", json={"parent_id":child_id}, headers=u1).status_code == 400
    assert client.get(f"/api/v1/categories/{food_id}", headers=u2).status_code == 404

    base = {"transaction_date":"2026-09-10T10:00:00Z"}
    def tx(account_id, kind, amount, category_id=None, transfer_account_id=None, date="2026-09-10T10:00:00Z"):
        payload={**base,"account_id":account_id,"transaction_type":kind,"amount":amount,"transaction_date":date}
        if category_id is not None: payload["category_id"]=category_id
        if transfer_account_id is not None: payload["transfer_account_id"]=transfer_account_id
        return client.post("/api/v1/transactions", json=payload, headers=u1)

    assert tx(bank_id,"INCOME","10000.00",salary_id).status_code == 201
    assert tx(bank_id,"EXPENSE","1200.00",food_id).status_code == 201
    assert tx(bank_id,"REFUND","200.00",food_id).status_code == 201
    assert tx(bank_id,"TRANSFER","500.00",transfer_account_id=cash_id).status_code == 201
    assert tx(cash_id,"EXPENSE","300.00",food_id).status_code == 201
    assert tx(cc_id,"EXPENSE","1000.00",food_id).status_code == 201

    assert tx(bank_id,"TRANSFER","10.00",transfer_account_id=bank_id).status_code == 400
    assert tx(bank_id,"TRANSFER","10.00",category_id=food_id,transfer_account_id=cash_id).status_code == 422
    assert tx(bank_id,"EXPENSE","0.00",food_id).status_code == 422
    assert tx(999999,"EXPENSE","10.00",food_id).status_code == 400
    assert tx(bank_id,"EXPENSE","10.00",999999).status_code == 400
    assert tx(bank_id,"EXPENSE","10.00",food_id, date="2026-09-30T23:59:59Z").status_code == 201

    txs = client.get("/api/v1/transactions", headers=u1)
    assert txs.status_code == 200 and len(txs.json()) == 7
    assert client.get(f"/api/v1/transactions/{txs.json()[0]['id']}", headers=u2).status_code == 404

    summary = client.get("/api/v1/summary", headers=u1)
    assert summary.status_code == 200, summary.text
    s = summary.json()
    assert Decimal(str(s["income"])) == Decimal("10000.00")
    assert Decimal(str(s["expenses"])) == Decimal("2510.00")
    assert Decimal(str(s["refunds"])) == Decimal("200.00")
    assert Decimal(str(s["net_cash_flow"])) == Decimal("7690.00")
    assert Decimal(str(s["total_assets"])) == Decimal("14690.00")
    assert Decimal(str(s["credit_card_debt"])) == Decimal("1000.00")
    assert Decimal(str(s["net_worth"])) == Decimal("13690.00")

    budget = client.post("/api/v1/budgets", json={"category_id":food_id,"name":"September Food","amount":"3000.00","period_start":"2026-09-01T00:00:00Z","period_end":"2026-09-30T23:59:59Z"}, headers=u1)
    assert budget.status_code == 201, budget.text
    budget_id = budget.json()["id"]
    progress = client.get(f"/api/v1/budgets/{budget_id}/progress", headers=u1)
    assert progress.status_code == 200, progress.text
    p = progress.json()
    assert Decimal(str(p["spent"])) == Decimal("2510.00")
    assert Decimal(str(p["remaining"])) == Decimal("490.00")
    assert p["over_budget"] is False

    assert client.post("/api/v1/budgets", json={"category_id":salary_id,"name":"Bad","amount":"100","period_start":"2026-09-01T00:00:00Z","period_end":"2026-09-30T00:00:00Z"}, headers=u1).status_code == 400
    assert client.post("/api/v1/budgets", json={"category_id":food_id,"name":"Bad","amount":"100","period_start":"2026-09-30T00:00:00Z","period_end":"2026-09-01T00:00:00Z"}, headers=u1).status_code == 422
    assert client.get(f"/api/v1/budgets/{budget_id}", headers=u2).status_code == 404

    assert client.delete(f"/api/v1/accounts/{cash_id}", headers=u1).status_code == 200
    assert client.delete(f"/api/v1/categories/{child_id}", headers=u1).status_code == 200
    assert client.delete(f"/api/v1/transactions/{txs.json()[0]['id']}", headers=u1).status_code == 200
    assert client.delete(f"/api/v1/budgets/{budget_id}", headers=u1).status_code == 200


def test_postgres_fk_and_precision_boundaries():
    u = auth_user("pg-boundary@example.com", "Boundary")
    account = client.post("/api/v1/accounts", json={"name":"Precision","account_type":"CASH","opening_balance":"0.01"}, headers=u)
    assert account.status_code == 201
    account_id = account.json()["id"]
    category = client.post("/api/v1/categories", json={"name":"Tiny","category_type":"EXPENSE"}, headers=u)
    assert category.status_code == 201
    category_id = category.json()["id"]
    r = client.post("/api/v1/transactions", json={"account_id":account_id,"category_id":category_id,"transaction_type":"EXPENSE","amount":"0.01","transaction_date":"2026-09-29T12:00:00Z"}, headers=u)
    assert r.status_code == 201, r.text
    assert r.json()["amount"] == "0.01"
    assert client.post("/api/v1/transactions", json={"account_id":account_id,"category_id":category_id,"transaction_type":"EXPENSE","amount":"-0.01","transaction_date":"2026-09-29T12:00:00Z"}, headers=u).status_code == 422


def test_inactive_account_cannot_accept_transactions_and_summary_survives():
    u = auth_user("pg-lifecycle@example.com", "Lifecycle")
    account = client.post("/api/v1/accounts", json={"name":"Lifecycle","account_type":"CASH","opening_balance":"100.00"}, headers=u)
    category = client.post("/api/v1/categories", json={"name":"Lifecycle Expense","category_type":"EXPENSE"}, headers=u)
    assert account.status_code == category.status_code == 201
    account_id, category_id = account.json()["id"], category.json()["id"]
    tx = {"account_id":account_id,"category_id":category_id,"transaction_type":"EXPENSE","amount":"10.00","transaction_date":"2026-09-29T12:00:00Z"}
    assert client.post("/api/v1/transactions", json=tx, headers=u).status_code == 201
    assert client.delete(f"/api/v1/accounts/{account_id}", headers=u).status_code == 200
    r = client.post("/api/v1/transactions", json=tx, headers=u)
    assert r.status_code == 400
    r = client.get("/api/v1/summary", headers=u)
    assert r.status_code == 200, r.text
