from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.accounts.models import Account, AccountType
from app.budgets.models import Budget
from app.categories.models import Category
from app.credit_cards.router import _summary
from app.debts.models import Debt, DebtDirection, DebtStatus
from app.net_worth.router import _load_values
from app.transactions.models import Transaction, TransactionType
from app.conversational_finance.parser import parse_query
from app.users.models import User


def _money(value):
    return f"₹{Decimal(value):,.2f}"


def _transactions(db, user_id, start=None, end=None):
    stmt = select(Transaction).where(
        Transaction.user_id == user_id,
        Transaction.is_active.is_(True),
    )
    if start:
        stmt = stmt.where(Transaction.transaction_date >= datetime.combine(start, time.min))
    if end:
        stmt = stmt.where(Transaction.transaction_date < datetime.combine(end + timedelta(days=1), time.min))
    return db.scalars(stmt.order_by(Transaction.transaction_date, Transaction.id)).all()


def _period(parsed, context):
    start = date.fromisoformat(parsed["start"]) if parsed["start"] else None
    end = date.fromisoformat(parsed["end"]) if parsed["end"] else None
    if start is None and context.get("start"):
        start = date.fromisoformat(context["start"])
        end = date.fromisoformat(context["end"])
    if start is None:
        start = date.today().replace(day=1)
        end = date.today()
    return start, end


