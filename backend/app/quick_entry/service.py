from datetime import date
from decimal import Decimal
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts.models import Account, AccountType
from app.categories.models import Category, CategoryType
from app.quick_entry.parser import parse_entry, split_entries
from app.quick_entry.schemas import QuickEntryCandidate, QuickEntryConfidence
from app.transactions.models import TransactionType

CATEGORY_KEYWORDS = {
    "fuel": ("petrol", "pertol", "diesel", "desile", "fuel", "petrol"),
    "food": ("food", "tiffin", "tiffan", "breakfast", "lunch", "dinner", "snack", "snacks", "gobi", "juice", "tea", "biryani", "kfc", "domino"),
    "rent": ("rent",),
    "utilities": ("current bill", "electricity", "water bill", "utility", "recharge"),
    "vehicle": ("bike wash", "bike repair", "puncture", "toolbox", "vehicle", "car wash", "service"),
    "medicine": ("medicine", "medical", "hospital"),
}


def _account_matches(account: Account, text: str) -> bool:
    haystack = text.lower()
    return any(value and value.lower() in haystack for value in (account.name, account.institution_name))


def _resolve_account(db: Session, user_id: int, text: str) -> tuple[Account | None, bool]:
    accounts = db.scalars(
        select(Account).where(Account.user_id == user_id, Account.is_active.is_(True)).order_by(Account.id)
    ).all()
    explicit = [account for account in accounts if _account_matches(account, text)]
    if len(explicit) == 1:
        return explicit[0], True
    if len(explicit) > 1:
        return None, False

    usable = [account for account in accounts]
    if len(usable) == 1:
        return usable[0], True
    return None, False


def _resolve_category(db: Session, user_id: int, text: str, transaction_type: TransactionType):
    if transaction_type not in {TransactionType.EXPENSE, TransactionType.INCOME, TransactionType.REFUND}:
        return None

    category_type = CategoryType.EXPENSE if transaction_type == TransactionType.EXPENSE else CategoryType.INCOME
    categories = db.scalars(
        select(Category).where(
            Category.user_id == user_id,
            Category.is_active.is_(True),
            Category.category_type == category_type,
        ).order_by(Category.id)
    ).all()
    lowered = text.lower()
    for category in categories:
        if category.name.lower() in lowered:
            return category

    for category in categories:
        key = category.name.lower()
        keywords = CATEGORY_KEYWORDS.get(key, ())
        if any(keyword in lowered for keyword in keywords):
            return category

    return None


def build_candidates(db: Session, user_id: int, text: str, today: date) -> list[QuickEntryCandidate]:
    results = []
    for raw in split_entries(text):
        parsed = parse_entry(raw, today)
        missing = []
        reason = None

        if parsed["amount"] is None:
            missing.append("amount")
        if parsed["transaction_type"] is None:
            missing.append("transaction_type")

        account = None
        account_ok = False
        if parsed["transaction_type"] == TransactionType.TRANSFER:
            missing.append("transfer_accounts")
            reason = "Transfers are intentionally handled in a later Quick Entry stage."
        else:
            account, account_ok = _resolve_account(db, user_id, raw)
            if not account_ok:
                missing.append("account")
                reason = "Account could not be resolved unambiguously."

        category = _resolve_category(db, user_id, parsed["description"] or "", parsed["transaction_type"]) if parsed["transaction_type"] else None

        if missing:
            confidence = QuickEntryConfidence.LOW if "amount" in missing else QuickEntryConfidence.MEDIUM
        elif account_ok:
            confidence = QuickEntryConfidence.HIGH
        else:
            confidence = QuickEntryConfidence.MEDIUM

        results.append(
            QuickEntryCandidate(
                text=raw,
                transaction_type=parsed["transaction_type"],
                amount=parsed["amount"],
                description=parsed["description"],
                category_id=category.id if category else None,
                category_name=category.name if category else None,
                account_id=account.id if account else None,
                account_name=account.name if account else None,
                transaction_date=parsed["transaction_date"],
                confidence=confidence,
                missing=missing,
                reason=reason,
            )
        )
    return results


def save_ready_candidates(db: Session, user_id: int, candidates: list[QuickEntryCandidate]) -> list[int]:
    from app.transactions.models import Transaction

    ids = []
    for candidate in candidates:
        if candidate.confidence != QuickEntryConfidence.HIGH:
            continue
        transaction = Transaction(
            user_id=user_id,
            account_id=candidate.account_id,
            category_id=candidate.category_id,
            transfer_account_id=None,
            transaction_type=candidate.transaction_type,
            amount=Decimal(candidate.amount),
            description=candidate.description,
            transaction_date=candidate.transaction_date,
        )
        db.add(transaction)
        db.flush()
        ids.append(transaction.id)
    return ids
