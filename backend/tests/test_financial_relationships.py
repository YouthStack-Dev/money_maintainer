import uuid
from decimal import Decimal

from fastapi.testclient import TestClient

from app.accounts.models import Account, AccountType
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.debts.models import Debt, DebtDirection, DebtStatus
from app.main import app
from app.users.models import Role, User

client = TestClient(app)


def setup_user():
    email = f"relationship-{uuid.uuid4().hex[:10]}@example.com"
    with SessionLocal() as db:
        user = User(
            email=email,
            full_name="Relationship Tester",
            password_hash=hash_password("StrongPass123!"),
            role=Role.USER,
            is_email_verified=True,
        )
        db.add(user)
        db.flush()
        account = Account(
            user_id=user.id,
            name="Test Bank",
            account_type=AccountType.BANK_ACCOUNT,
            currency="INR",
            opening_balance=Decimal("10000.00"),
        )
        db.add(account)
        db.commit()
        user_id, account_id = user.id, account.id

    login = client.post("/api/v1/auth/login",
        params={"email": email, "password": "StrongPass123!"})
    assert login.status_code == 200
    return user_id, account_id, {"Authorization": "Bearer " + login.json()["access_token"]}


def test_lend_requires_confirmation_then_saves_debt():
    _, account_id, headers = setup_user()
    text = "I lent 5000 to Ravi from Test Bank"

    preview = client.post("/api/v1/financial-relationships",
        json={"text": text}, headers=headers)
    assert preview.status_code == 200
    data = preview.json()
    assert data["status"] == "SAVED"
    assert data["candidate"]["intent"] == "LEND"
    assert data["candidate"]["person_name"] == "Ravi"
    assert data["candidate"]["account_id"] == account_id
    assert data["candidate"]["amount"] == "5000"
    body = data
    assert body["debt_id"] is not None

    with SessionLocal() as db:
        debt = db.get(Debt, body["debt_id"])
        assert debt is not None
        assert debt.direction == DebtDirection.LENT
        assert debt.person_name == "Ravi"
        assert debt.original_amount == Decimal("5000.00")
        assert debt.status == DebtStatus.ACTIVE


def test_borrow_saves_borrowed_direction():
    _, _, headers = setup_user()
    text = "I borrowed 2000 from Gagan from Test Bank"
    preview = client.post("/api/v1/financial-relationships",
        json={"text": text}, headers=headers)
    assert preview.status_code == 200
    data = preview.json()
    assert data["candidate"]["intent"] == "BORROW"
    assert data["candidate"]["person_name"] == "Gagan"

    assert data["status"] == "SAVED"
    assert data["debt_id"] is not None


def test_missing_details_do_not_save():
    _, _, headers = setup_user()
    response = client.post("/api/v1/financial-relationships",
        json={"text": "I lent money to Ravi"}, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "NEEDS_CONFIRMATION"
    assert "amount" in body["candidate"]["missing"]
    assert body["candidate"]["confidence"] != "HIGH"


def test_confirmation_guards():
    _, _, headers = setup_user()
    text = "I lent 5000 to Ravi from Test Bank"
    preview = client.post("/api/v1/financial-relationships",
        json={"text": text}, headers=headers).json()
    candidate = preview["candidate"]

    missing_candidate = dict(candidate)
    missing_candidate["missing"] = ["amount"]
    rejected = client.post("/api/v1/financial-relationships",
        json={"text": text, "confirm": True, "candidate": missing_candidate},
        headers=headers)
    assert rejected.status_code == 400

    mismatched = dict(candidate)
    mismatched["text"] = "different text"
    rejected = client.post("/api/v1/financial-relationships",
        json={"text": text, "confirm": True, "candidate": mismatched},
        headers=headers)
    assert rejected.status_code == 400


def test_requires_authentication():
    response = client.post("/api/v1/financial-relationships",
        json={"text": "I lent 5000 to Ravi"})
    assert response.status_code == 401


def test_empty_text_validation():
    _, _, headers = setup_user()
    response = client.post("/api/v1/financial-relationships",
        json={"text": ""}, headers=headers)
    assert response.status_code == 422