def answer_query(db: Session, user: User, text: str, context=None):
    context = context or {}
    parsed = parse_query(text)
    intent = parsed["intent"]

    if intent == "SPENDING":
        start, end = _period(parsed, context)
        txs = _transactions(db, user.id, start, end)
        expenses = [tx for tx in txs if tx.transaction_type == TransactionType.EXPENSE]
        categories = {
            c.id: c.name for c in db.scalars(
                select(Category).where(Category.user_id == user.id)
            ).all()
        }
        by_category = defaultdict(Decimal)
        for tx in expenses:
            by_category[categories.get(tx.category_id, "Uncategorized")] += Decimal(tx.amount)
        requested = parsed["category"] or context.get("category")
        if requested:
            matches = [name for name in by_category if requested.lower() in name.lower()]
            total = sum((by_category[name] for name in matches), Decimal("0"))
            answer = (
                f"You spent {_money(total)} on {', '.join(matches)} between "
                f"{start:%d %b %Y} and {end:%d %b %Y}."
                if matches else
                f"I found no spending matching “{requested}” between "
                f"{start:%d %b %Y} and {end:%d %b %Y}."
            )
            data = {"amount": total, "category": requested, "start": start, "end": end}
        else:
            total = sum((Decimal(tx.amount) for tx in expenses), Decimal("0"))
            top = sorted(by_category.items(), key=lambda item: item[1], reverse=True)[:5]
            answer = f"You spent {_money(total)} between {start:%d %b %Y} and {end:%d %b %Y}."
            data = {
                "amount": total,
                "start": start,
                "end": end,
                "top_categories": [{"category": name, "amount": amount} for name, amount in top],
            }
        return answer, data, {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "category": requested,
        }, ["What about petrol?", "Where did most of it go?"]

    if intent == "MONEY_OWED_TO_ME":
        stmt = select(Debt).where(
            Debt.user_id == user.id,
            Debt.direction == DebtDirection.LENT,
            Debt.status != DebtStatus.CANCELLED,
            Debt.outstanding_amount > 0,
        )
        if parsed["person"]:
            stmt = stmt.where(func.lower(Debt.person_name).contains(parsed["person"].lower()))
        debts = db.scalars(stmt.order_by(Debt.person_name)).all()
        grouped = defaultdict(Decimal)
        for debt in debts:
            grouped[debt.person_name] += Decimal(debt.outstanding_amount)
        total = sum(grouped.values(), Decimal("0"))
        answer = f"People owe you {_money(total)}." if grouped else "Nobody currently owes you anything."
        return answer, {
            "total": total,
            "people": [{"person": person, "amount": amount} for person, amount in grouped.items()],
        }, {}, ["Who owes me the most?"]

    if intent == "MONEY_I_OWE":
        stmt = select(Debt).where(
            Debt.user_id == user.id,
            Debt.direction == DebtDirection.BORROWED,
            Debt.status != DebtStatus.CANCELLED,
            Debt.outstanding_amount > 0,
        )
        if parsed["person"]:
            stmt = stmt.where(func.lower(Debt.person_name).contains(parsed["person"].lower()))
        debts = db.scalars(stmt.order_by(Debt.person_name)).all()
        borrowed = sum((Decimal(debt.outstanding_amount) for debt in debts), Decimal("0"))
        cards = db.scalars(select(Account).where(
            Account.user_id == user.id,
            Account.account_type == AccountType.CREDIT_CARD,
            Account.is_active.is_(True),
        )).all()
        card_debt = Decimal("0")
        for card in cards:
            if card.credit_limit is not None and card.statement_day is not None and card.payment_due_day is not None:
                card_debt += max(Decimal("0"), -Decimal(_summary(db, user.id, card).current_balance))
        total = borrowed + card_debt
        return f"You owe {_money(total)} in borrowed money and card debt.", {
            "borrowed_debt": borrowed,
            "credit_card_debt": card_debt,
            "total": total,
        }, {}, ["How much do I owe Teja?"]

    if intent == "CREDIT_CARD_STATUS":
        cards = db.scalars(select(Account).where(
            Account.user_id == user.id,
            Account.account_type == AccountType.CREDIT_CARD,
            Account.is_active.is_(True),
        )).all()
        rows = []
        for card in cards:
            if card.credit_limit is not None and card.statement_day is not None and card.payment_due_day is not None:
                summary = _summary(db, user.id, card)
                rows.append({
                    "account_id": card.id,
                    "name": card.name,
                    "outstanding": summary.outstanding_balance,
                    "available": summary.available_credit,
                    "due_date": summary.next_payment_due_date,
                })
        total = sum((row["outstanding"] for row in rows), Decimal("0"))
        return f"Your configured credit cards have {_money(total)} outstanding.", {
            "cards": rows,
            "total_outstanding": total,
        }, {}, ["What is my SBI card balance?"]

    if intent == "NET_WORTH":
        values = _load_values(db, user.id)
        return f"Your current net worth is {_money(values['net_worth'])}.", values, {}, [
            "Show my assets.", "Show my liabilities."
        ]

    if intent == "BUDGET_STATUS":
        today = date.today()
        budgets = db.scalars(select(Budget).where(
            Budget.user_id == user.id,
            Budget.is_active.is_(True),
            Budget.period_start <= datetime.combine(today, time.max),
            Budget.period_end >= datetime.combine(today, time.min),
        )).all()
        txs = _transactions(db, user.id, today.replace(day=1), today)
        spent = defaultdict(Decimal)
        for tx in txs:
            if tx.transaction_type == TransactionType.EXPENSE:
                spent[tx.category_id] += Decimal(tx.amount)
        rows = []
        for budget in budgets:
            used = spent[budget.category_id]
            rows.append({
                "budget": budget.name,
                "category_id": budget.category_id,
                "budget_amount": budget.amount,
                "spent": used,
                "remaining": Decimal(budget.amount) - used,
            })
        total_budget = sum((row["budget_amount"] for row in rows), Decimal("0"))
        total_spent = sum((row["spent"] for row in rows), Decimal("0"))
        remaining = total_budget - total_spent
        return f"You have {_money(remaining)} remaining across active budgets.", {
            "budgets": rows,
            "total_budget": total_budget,
            "total_spent": total_spent,
            "remaining": remaining,
        }, {}, ["Which budget is closest to its limit?"]

    if intent == "SAVINGS":
        start, end = _period(parsed, context)
        txs = _transactions(db, user.id, start, end)
        income = sum((Decimal(tx.amount) for tx in txs if tx.transaction_type == TransactionType.INCOME), Decimal("0"))
        refunds = sum((Decimal(tx.amount) for tx in txs if tx.transaction_type == TransactionType.REFUND), Decimal("0"))
        expenses = sum((Decimal(tx.amount) for tx in txs if tx.transaction_type == TransactionType.EXPENSE), Decimal("0"))
        net = income + refunds - expenses
        return f"Your current net savings for the period is {_money(net)}.", {
            "income": income, "refunds": refunds, "expenses": expenses,
            "net_savings": net, "start": start, "end": end,
        }, {"start": start.isoformat(), "end": end.isoformat()}, ["How much did I spend this month?"]

    txs = _transactions(db, user.id, date.today().replace(day=1), date.today())
    income = sum((Decimal(tx.amount) for tx in txs if tx.transaction_type == TransactionType.INCOME), Decimal("0"))
    refunds = sum((Decimal(tx.amount) for tx in txs if tx.transaction_type == TransactionType.REFUND), Decimal("0"))
    expenses = sum((Decimal(tx.amount) for tx in txs if tx.transaction_type == TransactionType.EXPENSE), Decimal("0"))
    values = _load_values(db, user.id)
    net_cash_flow = income + refunds - expenses
    return (
        f"This month: {_money(income)} income, {_money(expenses)} spending, "
        f"{_money(refunds)} refunds, and {_money(net_cash_flow)} net cash flow. "
        f"Current net worth is {_money(values['net_worth'])}."
    ), {
        "income": income, "expenses": expenses, "refunds": refunds,
        "net_cash_flow": net_cash_flow, "net_worth": values["net_worth"],
    }, {}, ["How much do I owe?", "Who owes me?"]
