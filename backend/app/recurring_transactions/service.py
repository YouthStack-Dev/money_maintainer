import calendar
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.models import Account
from app.categories.models import Category, CategoryType
from app.recurring_transactions.models import RecurringFrequency, RecurringTransaction, RecurringTransactionRun
from app.transactions.models import Transaction, TransactionType


def _month_end(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def advance_schedule(value: datetime, frequency: RecurringFrequency) -> datetime:
    if frequency == RecurringFrequency.WEEKLY:
        return value.replace(microsecond=0) + timedelta(days=7)
    if frequency == RecurringFrequency.YEARLY:
        year = value.year + 1
        day = min(value.day, _month_end(year, value.month))
        return value.replace(year=year, day=day, microsecond=0)
    month_index = value.year * 12 + value.month - 1 + 1
    year, month0 = divmod(month_index, 12)
    month = month0 + 1
    day = min(value.day, _month_end(year, month))
    return value.replace(year=year, month=month, day=day, microsecond=0)


def validate_dependencies(
    db: Session,
    user_id: int,
    account_id: int,
    category_id: int | None,
    transaction_type: TransactionType,
) -> None:
    account = db.scalar(select(Account).where(Account.id == account_id, Account.user_id == user_id, Account.is_active.is_(True)))
    if not account:
        raise ValueError("Account not found or inactive")

    if category_id is None:
        return

    category = db.scalar(select(Category).where(Category.id == category_id, Category.user_id == user_id, Category.is_active.is_(True)))
    if not category:
        raise ValueError("Category not found or inactive")
    expected = CategoryType.INCOME if transaction_type == TransactionType.INCOME else CategoryType.EXPENSE
    if category.category_type != expected:
        raise ValueError("Category type is incompatible with transaction type")


def create_template(db: Session, user_id: int, values: dict) -> RecurringTransaction:
    validate_dependencies(db, user_id, values["account_id"], values.get("category_id"), values["transaction_type"])
    start = values["start_date"]
    end = values.get("end_date")
    if end is not None and end < start:
        raise ValueError("end_date cannot be before start_date")
    scheduled = datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc)
    template = RecurringTransaction(user_id=user_id, next_run_at=scheduled, **values)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def generate_next(db: Session, user_id: int, recurring_id: int) -> tuple[RecurringTransaction, Transaction, datetime]:
    template = db.scalar(
        select(RecurringTransaction)
        .where(RecurringTransaction.id == recurring_id, RecurringTransaction.user_id == user_id)
        .with_for_update()
    )
    if not template:
        raise ValueError("Recurring transaction not found")
    if not template.is_active:
        raise ValueError("Recurring transaction is inactive")

    scheduled = template.next_run_at
    if scheduled > datetime.now(timezone.utc):
        raise ValueError("Next scheduled run is not due")
    if template.end_date is not None and scheduled.date() > template.end_date:
        template.is_active = False
        db.commit()
        raise ValueError("Recurring transaction has reached its end date")

    validate_dependencies(db, user_id, template.account_id, template.category_id, TransactionType(template.transaction_type))

    existing = db.scalar(
        select(RecurringTransactionRun).where(
            RecurringTransactionRun.recurring_transaction_id == template.id,
            RecurringTransactionRun.scheduled_run_at == scheduled,
        )
    )
    if existing:
        transaction = db.get(Transaction, existing.transaction_id)
        next_run = advance_schedule(scheduled, template.frequency)
        return template, transaction, next_run

    transaction = Transaction(
        user_id=user_id,
        account_id=template.account_id,
        category_id=template.category_id,
        transfer_account_id=None,
        transaction_type=TransactionType(template.transaction_type),
        amount=template.amount,
        description=template.description or template.name,
        transaction_date=scheduled,
    )
    db.add(transaction)
    db.flush()
    db.add(RecurringTransactionRun(
        recurring_transaction_id=template.id,
        scheduled_run_at=scheduled,
        transaction_id=transaction.id,
    ))
    template.last_run_at = scheduled
    next_run = advance_schedule(scheduled, template.frequency)
    template.next_run_at = next_run
    if template.end_date is not None and next_run.date() > template.end_date:
        template.is_active = False
    db.commit()
    db.refresh(template)
    db.refresh(transaction)
    return template, transaction, scheduled
