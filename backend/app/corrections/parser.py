import re
from datetime import date, datetime, timezone
from decimal import Decimal
from app.corrections.schemas import CorrectionAction

_AMOUNT = re.compile(r"(?:₹|rs\.?\s*)?([0-9][0-9,]*(?:\.\d{1,2})?)", re.I)
_ID = re.compile(r"\b(?:transaction|txn|tx)\s*#?\s*(\d+)\b", re.I)
_DATE = re.compile(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{4}))?\b")

def parse_correction(text: str, today: date, transaction_id: int | None = None):
    body = text.strip()
    lower = body.lower()
    action = CorrectionAction.DELETE if re.search(r"\b(?:delete|remove|duplicate)\b", lower) else CorrectionAction.UPDATE
    found_id = transaction_id
    if found_id is None:
        match = _ID.search(body)
        if match:
            found_id = int(match.group(1))

    amount = None
    if action == CorrectionAction.UPDATE:
        match = re.search(r"\b(?:to|amount)\s*(?:₹|rs\.?\s*)?([0-9][0-9,]*(?:\.\d{1,2})?)\b", lower, re.I)
        if match:
            amount = Decimal(match.group(1).replace(",", ""))
        else:
            match = _AMOUNT.search(body)
            if match and re.search(r"\b(?:change|correct|update)\b", lower):
                amount = Decimal(match.group(1).replace(",", ""))

    tx_date = None
    match = _DATE.search(body)
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3) or today.year)
        tx_date = datetime(day=day, month=month, year=year, tzinfo=timezone.utc)

    description = None
    desc_match = re.search(r"\b(?:description|note)\s*(?:to|=)\s*(.+)$", body, re.I)
    if desc_match:
        description = desc_match.group(1).strip()

    missing = []
    if not found_id:
        missing.append("transaction_id")
    if action == CorrectionAction.UPDATE and amount is None and tx_date is None and description is None:
        missing.append("correction_fields")

    confidence = "HIGH" if not missing else "MEDIUM"
    reason = None if confidence == "HIGH" else "Identify the transaction and the field to change before saving."
    return {
        "text": body,
        "action": action,
        "transaction_id": found_id,
        "amount": amount,
        "transaction_date": tx_date,
        "description": description,
        "reason": reason,
        "confidence": confidence,
        "missing": missing,
    }
