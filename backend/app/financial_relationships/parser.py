import re

from app.financial_relationships.schemas import RelationshipIntent

def infer_relationship(text: str) -> RelationshipIntent | None:
    s = text.lower()
    if re.search(r"\b(?:cc|credit card)\b.*\b(?:paid|payment|settle|clear)\b|\b(?:paid|payment|settle|clear)\b.*\b(?:cc|credit card)\b", s):
        return RelationshipIntent.CREDIT_CARD_PAYMENT
    if re.search(r"\b(?:salary|salary received|got my salary)\b", s):
        return RelationshipIntent.SALARY
    if re.search(r"\b(?:refund|refunded|cashback)\b", s):
        return RelationshipIntent.REFUND
    if re.search(r"\b(?:transfer|moved?|move)\b", s):
        return RelationshipIntent.TRANSFER
    if re.search(r"\b(?:emi|installment)\b", s):
        return RelationshipIntent.EMI
    if re.search(r"\b(?:lending|lent|gave|given)\b", s) and re.search(r"\b(?:to)\b", s):
        return RelationshipIntent.LEND
    if re.search(r"\b(?:borrowed|borrow|took)\b", s) and re.search(r"\b(?:from)\b", s):
        return RelationshipIntent.BORROW
    if re.search(r"\b(?:paid|returned|repaid|repayment)\b", s) and re.search(r"\b(?:back|to)\b", s):
        return RelationshipIntent.REPAY_BORROWED
    if re.search(r"\b(?:paid me|returned|repaid)\b", s):
        return RelationshipIntent.RECEIVE_LENT_REPAYMENT
    if re.search(r"\b(?:cc|credit card)\b", s):
        return RelationshipIntent.CREDIT_CARD_PURCHASE
    return None

def extract_person(text: str, intent: RelationshipIntent | None) -> str | None:
    s = text.strip()
    if intent == RelationshipIntent.LEND:
        m = re.search(r"\bto\s+([A-Za-z][A-Za-z .'-]{1,80}?)(?:\s+from\s+|\s+using\s+|$)", s, re.I)
        return m.group(1).strip() if m else None
    if intent == RelationshipIntent.BORROW:
        m = re.search(r"\bfrom\s+([A-Za-z][A-Za-z .'-]{1,80}?)(?:\s+using\s+|\s+from\s+|$)", s, re.I)
        return m.group(1).strip() if m else None
    m = re.search(r"\b(?:to|from|in)\s+([A-Za-z][A-Za-z .'-]{1,80}?)(?:\s+(?:he|she|paid|gave)\b|$)", s, re.I)
    if m:
        return m.group(1).strip()
    m = re.match(r"^([A-Za-z][A-Za-z .'-]{1,80}?)\s+(?:paid|returned|repaid)\b", s, re.I)
    return m.group(1).strip() if m else None
