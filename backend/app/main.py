from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.access import authorize_path
from app.core.database import SessionLocal
from app.core.audit import audit
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.admins.router import router as admins_router
from app.accounts.router import router as accounts_router
from app.categories.router import router as categories_router
from app.transactions.router import router as transactions_router
from app.summary.router import router as summary_router
from app.budgets.router import router as budgets_router

app = FastAPI(title="Money Maintainer API", version="0.1.0", description="Personal finance API with accounts, transactions, budgets and security controls.")

@app.middleware("http")
async def permission_and_audit_middleware(request: Request, call_next):
    db=SessionLocal(); actor_id=None
    try:
        actor_id=authorize_path(db,request.headers.get("authorization"),request.url.path,request.method)
        response=await call_next(request)
        if actor_id and request.method in {"POST","PATCH","PUT","DELETE"}:
            audit(db,actor_id,f"{request.method} {request.url.path}","API",request.url.path)
            db.commit()
        return response
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(admins_router, prefix="/api/v1/admins", tags=["Admins"])
app.include_router(accounts_router, prefix="/api/v1/accounts", tags=["Accounts"])
app.include_router(categories_router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(transactions_router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(summary_router, prefix="/api/v1/summary", tags=["Financial Summary"])
app.include_router(budgets_router, prefix="/api/v1/budgets", tags=["Budgets"])

@app.get("/health")
def health():
    return {"status": "ok"}
