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

## Next 3F-C slices

1. Financial relationship corrections: lending/repayment and CC settlement without breaking linked records.
2. Duplicate detection and safe merge.
3. Office reimbursement correction.
4. Correction history / before-after audit view.
