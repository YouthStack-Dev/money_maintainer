# Personal Finance Home

## Purpose

3F-E is the user's daily starting screen. It combines the financial information that matters for immediate decisions without replacing the detailed domain APIs.

Endpoint:

GET /api/v1/personal-finance-home

The endpoint is read-only.

## Home sections

### Available money

Calculated from active non-credit-card accounts using opening balances and the complete active transaction ledger.

Transfers between accounts are moved between source and destination accounts rather than counted as income or spending.

### This month

Shows:
- income
- refunds
- spending
- net cash flow

Expense totals use EXPENSE transactions only. Transfers do not count as spending.

### Budget

Shows:
- active current-period budget total
- budget spending
- remaining budget

### Credit cards

Shows aggregate configured credit-card outstanding balance.

### Money relationships

Shows:
- money owed to the user from active LENT debts
- money the user owes from active BORROWED debts
- pending office reimbursement amount

### Goals and obligations

Shows:
- active goal count
- goals within seven days of their target date
- overdue debt count
- upcoming debt count
- a short list of debt obligations with person, amount and due date

### Alerts

Shows unread financial-alert count. The existing alert engine remains the source of alert generation.

### Spending and activity

Shows:
- top five current-month spending categories
- five most recent active transactions

## Design boundary

The home endpoint is an aggregation/read model. It does not create financial records and does not become a second source of truth.

Detailed actions remain in:
- Quick Entry
- Financial Relationships
- Corrections
- Conversational Finance
- Accounts
- Transactions
- Budgets
- Debts
- Credit Cards
- Goals
- Alerts

## Security

The endpoint uses the authenticated user and the existing transactions.read permission mapping. Every source query is scoped to the authenticated user.
