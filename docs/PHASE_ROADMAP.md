# Phase Roadmap

## Product direction
Money Maintainer is structured as a progressive personal-finance platform. Each phase adds control on top of the previous financial foundation.

Phase 1 → Financial Core → Phase 2 → Financial Control → Phase 3 → Wealth Management → Phase 4 → Intelligence / Automation → Phase 5 → Advanced Platform

## Phase 1 — Financial Core
Status: Complete

Establishes identity, security, ledger and core financial objects.
- User registration and authentication
- JWT access tokens and persisted rotating refresh sessions
- Logout, password change, email verification and password reset
- USER / ADMIN / SUPER_ADMIN roles
- User and admin administration
- Accounts, categories, transactions, transfers and refunds
- Financial summary and budgets
- Permission middleware and audit logging
- PostgreSQL/Alembic foundation

Transaction types: INCOME, EXPENSE, TRANSFER, REFUND. Transfers move value between accounts and are not income or expense. Refunds increase cash flow and account balance.

## Phase 2 — Financial Control
Status: Complete

Adds planning, obligations, credit control and proactive financial visibility without replacing the Phase 1 ledger.

### 2A — Recurring Transactions
Status: Complete
Weekly, monthly and yearly schedules; deterministic month-end handling; income/expense/refund templates; ownership validation; scheduled-run idempotency; real transaction generation; active/inactive lifecycle.
Endpoints: GET/POST /api/v1/recurring-transactions, GET/PATCH/DELETE /api/v1/recurring-transactions/{recurring_id}, POST /api/v1/recurring-transactions/{recurring_id}/generate.

### 2B — Debt & Lending
Status: Complete
Borrowed vs lent tracking, person, original/outstanding amount, due date, lifecycle status, partial/full repayments, repayment history and real ledger integration.
Endpoints: GET/POST /api/v1/debts, GET /api/v1/debts/summary, GET/PATCH/DELETE /api/v1/debts/{debt_id}, GET/POST /api/v1/debts/{debt_id}/repayments.

### 2C — Credit Card Control
Status: Complete
Credit limit, statement day, payment due day, current/outstanding balance, available credit, over-limit amount, utilization and next payment due date.
Endpoints: GET /api/v1/credit-cards, GET /api/v1/credit-cards/{account_id}, PUT /api/v1/credit-cards/{account_id}.

### 2D — Financial Goals
Status: Complete
Target amount/date, description, lifecycle, contributions, progress, remaining amount and automatic completion. Contributions are allocation records and do not create ledger transactions.
Endpoints: GET/POST /api/v1/goals, GET/PATCH/DELETE /api/v1/goals/{goal_id}, GET /progress and /contributions, POST /contributions, DELETE /contributions/{contribution_id}.

### 2E — Cash-Flow Planning
Status: Complete
Named plans, dates, starting balance, planned income/expenses, projected ending balance, actual cash flow, variance and forecast. Actual income includes refunds; transfers are excluded.
Endpoints: GET/POST /api/v1/cash-flow, GET/PATCH/DELETE /api/v1/cash-flow/{plan_id}, GET/POST /items, PATCH/DELETE /items/{item_id}, GET /forecast.

### 2F — Financial Alerts
Status: Complete
Stored user-visible alerts for credit-card due/over-limit, debt due/overdue and goal deadlines. Severity levels are INFO, WARNING and CRITICAL. CASH_FLOW_LOW exists as a model type but has no generation rule yet.
Endpoints: GET /api/v1/alerts, GET /api/v1/alerts/summary, POST /api/v1/alerts/refresh, PATCH /api/v1/alerts/{alert_id}/read.

## Phase 3 — Wealth Management
Status: Planned
Potential scope: investments, assets, net-worth history, portfolio tracking, investment performance and financial protection. No Phase 3 endpoint is implemented until added to the repository and documented.

## Phase 4 — Intelligence / Automation
Status: Planned
Potential scope: financial insights, spending analysis, forecasting intelligence, smart categorization, notifications and anomaly detection.

## Phase 5 — Advanced Platform
Status: Planned
Potential scope: advanced reporting, external financial integrations, synchronization, automation and extensibility.