from datetime import date

from app.conversational_finance.parser import parse_query


def test_parse_this_month_spending():
    result = parse_query("How much did I spend this month?", date(2026, 9, 30))
    assert result["intent"] == "SPENDING"
    assert result["start"] == "2026-09-01"
    assert result["end"] == "2026-09-30"


def test_parse_category_spending():
    result = parse_query("How much did I spend on petrol?", date(2026, 9, 30))
    assert result["intent"] == "SPENDING"
    assert result["category"] == "petrol"


def test_parse_money_owed_to_me():
    assert parse_query("Who owes me?", date(2026, 9, 30))["intent"] == "MONEY_OWED_TO_ME"


def test_parse_money_i_owe():
    assert parse_query("How much do I owe?", date(2026, 9, 30))["intent"] == "MONEY_I_OWE"


def test_parse_cc_status():
    assert parse_query("How much is pending on my CC?", date(2026, 9, 30))["intent"] == "CREDIT_CARD_STATUS"


def test_parse_net_worth():
    assert parse_query("What is my net worth?", date(2026, 9, 30))["intent"] == "NET_WORTH"


def test_parse_last_month():
    result = parse_query("Show my last month expenses", date(2026, 9, 30))
    assert result["start"] == "2026-08-01"
    assert result["end"] == "2026-08-31"


def test_parse_savings():
    assert parse_query("How much can I save this month?", date(2026, 9, 30))["intent"] == "SAVINGS"


def test_parse_budget():
    assert parse_query("How much budget is remaining?", date(2026, 9, 30))["intent"] == "BUDGET_STATUS"


def test_unknown_question_falls_back_to_summary():
    assert parse_query("Give me a financial overview", date(2026, 9, 30))["intent"] == "FINANCIAL_SUMMARY"
