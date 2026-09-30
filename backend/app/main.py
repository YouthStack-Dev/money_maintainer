from fastapi import FastAPI, Request
from app.core.access import authorize_path
from app.core.database import SessionLocal
from app.core.audit import audit
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.admins.router import router as admins_router
from app.accounts.router import router as accounts_router
from app.categories.router import router as categories_router
from app.transactions.router import router as transactions_router
from app.quick_entry.router import router as quick_entry_router
from app.financial_relationships.router import router as financial_relationships_router
from app.summary.router import router as summary_router
from app.budgets.router import router as budgets_router
from app.recurring_transactions.router import router as recurring_transactions_router
from app.debts.router import router as debts_router
from app.credit_cards.router import router as credit_cards_router
from app.goals.router import router as goals_router
from app.cash_flow.router import router as cash_flow_router
from app.alerts.router import router as alerts_router
from app.investments.router import router as investments_router
from app.investment_transactions.router import router as investment_transactions_router
from app.assets.router import router as assets_router
from app.net_worth.router import router as net_worth_router
from app.wealth_dashboard.router import router as wealth_dashboard_router

app=FastAPI(title="Money Maintainer API",version="0.1.0",description="Personal finance API with accounts, transactions, budgets and security controls.")

@app.middleware("http")
async def permission_and_audit_middleware(request: Request,call_next):
 db=SessionLocal(); actor_id=None
 try:
  actor_id=authorize_path(db,request.headers.get("authorization"),request.url.path,request.method); response=await call_next(request)
  if actor_id and request.method in {"POST","PATCH","PUT","DELETE"}: audit(db,actor_id,f"{request.method} {request.url.path}","API",request.url.path); db.commit()
  return response
 except Exception: db.rollback(); raise
 finally: db.close()

app.include_router(auth_router,prefix="/api/v1/auth",tags=["Auth"])
app.include_router(users_router,prefix="/api/v1/users",tags=["Users"])
app.include_router(admins_router,prefix="/api/v1/admins",tags=["Admins"])
app.include_router(accounts_router,prefix="/api/v1/accounts",tags=["Accounts"])
app.include_router(categories_router,prefix="/api/v1/categories",tags=["Categories"])
app.include_router(transactions_router,prefix="/api/v1/transactions",tags=["Transactions"])
app.include_router(quick_entry_router,prefix="/api/v1/quick-entry",tags=["Quick Entry"])
app.include_router(financial_relationships_router,prefix="/api/v1/financial-relationships",tags=["Financial Relationships"])
app.include_router(summary_router,prefix="/api/v1/summary",tags=["Financial Summary"])
app.include_router(budgets_router,prefix="/api/v1/budgets",tags=["Budgets"])
app.include_router(recurring_transactions_router,prefix="/api/v1/recurring-transactions",tags=["Recurring Transactions"])
app.include_router(debts_router,prefix="/api/v1/debts",tags=["Debts & Lending"])
app.include_router(credit_cards_router,prefix="/api/v1/credit-cards",tags=["Credit Cards"])
app.include_router(goals_router,prefix="/api/v1/goals",tags=["Financial Goals"])
app.include_router(cash_flow_router,prefix="/api/v1/cash-flow",tags=["Cash-Flow Planning"])
app.include_router(alerts_router,prefix="/api/v1/alerts",tags=["Financial Alerts"])
app.include_router(investments_router,prefix="/api/v1/investments",tags=["Investments"])
app.include_router(investment_transactions_router,prefix="/api/v1/investment-transactions",tags=["Investment Transactions"])
app.include_router(assets_router,prefix="/api/v1/assets",tags=["Assets"])
app.include_router(net_worth_router,prefix="/api/v1/net-worth",tags=["Net Worth"])
app.include_router(wealth_dashboard_router,prefix="/api/v1/wealth-dashboard",tags=["Wealth Dashboard"])

@app.get("/health")
def health(): return {"status":"ok"}
