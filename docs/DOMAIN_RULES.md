# Domain and Accounting Rules

## 1. Ownership and isolation
All financial resources are user-owned. User-facing financial queries must scope by authenticated user ID. Referenced accounts and categories must belong to the same user.

## 2. Authentication and authorization
Protected resources use bearer access tokens. GET maps to read, POST to create, PATCH/PUT to update and DELETE to delete. Permission code format is resource.action. SUPER_ADMIN bypasses normal permission lookup.

## 3. Account types
CASH, BANK_ACCOUNT, CREDIT_CARD and WALLET. Credit cards additionally store credit_limit, statement_day and payment_due_day.

## 4. Transaction types
INCOME adds to the account. EXPENSE subtracts. REFUND adds and counts as positive cash flow. TRANSFER moves money from account_id to transfer_account_id and is neither income nor expense.

## 5. Financial summary
Account balance = opening balance + income + refunds - expenses ± transfers. Credit-card debt is the positive amount represented by a negative credit-card balance. Net worth = total assets - credit-card debt.

## 6. Budgets
Budgets use active expense categories. The period end cannot precede the period start. Progress is derived from matching expense transactions.

## 7. Recurring transactions
Templates support INCOME, EXPENSE and REFUND. Recurring transfers are unsupported. Generation creates a real transaction. Scheduled occurrences are idempotent and future occurrences cannot be generated early.

## 8. Debt and lending accounting
| Direction | Origin transaction | Repayment transaction |
|---|---|---|
| BORROWED | INCOME | EXPENSE |
| LENT | EXPENSE | INCOME |
Repayment cannot exceed outstanding amount. Repayment locks the debt row. Zero outstanding amount produces SETTLED status.

## 9. Credit-card calculations
Current card balance is derived from ledger transactions. Outstanding = max(-balance, 0). Available credit = credit limit - outstanding. Over-limit = max(outstanding - credit limit, 0). Utilization = outstanding / credit limit × 100. Over-limit values remain visible.

## 10. Financial goals
Goal current amount is the sum of contribution records. Contributions are allocation/progress records and do not create bank/cash transactions. Goals auto-complete at target. Deleting a contribution can reopen a completed goal.

## 11. Cash-flow planning
Planned items support INCOME and EXPENSE. Forecast includes planned income, planned expenses, planned net cash flow, projected ending balance, actual income, actual expenses, actual net cash flow and variance. Actual income includes refunds. Transfers are excluded.

## 12. Financial alerts
Current rules: credit-card over-limit = CRITICAL; card payment due within 3 days with outstanding balance = WARNING; debt overdue = CRITICAL; debt due within 3 days = WARNING; goal deadline passed = CRITICAL; goal deadline within 7 days = WARNING.
CASH_FLOW_LOW exists as an alert type but is not currently generated.
Refresh deletes existing alerts for the user and creates a fresh current snapshot.

## 13. Soft deletion and lifecycle
Accounts, transactions, recurring transactions, users and admins use deactivation. Debts and goals use domain statuses.

## 14. Phase 2 migrations
| Migration | Feature |
|---|---|
| 0007 | Recurring transactions |
| 0008 | Debts / lending |
| 0009 | Credit-card control |
| 0010 | Financial goals |
| 0011 | Cash-flow planning |
| 0012 | Financial alerts |
Always apply the Alembic migration chain rather than manually creating Phase 2 schema objects.