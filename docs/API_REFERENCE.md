# API Reference

Base path: /api/v1
Unless otherwise stated, resource endpoints require a bearer access token and the corresponding permission.

## Permission convention
| HTTP method | Required action |
|---|---|
| GET | read |
| POST | create |
| PATCH | update |
| PUT | update |
| DELETE | delete |

# Phase 1 — Identity and Financial Core

## Auth — /api/v1/auth
Authentication endpoints are outside the normal resource permission middleware.
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /register | Register a user and issue tokens |
| POST | /login | Authenticate with email/password |
| POST | /refresh | Rotate a refresh session |
| POST | /logout | Revoke a refresh session |
| POST | /verify-email | Consume an email verification token |
| POST | /forgot-password | Request a password-reset email |
| POST | /reset-password | Consume a password-reset token |
| GET | /me | Return current authenticated user |
| POST | /change-password | Change password and revoke sessions |

## Users — /api/v1/users
Permission prefix: users.*. Admin users operate on normal USER accounts.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List users |
| POST | / | Create a user |
| GET | /{user_id} | Get a user |
| PATCH | /{user_id} | Update user name/active state |
| DELETE | /{user_id} | Deactivate user |

## Admins — /api/v1/admins
Permission prefix: admins.*. Admin listing/get requires admin access; create/update/deactivate requires super-admin access.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List admins |
| POST | / | Create an ADMIN |
| GET | /{admin_id} | Get an admin |
| PATCH | /{admin_id} | Update admin |
| DELETE | /{admin_id} | Deactivate admin |

## Accounts — /api/v1/accounts
Permission prefix: accounts.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List accounts |
| POST | / | Create account |
| GET | /{account_id} | Get account |
| PATCH | /{account_id} | Update account |
| DELETE | /{account_id} | Deactivate account |

## Categories — /api/v1/categories
Permission prefix: categories.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List categories |
| POST | / | Create category |
| GET | /{category_id} | Get category |
| PATCH | /{category_id} | Update category |
| DELETE | /{category_id} | Deactivate category |

## Transactions — /api/v1/transactions
Permission prefix: transactions.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List transactions |
| POST | / | Create transaction |
| GET | /{transaction_id} | Get transaction |
| PATCH | /{transaction_id} | Update transaction |
| DELETE | /{transaction_id} | Deactivate transaction |

## Financial Summary — /api/v1/summary
Permission prefix: summary.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | Ledger-derived income, expenses, refunds, cash flow, assets, credit-card debt, net worth and account balances |

## Budgets — /api/v1/budgets
Permission prefix: budgets.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List budgets |
| POST | / | Create budget |
| GET | /{budget_id} | Get budget |
| PATCH | /{budget_id} | Update budget |
| DELETE | /{budget_id} | Delete/deactivate budget |
| GET | /{budget_id}/progress | Calculate budget spending progress |

# Phase 2 — Financial Control

## 2A Recurring Transactions — /api/v1/recurring-transactions
Permission prefix: recurring_transactions.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List recurring templates |
| POST | / | Create recurring template |
| GET | /{recurring_id} | Get template |
| PATCH | /{recurring_id} | Update template |
| DELETE | /{recurring_id} | Deactivate template |
| POST | /{recurring_id}/generate | Generate next scheduled real transaction |

## 2B Debt & Lending — /api/v1/debts
Permission prefix: debts.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List debts/lending |
| POST | / | Create debt/lending record |
| GET | /summary | Return debt/lending totals |
| GET | /{debt_id} | Get debt |
| PATCH | /{debt_id} | Update debt |
| DELETE | /{debt_id} | Cancel/deactivate debt |
| GET | /{debt_id}/repayments | List repayments |
| POST | /{debt_id}/repayments | Record repayment |

## 2C Credit Cards — /api/v1/credit-cards
Permission prefix: credit_cards.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List configured active cards with derived metrics |
| GET | /{account_id} | Get one card summary |
| PUT | /{account_id} | Configure/update card metadata |

## 2D Financial Goals — /api/v1/goals
Permission prefix: goals.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List goals |
| POST | / | Create goal |
| GET | /{goal_id} | Get goal |
| PATCH | /{goal_id} | Update goal |
| DELETE | /{goal_id} | Cancel goal |
| GET | /{goal_id}/progress | Get calculated progress |
| GET | /{goal_id}/contributions | List contributions |
| POST | /{goal_id}/contributions | Add contribution |
| DELETE | /{goal_id}/contributions/{contribution_id} | Remove contribution |

## 2E Cash-Flow Planning — /api/v1/cash-flow
Permission prefix: cash_flow.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List cash-flow plans |
| POST | / | Create plan |
| GET | /{plan_id} | Get plan |
| PATCH | /{plan_id} | Update plan |
| DELETE | /{plan_id} | Deactivate/delete plan |
| GET | /{plan_id}/items | List planned items |
| POST | /{plan_id}/items | Add planned item |
| PATCH | /{plan_id}/items/{item_id} | Update planned item |
| DELETE | /{plan_id}/items/{item_id} | Deactivate/delete planned item |
| GET | /{plan_id}/forecast | Planned vs actual cash-flow forecast |

