# 3F-C — Correction Engine

## Purpose

3F-C lets the user correct an existing financial transaction using natural language without manually navigating a finance form.

The first slice is intentionally conservative: it corrects amount, date, description, or deactivates a duplicate transaction.

## Endpoint

POST /api/v1/corrections

Example: `change transaction 42 amount to 550`

The API returns a structured candidate before saving when required information is ambiguous.

### Delete duplicate

`delete duplicate transaction 42`

Deletion is a soft delete (`is_active=false`) so the original ledger row remains auditable.

### Change date

`correct transaction 42 date to 21/08`

## Confirmation

A correction with missing target or correction fields returns `NEEDS_CONFIRMATION`.

The client can resubmit the same text with `confirm=true` and the completed candidate.

## Safety rules

- Corrections are restricted to the authenticated user’s transaction.
- Amount must remain positive.
- Transaction rows are soft-deleted, not physically removed.
- Corrections use row locking during execution.
- Relationship-linked corrections are not silently rewritten in this slice because debt, repayment, credit-card and office-reimbursement records can depend on the original financial event.

## Next 3F-C slices

1. Contextual correction: “that transaction” using recent transaction context.
2. Account/category correction with ownership validation.
3. Financial relationship corrections: lending/repayment and CC settlement without breaking linked records.
4. Duplicate detection and safe merge.
5. Office reimbursement correction.
6. Correction history / before-after audit view.
