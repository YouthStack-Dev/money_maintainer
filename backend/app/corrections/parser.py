import re
from datetime import date, datetime, timezone
from decimal import Decimal

from app.corrections.schemas import CorrectionAction

_AMOUNT = re.compile(r"(?:₹|rs\.?\s*)?([0-9][0-9,]*(?:\.\d{1,2})?)", re.I)
_ID = re.compile(r"\b(?:transaction|txn|tx)\s*#?\s*(\d+)\b", re.I)
_DATE = re.compile(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{4}))?\b")
_CONTEXT = re.compile(
    r"\b(?:that|this|last|latest|previous|recent)\s+(?:transaction|txn|tx)\b"
    r"|\b(?:that|this)\b",
    re.I,
)
_ACCOUNT = re.compile(
    r"\b(?:account|bank|card|wallet)\s*(?:to|=|is|as)\s+(.+?)(?=$|\s+(?:and|but)\b)",
    re.I,
)
_CATEGORY = re.compile(
    r"\bcategory\s*(?:to|=|is|as)\s+(.+?)(?=$|\s+(?:and|but)\b)",
    re.I,
)
_REIMBURSEMENT_ID = re.compile(
    r"\b(?:office\s+)?reimbursement\s*(?:#|id\s*)?(\d+)\b",
    re.I,
)


def parse_correction(
    text: str,
    today: date,
    transaction_id: int | None = None,
    context_transaction_id: int | None = None,
):
    body = text.strip()
    lower = body.lower()

    reimbursement_match = _REIMBURSEMENT_ID.search(body)
    office_reimbursement = bool(
        reimbursement_match and re.search(r"\boffice\s+reimbursement\b", lower)
    )
    merge_match = re.search(
        r"\bmerge\s+(?:transaction|txn|tx)\s*#?\s*(\d+)\s+(?:into|with)\s+(?:transaction|txn|tx)?\s*#?\s*(\d+)\b",
        lower,
    )
    action = (
        CorrectionAction.OFFICE_REIMBURSEMENT_UPDATE
        if office_reimbursement
        else (
            CorrectionAction.MERGE
            if merge_match
            else (
                CorrectionAction.DELETE
                if re.search(r"\b(?:delete|remove|duplicate)\b", lower)
                else CorrectionAction.UPDATE
            )
        )
    )

    found_id = transaction_id
    duplicate_transaction_id = None
    reimbursement_id = None

    if office_reimbursement:
        reimbursement_id = int(reimbursement_match.group(1))
    elif merge_match:
        duplicate_transaction_id = int(merge_match.group(1))
        found_id = int(merge_match.group(2))
    if found_id is None and not office_reimbursement:
        match = _ID.search(body)
        if match:
            found_id = int(match.group(1))
    if found_id is None and not office_reimbursement and _CONTEXT.search(body):
        found_id = context_transaction_id

    amount = None
    if action in {CorrectionAction.UPDATE, CorrectionAction.OFFICE_REIMBURSEMENT_UPDATE}:
        match = re.search(
            r"\b(?:to|amount)\s*(?:₹|rs\.?\s*)?([0-9][0-9,]*(?:\.\d{1,2})?)\b",
            lower,
            re.I,
        )
        if match:
            amount = Decimal(match.group(1).replace(",", ""))
        else:
            match = _AMOUNT.search(body)
            if match and re.search(r"\b(?:change|correct|update)\b", lower):
                amount = Decimal(match.group(1).replace(",", ""))

    tx_date = None
    match = _DATE.search(body)
    if match:
        day, month, year = (
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3) or today.year),
        )
        tx_date = datetime(year=year, month=month, day=day, tzinfo=timezone.utc)

    description = None
    desc_match = re.search(r"\b(?:description|note)\s*(?:to|=)\s*(.+)$", body, re.I)
    if desc_match:
        description = desc_match.group(1).strip()

    account_name = None
    account_match = _ACCOUNT.search(body)
    if account_match:
        account_name = account_match.group(1).strip().strip(".")
    category_name = None
    category_match = _CATEGORY.search(body)
    if category_match:
        category_name = category_match.group(1).strip().strip(".")

    missing = []
    if not found_id and not office_reimbursement:
        missing.append("transaction_id")
    if office_reimbursement and reimbursement_id is None:
        missing.append("reimbursement_id")
    if action == CorrectionAction.MERGE and duplicate_transaction_id == found_id:
        missing.append("distinct_transactions")

    has_field = any(
        value is not None
        for value in (amount, tx_date, description, account_name, category_name)
    )
    if action in {CorrectionAction.UPDATE, CorrectionAction.OFFICE_REIMBURSEMENT_UPDATE} and not has_field:
        missing.append("correction_fields")

    confidence = "HIGH" if not missing else "MEDIUM"
    reason = (
        None
        if confidence == "HIGH"
        else "Identify the reimbursement and field to change before saving."
        if action == CorrectionAction.OFFICE_REIMBURSEMENT_UPDATE
        else "Identify the transaction and the field to change before saving."
    )
    return {
        "text": body,
        "action": action,
        "transaction_id": found_id,
        "duplicate_transaction_id": duplicate_transaction_id,
        "reimbursement_id": reimbursement_id,
        "amount": amount,
        "transaction_date": tx_date,
        "description": description,
        "account_name": account_name,
        "category_name": category_name,
        "reason": reason,
        "confidence": confidence,
        "missing": missing,
    }
