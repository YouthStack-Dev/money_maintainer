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
Status: In progress

### 3A — Investments & Holdings
Status: Complete
Tracks user-owned investment holdings for stocks, mutual funds, ETFs, bonds, crypto and other instruments. Each holding stores symbol/name, quantity, average cost, current price, currency and notes. The API derives invested value, current market value, unrealized gain/loss and unrealized return percentage.
Endpoints: GET/POST /api/v1/investments, GET /api/v1/investments/summary, GET/PATCH/DELETE /api/v1/investments/{holding_id}.
Investment holdings are valuation records and do not create or modify bank/cash ledger transactions.

### 3B — Assets
Status: Complete
Tracks non-investment assets such as property, vehicles, gold and other assets with purchase/current valuation, purchase date, notes and lifecycle. The API derives appreciation/depreciation and aggregate asset value.
Endpoints: GET/POST /api/v1/assets, GET /api/v1/assets/summary, GET/PATCH/DELETE /api/v1/assets/{asset_id}.
Asset records are valuation records and do not create or modify bank/cash ledger transactions.

### 3C — Net-Worth History
Status: Complete
Stores one user-owned snapshot per date for historical wealth tracking. Snapshots include liquid assets, investment value, other assets, lent receivables, credit-card debt, borrowed debt, total assets, total liabilities and net worth. A generation endpoint calculates the snapshot from current ledger and valuation records and is idempotent for a given user/date.

### 3D — Portfolio Performance
Status: Complete
Adds BUY/SELL investment transactions with quantity validation, weighted-average cost basis updates, fee-aware realized gains, portfolio performance metrics and allocation by investment type. Investment transactions update portfolio holdings but remain separate from the bank/cash ledger.

### 3E — Wealth Dashboard
Status: Complete
Provides a read-only unified wealth view across live liquid assets, investments, other assets, lent receivables, credit-card debt and borrowed debt, plus investment performance, debt/goal signals and historical net-worth trend.

### 3F — Personal UX Intelligence
Status: In progress

#### 3F-A — Quick Entry
Status: Complete
Natural-language transaction capture with amount/date/category/account inference, batch parsing, confidence-based confirmation and normal ledger writes.

#### 3F-B — Financial Relationship Entry
Status: Complete
Relationship-aware entry for lending, borrowing, repayments, credit-card purchases/payments, salary, refunds, EMI and explicit account transfers. Adds confirmation-safe saving and linked office reimbursement tracking so office money is not treated as salary.
Endpoints: POST /api/v1/financial-relationships, GET/POST /api/v1/office-reimbursements, POST /api/v1/office-reimbursements/{reimbursement_id}/reimburse.

#### 3F-C — Correction Engine
Status: Complete
Supports contextual and explicit transaction corrections, amount/date/description/account/category changes, relationship-safe debt repayment corrections, duplicate detection and exact-match merge, office reimbursement correction, confirmation safeguards and correction before/after history.

#### 3F-D — Conversational Finance
Status: Complete
Read-only natural-language financial queries over the existing ledger and control models. Supports period-aware spending, category spending, money owed to the user, money the user owes, credit-card status, budgets, savings/cash flow, net worth and financial summaries. Query context is returned so clients can support follow-up questions without introducing a second financial data model.
Endpoint: POST /api/v1/conversational-finance.

#### 3F-E — Personal Finance Home
Status: Planned

## Phase 4 — Intelligence / Automation
Status: Planned
Potential scope: financial insights, spending analysis, forecasting intelligence, smart categorization, notifications and anomaly detection.

## Phase 5 — Advanced Platform
Status: Planned
Potential scope: advanced reporting, external financial integrations, synchronization, automation and extensibility.
