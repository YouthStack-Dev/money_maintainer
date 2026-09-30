from datetime import date, datetime, time, timezone
from decimal import Decimal
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.models import Account, AccountType
from app.debts.models import Debt, DebtDirection, DebtStatus
from app.debts.service import create_debt, repay_debt
from app.financial_relationships.parser import extract_person, infer_relationship
from app.financial_relationships.schemas import RelationshipCandidate, RelationshipIntent
from app.quick_entry.parser import extract_amount, extract_date
from app.transactions.models import Transaction, TransactionType


def _accounts(db: Session, user_id: int):
    return db.scalars(
        select(Account).where(Account.user_id == user_id, Account.is_active.is_(True)).order_by(Account.id)
    ).all()


def _resolve_account(accounts: list[Account], text: str, account_type: AccountType | None = None):
    pool = [a for a in accounts if account_type is None or a.account_type == account_type]
    lowered = text.lower()
    explicit = [
        a for a in pool
        if any(value and value.lower() in lowered for value in (a.name, a.institution_name))
    ]
    if len(explicit) == 1:
        return explicit[0]
    if len(pool) == 1:
        return pool[0]
    return None


def _resolve_transfer_accounts(accounts: list[Account], text: str):
    parts = re.split(r"\b(?:to|->|into)\b", text.lower(), maxsplit=1)
    if len(parts) != 2:
        return None, None
    def match(fragment: str):
        matches = [a for a in accounts if any(v and v.lower() in fragment for v in (a.name, a.institution_name))]
        return matches[0] if len(matches) == 1 else None
    return match(parts[0]), match(parts[1])

def _candidate(db: Session, user_id: int, text: str, today: date) -> RelationshipCandidate:
    tx_date, body, explicit = extract_date(text, today)
    amount, body = extract_amount(body)
    intent = infer_relationship(body)
    accounts = _accounts(db, user_id)
    missing: list[str] = []
    reason = None

    person = extract_person(body, intent)
    account = None
    secondary = None

    if amount is None:
        missing.append("amount")

    if intent is None:
        missing.append("relationship_intent")
        reason = "The message does not clearly identify the financial relationship."

    if intent in {RelationshipIntent.LEND, RelationshipIntent.BORROW,
                  RelationshipIntent.REPAY_BORROWED, RelationshipIntent.RECEIVE_LENT_REPAYMENT}:
        if not person:
            missing.append("person")
            reason = "A person is required for lending or repayment."
        account = _resolve_account(accounts, body)
        if not account:
            missing.append("account")
    elif intent == RelationshipIntent.CREDIT_CARD_PURCHASE:
        account = _resolve_account(accounts, body, AccountType.CREDIT_CARD)
        if not account:
            missing.append("credit_card")
    elif intent == RelationshipIntent.CREDIT_CARD_PAYMENT:
        secondary = _resolve_account(accounts, body, AccountType.CREDIT_CARD)
        if not secondary:
            missing.append("credit_card")
        account = _resolve_account(accounts, body, None)
        if account and secondary and account.id == secondary.id:
            account = None
        if not account:
            bank_accounts = [a for a in accounts if a.account_type in {AccountType.BANK_ACCOUNT, AccountType.CASH, AccountType.WALLET}]
            if len(bank_accounts) == 1:
                account = bank_accounts[0]
            else:
                missing.append("payment_source_account")
    elif intent in {RelationshipIntent.SALARY, RelationshipIntent.REFUND, RelationshipIntent.EMI}:
        account = _resolve_account(accounts, body)
        if not account:
            missing.append("account")
    elif intent == RelationshipIntent.TRANSFER:
        account, secondary = _resolve_transfer_accounts(accounts, body)
        if not account:
            missing.append("source_account")
        if not secondary:
            missing.append("destination_account")
    else:
        account = _resolve_account(accounts, body)

    confidence = "HIGH" if not missing else ("LOW" if "relationship_intent" in missing else "MEDIUM")
    return RelationshipCandidate(
        text=text,
        intent=intent,
        amount=amount,
        person_name=person,
        account_id=account.id if account else None,
        account_name=account.name if account else None,
        secondary_account_id=secondary.id if secondary else None,
        secondary_account_name=secondary.name if secondary else None,
        transaction_date=datetime.combine(tx_date, time.min, tzinfo=timezone.utc),
        confidence=confidence,
        missing=missing,
        reason=reason,
    )


