import re
from calendar import monthrange
from datetime import date, timedelta

MONTHS = {name[:3].lower(): i for i, name in enumerate(
    ["January","February","March","April","May","June","July","August","September","October","November","December"], 1
)}

def _period(text: str, today: date):
    t = text.lower()
    m = re.search(r"\b(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\s*(20\d{2})?\b", t)
    if m:
        month = MONTHS[m.group(1)[:3].lower()]
        year = int(m.group(2) or today.year)
        return date(year, month, 1), date(year, month, monthrange(year, month)[1])
    if "last month" in t:
        year, month = today.year, today.month - 1
        if month == 0: year, month = year - 1, 12
        return date(year, month, 1), date(year, month, monthrange(year, month)[1])
    if "this month" in t or "current month" in t:
        return today.replace(day=1), today
    if "yesterday" in t:
        d = today - timedelta(days=1)
        return d, d
    if "today" in t:
        return today, today
    return None, None

def parse_query(text: str, today: date | None = None) -> dict:
    today = today or date.today()
    t = text.strip().lower()
    start, end = _period(t, today)
    if re.search(r"\b(who\s+owes\s+me|owes\s+me|people\s+owe|lent|receivable)", t):
        intent = "MONEY_OWED_TO_ME"
    elif re.search(r"\b(how\s+much\s+do\s+i\s+owe|what\s+do\s+i\s+owe|my\s+debt|borrowed|owe)", t):
        intent = "MONEY_I_OWE"
    elif re.search(r"\b(credit\s*card|cc)\b.*\b(pending|outstanding|due|balance)", t):
        intent = "CREDIT_CARD_STATUS"
    elif re.search(r"\b(net\s+worth|wealth)", t):
        intent = "NET_WORTH"
    elif re.search(r"\b(budget|budgets|remaining\s+budget)", t):
        intent = "BUDGET_STATUS"
    elif re.search(r"\b(save|saving|savings)\b", t):
        intent = "SAVINGS"
    elif re.search(r"\b(spend|spent|spending|expenses?|how\s+much)", t):
        intent = "SPENDING"
    else:
        intent = "FINANCIAL_SUMMARY"
    category = None
    m = re.search(r"\b(?:on|for)\s+([a-z][a-z &'-]{2,40})\??$", t)
    if intent == "SPENDING" and m:
        category = m.group(1).strip()
    person = None
    if intent in {"MONEY_OWED_TO_ME", "MONEY_I_OWE"}:
        m = re.search(r"\b(?:from|to|by|of)\s+([a-z][a-z .'-]{1,50})", t)
        if m: person = m.group(1).strip()
    return {"intent":intent,"start":start.isoformat() if start else None,"end":end.isoformat() if end else None,"category":category,"person":person,"text":text}
