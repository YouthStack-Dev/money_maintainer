from fastapi import FastAPI
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.admins.router import router as admins_router
from app.accounts.router import router as accounts_router

app = FastAPI(title="Money Maintainer API", version="0.1.0")
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(admins_router, prefix="/api/v1/admins", tags=["Admins"])
app.include_router(accounts_router, prefix="/api/v1/accounts", tags=["Accounts"])

@app.get("/health")
def health():
    return {"status": "ok"}