## 2F Financial Alerts — /api/v1/alerts
Permission prefix: alerts.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List stored alerts |
| GET | /summary | Current generated alert summary |
| POST | /refresh | Rebuild stored alert snapshot |
| PATCH | /{alert_id}/read | Mark alert as read |

# Phase 3 — Wealth Management

## 3A Investments & Holdings — /api/v1/investments
Permission prefix: investments.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List active investment holdings with derived valuation and unrealized return |
| POST | / | Create an investment holding |
| GET | /summary | Aggregate active holding count, invested value, market value, unrealized gain/loss and return |
| GET | /{holding_id} | Get one investment holding |
| PATCH | /{holding_id} | Update holding details or valuation |
| DELETE | /{holding_id} | Deactivate an investment holding |

Investment holdings are valuation records and do not create or modify bank/cash ledger transactions.

## 3B Assets — /api/v1/assets
Permission prefix: assets.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List active non-investment assets with derived appreciation/depreciation |
| POST | / | Create an asset |
| GET | /summary | Aggregate active asset count, purchase value, current value and appreciation |
| GET | /{asset_id} | Get one asset |
| PATCH | /{asset_id} | Update asset details or valuation |
| DELETE | /{asset_id} | Deactivate an asset |

Supported asset types: PROPERTY, VEHICLE, GOLD and OTHER. Asset records do not create or modify bank/cash ledger transactions.

## 3C Net-Worth History — /api/v1/net-worth
Permission prefix: net_worth.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List historical net-worth snapshots |
| GET | /current | Calculate the current net-worth position without creating a snapshot |
| POST | /snapshots/generate | Create or refresh the snapshot for a requested date; defaults to today |
| GET | /snapshots/{snapshot_id} | Get one historical snapshot |

A snapshot includes liquid assets, investment market value, other assets, lent receivables, credit-card debt, borrowed debt, total assets, total liabilities and net worth. Investment and asset records remain valuation records; snapshot generation does not create ledger transactions.


## 3D Portfolio Performance — /api/v1/investment-transactions
Permission prefix: investment_transactions.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | List investment BUY/SELL transactions; optional holding_id filter |
| POST | / | Record a BUY or SELL and update holding quantity/cost basis |
| GET | /summary | Aggregate investment transaction count, buy value, sell proceeds and realized gain/loss |
| GET | /performance | Return invested value, market value, realized/unrealized gain/loss and total return |
| GET | /allocation | Return current market-value allocation by investment type |

SELL quantity cannot exceed the active holding quantity. BUY transactions update weighted-average cost including fees. SELL transactions persist realized gain/loss using the holding cost basis and fees. These portfolio transactions do not create bank/cash ledger transactions.


## 3E Wealth Dashboard — /api/v1/wealth-dashboard
Permission prefix: wealth_dashboard.*.
| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | Unified live wealth position, investment performance and financial signals |
| GET | /trend | Historical net-worth trend from saved snapshots; optional limit up to 120 |

The dashboard is read-only and derives its current position from existing domain records. Historical trend data comes from 3C net-worth snapshots. No new financial source of truth or ledger transactions are created.


## 3F Personal UX Intelligence

### 3F-A Quick Entry — /api/v1/quick-entry
Natural-language transaction capture with confidence-based saving and confirmation.

### 3F-B Financial Relationships — /api/v1/financial-relationships
Relationship-aware entry for lending, borrowing, repayments, credit-card purchases/payments, salary, refunds, EMI and transfers.

### 3F-C Corrections — /api/v1/corrections
Transaction and office-reimbursement corrections, safe duplicate merge and correction history.

### 3F-E Personal Finance Home — /api/v1/personal-finance-home
Permission prefix: transactions.read.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | Daily read-only finance home |

Returns available money, current-month income/spending/refunds/net cash flow, budget remaining, credit-card outstanding, money owed/to be repaid, pending office reimbursements, goal/debt signals, unread alerts, top spending categories and recent activity.

### 3F-D Conversational Finance — /api/v1/conversational-finance
Permission prefix: transactions.read.
| Method | Endpoint | Purpose |
|---|---|---|
| POST | / | Answer a read-only natural-language financial question |

Supported intents include spending by period/category, money owed to the user, money the user owes, credit-card status, budget status, savings/cash flow, net worth and financial summary. The response includes structured data, follow-up context and suggested follow-up questions.

The endpoint is read-only and does not create or modify financial records. Transfers are excluded from spending/cash-flow expense totals, while refunds are reported separately and included in net cash flow/savings.

# System
## Health
| Method | Endpoint | Purpose |
|---|---|---|
| GET | /health | Return status=ok |

## Interactive API documentation
When the backend is running: Swagger UI /docs, OpenAPI schema /openapi.json, ReDoc /redoc.
The generated OpenAPI schema is the exact request/response schema reference; this document is the human-readable product/API map.