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

# System
## Health
| Method | Endpoint | Purpose |
|---|---|---|
| GET | /health | Return status=ok |

## Interactive API documentation
When the backend is running: Swagger UI /docs, OpenAPI schema /openapi.json, ReDoc /redoc.
The generated OpenAPI schema is the exact request/response schema reference; this document is the human-readable product/API map.