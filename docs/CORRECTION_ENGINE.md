# 3F-C — Correction Engine

## Purpose

3F-C lets the user correct an existing financial transaction using natural language without manually navigating a finance form.

The first slices are intentionally conservative: they correct amount, date, or description, or deactivate a duplicate transaction.

## Endpoint

POST /api/v1/corrections

### Explicit transaction

Example: `change transaction 42 amount to 550`

### Contextual transaction

The correction engine can resolve a contextual reference to the user's latest active transaction when the text contains a clear contextual phrase:

- `change that transaction amount to 550`
- `correct the last transaction date to 21/08`
- `update this transaction description to petrol`

Resolution uses the authenticated user's active transactions ordered by transaction date and ID. It never searches another user's transactions.

If no active transaction exists, the target remains missing and the API returns `NEEDS_CONFIRMATION`.

A request without an explicit ID or contextual reference, such as `change amount to 550`, still requires confirmation.

## Delete duplicate

`delete duplicate transaction 42`

Deletion is a soft delete (`is_active=false`) so the original ledger row remains auditable.

## Confirmation

A correction with missing target or correction fields returns `NEEDS_CONFIRMATION`.

The client can resubmit the same text with `confirm=true` and the completed candidate.

## Safety rules

- Corrections are restricted to the authenticated user's transaction.
- Amount must remain positive.
- Transaction rows are soft-deleted, not physically removed.
- Corrections use row locking during execution.
- Relationship-linked corrections are not silently rewritten in this slice because debt, repayment, credit-card and office-reimbursement records can depend on the original financial event.

## Current scope

1. Explicit transaction correction.
2. Contextual correction using the latest active transaction.
3. Amount, date, and description correction.
4. Soft-delete duplicate.

## Next 3F-C slices

1. Account/category correction with ownership validation.
2. Financial relationship corrections: lending/repayment and CC settlement without breaking linked records.
3. Duplicate detection and safe merge.
4. Office reimbursement correction.
5. Correction history / before-after audit view.
