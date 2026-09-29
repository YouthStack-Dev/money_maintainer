# Money Maintainer Backend — Phase 1

FastAPI + PostgreSQL identity foundation.

## Included
- Email/password login
- JWT access tokens
- Rotating persisted refresh sessions
- Logout and password change
- USER / ADMIN / SUPER_ADMIN roles
- User CRUD
- Admin CRUD
- Role-based access guards
- Alembic PostgreSQL migration
- Security unit tests

## Run
cp .env.example .env
docker compose up -d db
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

API docs: http://localhost:8000/docs