def build_candidate(db: Session, user_id: int, text: str, today: date) -> RelationshipCandidate:
    return _candidate(db, user_id, text, today)


def execute_candidate(db: Session, user_id: int, candidate: RelationshipCandidate):
    if candidate.confidence != "HIGH":
        raise ValueError("Relationship requires confirmation before saving")
    intent = candidate.intent
    amount = Decimal(candidate.amount)
    tx_date = candidate.transaction_date

    if intent in {RelationshipIntent.LEND, RelationshipIntent.BORROW}:
        debt = create_debt(db, user_id, {
            "direction": DebtDirection.LENT if intent == RelationshipIntent.LEND else DebtDirection.BORROWED,
            "account_id": candidate.account_id,
            "person_name": candidate.person_name,
            "original_amount": amount,
            "description": candidate.text,
        }, transaction_date=candidate.transaction_date)
        return None, debt.id, None

    if intent in {RelationshipIntent.REPAY_BORROWED, RelationshipIntent.RECEIVE_LENT_REPAYMENT}:
        direction = DebtDirection.BORROWED if intent == RelationshipIntent.REPAY_BORROWED else DebtDirection.LENT
        debts = db.scalars(
            select(Debt).where(
                Debt.user_id == user_id,
                Debt.direction == direction,
                Debt.person_name.ilike(candidate.person_name),
                Debt.status.in_([DebtStatus.ACTIVE, DebtStatus.PARTIALLY_PAID]),
            ).order_by(Debt.id.desc())
        ).all()
        if len(debts) != 1:
            raise ValueError("Repayment could not be matched to exactly one open debt for this person")
        debt, repayment, tx = repay_debt(db, user_id, debts[0].id, {
            "account_id": candidate.account_id,
            "amount": amount,
            "repayment_date": tx_date.date(),
            "note": candidate.text,
        })
        return tx.id, debt.id, repayment.id

    if intent == RelationshipIntent.CREDIT_CARD_PURCHASE:
        tx = Transaction(
            user_id=user_id,
            account_id=candidate.account_id,
            category_id=None,
            transfer_account_id=None,
            transaction_type=TransactionType.EXPENSE,
            amount=amount,
            description=candidate.text,
            transaction_date=tx_date,
        )
        db.add(tx)
        db.flush()
        return tx.id, None, None

    if intent == RelationshipIntent.TRANSFER:
        tx = Transaction(
            user_id=user_id,
            account_id=candidate.account_id,
            category_id=None,
            transfer_account_id=candidate.secondary_account_id,
            transaction_type=TransactionType.TRANSFER,
            amount=amount,
            description=candidate.text,
            transaction_date=tx_date,
        )
        db.add(tx)
        db.flush()
        return tx.id, None, None

    if intent == RelationshipIntent.CREDIT_CARD_PAYMENT:
        tx = Transaction(
            user_id=user_id,
            account_id=candidate.account_id,
            category_id=None,
            transfer_account_id=candidate.secondary_account_id,
            transaction_type=TransactionType.TRANSFER,
            amount=amount,
            description=candidate.text,
            transaction_date=tx_date,
        )
        db.add(tx)
        db.flush()
        return tx.id, None, None

    tx_type = {
        RelationshipIntent.SALARY: TransactionType.INCOME,
        RelationshipIntent.REFUND: TransactionType.REFUND,
        RelationshipIntent.EMI: TransactionType.EXPENSE,
    }.get(intent)
    if tx_type:
        tx = Transaction(
            user_id=user_id,
            account_id=candidate.account_id,
            category_id=None,
            transfer_account_id=None,
            transaction_type=tx_type,
            amount=amount,
            description=candidate.text,
            transaction_date=tx_date,
        )
        db.add(tx)
        db.flush()
        return tx.id, None, None

    raise ValueError("This relationship type is not implemented yet")
