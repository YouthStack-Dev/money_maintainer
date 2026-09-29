import re
from datetime import date, datetime, time, timezone
from decimal import Decimal, InvalidOperation

from app.transactions.models import TransactionType

_AMOUNT_RE = re.compile(r"(?:₹|rs\.?\s*)?([0-9][0-9,]*(?:\.\d{1,2})?)", re.I)
_DATE_RE = re.compile(r"^(?:(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?|([a-z]{3,9})\s+(\d{1,2}))\s*(?:,)?\s*(.*)$", re.I)
_REFUND_RE = re.compile(r"\b(refund|refunded|cashback)\b", re.I)
_INCOME_RE = re.compile(r"\b(salary|income|received|got paid|got my salary)\b", re.I)
_TRANSFER_RE = re.compile(r"\b(?:transfer|move)\b", re.I)


def split_entries(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[;\n]+", text) if part.strip()]


def extract_date(text: str, today: date) -> tuple[date, str]:
    match = _DATE_RE.match(text.strip())
    if not match:
        return today, text.strip()
    numeric_day, numeric_month, year, month_name, named_day, remainder = match.groups()
    try:
        if month_name:
            month = datetime.strptime(month_name[:3].title(), "%b").month
            parsed = date(today.year, month, int(named_day))
        else:
            parsed_year = int(year) if year else today.year
            if parsed_year < 100:
                parsed_year += 2000
            parsed = date(parsed_year, int(numeric_month), int(numeric_day))
        return parsed, remainder.strip()
    except ValueError:
        return today, text.strip()


def extract_amount(text: str) -> tuple[Decimal | None, str]:
    match = _AMOUNT_RE.search(text)
    if not match:
        return None, text.strip()
    try:
        amount = Decimal(match.group(1).replace(",", ""))
    except InvalidOperation:
        return None, text.strip()
    remainder = (text[:match.start()] + " " + text[match.end():]).strip()
    return amount, re.sub(r"\s+", " ", remainder)


def infer_type(text: str) -> TransactionType | None:
    lowered = text.lower()
    if _TRANSFER_RE.search(lowered):
        return TransactionType.TRANSFER
    if _REFUND_RE.search(lowered):
        return TransactionType.REFUND
    if _INCOME_RE.search(lowered):
        return TransactionType.INCOME
    if not lowered.strip():
        return None
    return TransactionType.EXPENSE


def clean_description(text: str, transaction_type: TransactionType) -> str:
    value = re.sub(r"\b(for|on|of)\s+(?:today|yesterday)\b", "", text, flags=re.I)
    value = re.sub(r"\b(?:paid|received|got)\s+me?\b", "", value, flags=re.I)
    value = re.sub(r"\s+", " ", value).strip(" ,.-")
    return value or transaction_type.value.title()


def parse_entry(text: str, today: date) -> dict:
    transaction_date, body = extract_date(text, today)
    amount, body = extract_amount(body)
    transaction_type = infer_type(body)
    description = clean_description(body, transaction_type) if transaction_type else body
    return {
        "text": text,
        "transaction_type": transaction_type,
        "amount": amount,
        "description": description,
        "transaction_date": datetime.combine(transaction_date, time.min, tzinfo=timezone.utc),
    }
