from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.accounts.models import Account
from app.categories.models import Category, CategoryType
from app.core.database import SessionLocal
from app.recurring_transactions.models import RecurringFrequency, RecurringTransactionRun
from app.recurring_transactions.schemas import RecurringTransactionCreate
from app.recurring_transactions.service import advance_schedule, create_template, generate_next
from app.transactions.models import TransactionType
from app.users.models import User


@pytest.fixture
def data():
    db = SessionLocal()
    email = f"recurring-{uuid4()}@example.com"
    user = User(email=email, full_name="Recurring Test", password_hash="test")
    db.add(user)
    db.flush()
    account = Account(user_id=user.id, name="Test Bank", account_type="BANK_ACCOUNT")
    category = Category(user_id=user.id, name="Bills", category_type=CategoryType.EXPENSE)
    db.add_all([account, category])
    db.commit()
    db.refresh(user)
    db.refresh(account)
    db.refresh(category)
    yield db, user, account, category
    db.rollback()
    db.delete(user)
    db.commit()
    db.close()


def test_frequency_schedule_boundaries():
    start = datetime(2026, 1, 31, tzinfo=timezone.utc)
    assert advance_schedule(start, RecurringFrequency.WEEKLY).date() == date(2026, 2, 7)
    assert advance_schedule(start, RecurringFrequency.MONTHLY).date() == date(2026, 2, 28)
    assert advance_schedule(datetime(2024, 2, 29, tzinfo=timezone.utc), RecurringFrequency.YEARLY).date() == date(2025, 2, 28)


def test_schema_rejects_transfer_and_bad_dates():
    with pytest.raises(ValidationError):
        RecurringTransactionCreate(
            name="Transfer", account_id=1, transaction_type=TransactionType.TRANSFER,
            amount=Decimal("10"), frequency=RecurringFrequency.MONTHLY, start_date=date(2026, 2, 1),
        )
    with pytest.raises(ValidationError):
        RecurringTransactionCreate(
            name="Bad", account_id=1, transaction_type=TransactionType.EXPENSE,
            amount=Decimal("10"), frequency=RecurringFrequency.MONTHLY,
            start_date=date(2026, 2, 2), end_date=date(2026, 2, 1),
        )


@pytest.mark.parametrize("frequency", list(RecurringFrequency))
def test_generation_creates_real_transaction_and_advances(data, frequency):
    db, user, account, category = data
    item = create_template(db, user.id, {
        "name": "Recurring bill", "description": "Monthly bill", "account_id": account.id,
        "category_id": category.id, "transaction_type": TransactionType.EXPENSE,
        "amount": Decimal("500.00"), "frequency": frequency, "start_date": date(2026, 1, 31),
        "end_date": None, "is_active": True,
    })
    item, tx, scheduled = generate_next(db, user.id, item.id)
    assert tx.transaction_type == TransactionType.EXPENSE
    assert tx.amount == Decimal("500.00")
    assert tx.transaction_date == scheduled
    assert item.last_run_at == scheduled
    assert item.next_run_at > scheduled


def test_generation_is_idempotent_per_schedule(data):
    db, user, account, category = data
    item = create_template(db, user.id, {
        "name": "Idempotent", "description": None, "account_id": account.id,
        "category_id": category.id, "transaction_type": TransactionType.EXPENSE,
        "amount": Decimal("100.00"), "frequency": RecurringFrequency.MONTHLY,
        "start_date": date(2026, 1, 1), "end_date": None, "is_active": True,
    })
    _, first, scheduled = generate_next(db, user.id, item.id)
    item.next_run_at = scheduled
    db.commit()
    _, second, _ = generate_next(db, user.id, item.id)
    assert first.id == second.id
    assert db.query(RecurringTransactionRun).filter_by(recurring_transaction_id=item.id).count() == 1


def test_end_date_stops_after_last_run(data):
    db, user, account, category = data
    item = create_template(db, user.id, {
        "name": "Ending", "description": None, "account_id": account.id,
        "category_id": category.id, "transaction_type": TransactionType.EXPENSE,
        "amount": Decimal("100.00"), "frequency": RecurringFrequency.MONTHLY,
        "start_date": date(2026, 1, 31), "end_date": date(2026, 2, 28), "is_active": True,
    })
    item, _, _ = generate_next(db, user.id, item.id)
    item, _, _ = generate_next(db, user.id, item.id)
    assert item.is_active is False
    with pytest.raises(ValueError):
        generate_next(db, user.id, item.id)


def test_inactive_dependencies_and_multi_user_isolation(data):
    db, user, account, category = data
    other = User(email=f"other-{uuid4()}@example.com", full_name="Other", password_hash="test")
    db.add(other)
    db.flush()
    other_account = Account(user_id=other.id, name="Other Bank", account_type="BANK_ACCOUNT")
    db.add(other_account)
    db.commit()

    with pytest.raises(ValueError, match="Account not found"):
        create_template(db, user.id, {
            "name": "Bad owner", "description": None, "account_id": other_account.id,
            "category_id": None, "transaction_type": TransactionType.EXPENSE,
            "amount": Decimal("10"), "frequency": RecurringFrequency.WEEKLY,
            "start_date": date(2026, 1, 1), "end_date": None, "is_active": True,
        })

    account.is_active = False
    db.commit()
    with pytest.raises(ValueError, match="Account not found or inactive"):
        create_template(db, user.id, {
            "name": "Inactive", "description": None, "account_id": account.id,
            "category_id": category.id, "transaction_type": TransactionType.EXPENSE,
            "amount": Decimal("10"), "frequency": RecurringFrequency.WEEKLY,
            "start_date": date(2026, 1, 1), "end_date": None, "is_active": True,
        })
    db.delete(other)
    db.commit()
