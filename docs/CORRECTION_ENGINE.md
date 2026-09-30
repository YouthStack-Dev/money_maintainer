# 3F-C — Correction Engine

## Purpose

3F-C lets the user correct an existing financial transaction using natural language without manually navigating a finance form.

The correction engine remains conservative around financial relationships.

## Endpoint

POST /api/v1/corrections

### Explicit transaction

`change transaction 42 amount to 550`

### Contextual transaction

`change that transaction amount to 550`

Context resolves to the user's latest active transaction. If no active transaction exists, confirmation is required.

### Account correction

`change transaction 42 account to HDFC`

The engine resolves the account by exact case-insensitive name among the authenticated user's active accounts. Unknown or inactive accounts require confirmation and are never assigned.

Account correction is not supported for transfer transactions in this slice because transfers have both source and destination accounts.

### Category correction

`change transaction 42 category to Fuel`

The engine resolves the category by exact case-insensitive name among the authenticated user's active categories. The category type must match the transaction:

- INCOME transaction -> INCOME category
- EXPENSE transaction -> EXPENSE category

REFUND and TRANSFER category semantics are intentionally not changed by this slice.

### Confirmation

If the transaction, account, or category cannot be resolved safely, the API returns `NEEDS_CONFIRMATION` rather than guessing.

A confirmed candidate must still resolve to resources owned by the authenticated user.

## Safety rules

- Corrections are restricted to the authenticated user's transaction.
- Amount must remain positive.
- Account/category references must belong to the authenticated user and be active.
- Transfer account changes are not supported here.
- Transaction rows are soft-deleted, not physically removed.
- Corrections use row locking during execution.
- Relationship-linked corrections are not silently rewritten in this slice.

## Current scope

1. Explicit transaction correction.
2. Contextual correction using the latest active transaction.
3. Amount, date, and description correction.
4. Account correction for non-transfer transactions.
5. Category correction for INCOME/EXPENSE transactions.
6. Soft-delete duplicate.

## Financial relationship safety

- Debt repayment transactions are detected through their linked `DebtRepayment.transaction_id`.
- Correcting a repayment amount updates the repayment amount, linked transaction amount, debt outstanding balance, and debt status atomically.
- Correcting a repayment date updates both the transaction date and repayment date.
- A repayment cannot be soft-deleted through generic transaction correction.
- Transactions linked to office reimbursements are blocked from generic correction so reimbursement state cannot drift.
- Credit-card purchases and payments remain ledger-derived transaction corrections; no separate balance is stored to synchronize.

## Next 3F-C slices

1. Duplicate detection and safe merge.
2. Office reimbursement correction.
3. Correction history / before-after audit view.


## Duplicate detection and safe merge

- Duplicate merge syntax: `merge transaction 43 into transaction 42`.
- Transaction 42 is retained; transaction 43 is soft-deleted.
- A merge is allowed only when both active transactions belong to the same user and match exactly on type, amount, account, category, transfer destination, and transaction date.
- The two transaction IDs must be different.
- Debt-repayment-linked and office-reimbursement-linked transactions cannot be merged through the generic correction engine.
- This slice does not attempt fuzzy duplicate matching or automatic merging based on similar descriptions.


## Office reimbursement correction

Office reimbursements are corrected through the reimbursement relationship, not by generic transaction correction.

Examples:

- `change office reimbursement 42 amount to 2500`
- `correct office reimbursement 42 date to 21/08`
- `change office reimbursement 42 description to Twilio refund`

Rules:

- The reimbursement ID must resolve to an active reimbursement owned by the authenticated user.
- CANCELLED reimbursements cannot be corrected.
- Amount corrections require a positive amount.
- For PENDING reimbursements, the linked office expense transaction and reimbursement record are updated together.
- For REIMBURSED reimbursements, the linked office expense transaction, reimbursement transaction, and reimbursement record are updated together.
- Date corrections keep the linked transaction dates synchronized.
- Description correction updates the reimbursement description and the generated reimbursement transaction description; the original office expense description is not silently replaced.
- Account and category changes are not supported through this reimbursement correction intent.
- Generic transaction correction remains blocked for reimbursement-linked transactions.
- The expense/reimbursement transaction links and reimbursement status are preserved.
