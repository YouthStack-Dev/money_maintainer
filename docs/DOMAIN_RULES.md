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

## 13. Investments & holdings
Investment holdings are separate from the bank/cash ledger. Supported types are STOCK, MUTUAL_FUND, ETF, BOND, CRYPTO and OTHER.
For each active holding:
- Invested value = quantity × average cost
- Market value = quantity × current price
- Unrealized gain/loss = market value - invested value
- Unrealized return % = unrealized gain/loss ÷ invested value × 100
Changing a holding's valuation fields does not create ledger transactions. Investment purchase/sale transaction history and realized gains are reserved for later Phase 3 work.

## 14. Assets
Supported asset types are PROPERTY, VEHICLE, GOLD and OTHER.
For each active asset:
- Appreciation/depreciation = current value - purchase value
- Appreciation/depreciation % = appreciation/depreciation ÷ purchase value × 100
- A zero purchase value produces 0% percentage
Assets are valuation records and do not create ledger transactions. Asset purchases, financing and disposal transactions remain in the normal ledger and are not automatically inferred from asset records.

## 15. Net-worth history
Net-worth snapshots are daily user-owned valuation records. The unique key is `(user_id, snapshot_date)`, so generating the same date refreshes the existing snapshot instead of creating a duplicate.

Snapshot calculation uses:
- Liquid assets: all non-credit-card account balances derived from opening balances and active ledger transactions
- Investment value: active investment market values
- Other assets: active asset current values
- Lent receivables: outstanding LENT debts except cancelled records
- Credit-card debt: positive outstanding amount represented by negative credit-card balances
- Borrowed debt: outstanding BORROWED debt except cancelled records
- Total assets = liquid assets + investment value + other assets + lent receivables
- Total liabilities = credit-card debt + borrowed debt
- Net worth = total assets - total liabilities

Snapshots are valuation history only. They do not create, modify or reverse ledger transactions. The current implementation aggregates stored monetary values without foreign-exchange conversion; multi-currency conversion is reserved for future work.

## 16. Soft deletion and lifecycle
Accounts, transactions, recurring transactions, users and admins use deactivation. Debts and goals use domain statuses. Investment holdings use is_active soft deletion.

## 16. Migrations
| Migration | Feature |
|---|---|
| 0007 | Recurring transactions |
| 0008 | Debts / lending |
| 0009 | Credit-card control |
| 0010 | Financial goals |
| 0011 | Cash-flow planning |
| 0012 | Financial alerts |
| 0013 | Investment holdings |
| 0014 | Asset tracking |
Always apply the Alembic migration chain rather than manually creating schema objects.
