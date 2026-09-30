# 3F-B — Financial Relationship Entry

3F-B adds relationship-aware natural-language entry on top of the existing ledger.

## Supported relationships

- Lending: "7000 lending to Giri" → LENT debt.
- Borrowing: "5000 borrowed from Sai" → BORROWED debt.
- Borrowed-debt repayment: matched to one open BORROWED debt and recorded through the existing debt repayment flow.
- Lent-money repayment: "Giri paid me 3000" → matched to one open LENT debt and recorded through the existing repayment flow.
- Credit-card purchase: recorded as an EXPENSE on the selected credit-card account.
- Credit-card payment: recorded as a TRANSFER from a bank/cash/wallet account to the selected credit card. It is not another expense.
- Salary: INCOME.
- Refund: REFUND.
- EMI: EXPENSE.
- Explicit transfers: `5000 HDFC to cash` → TRANSFER from HDFC to cash when both accounts can be resolved.\n- Office expense tracking: create an office reimbursement record linked to an existing expense.\n- Office reimbursement: creates a REFUND transaction linked back to the office item; it is not salary.

## Safety rule

Ambiguous relationships are returned as NEEDS_CONFIRMATION; they are not silently converted into an expense.

## Accounting boundary

The feature reuses the existing debt and transaction ledger. It does not create a second financial ledger.

## Endpoint

POST /api/v1/financial-relationships

Request: {"text":"7000 lending to Giri"}

A high-confidence relationship is saved immediately. Medium/low-confidence relationships return a structured candidate and missing fields for confirmation.

## Confirmation flow\n\nIf required information is missing, the endpoint returns `NEEDS_CONFIRMATION` with a structured candidate. The client can resubmit the same text with `confirm=true` and the completed candidate after the user confirms the fields.\n\n## Office reimbursement\n\n`POST /api/v1/office-reimbursements` links an existing personal expense to an office reimbursement record. `POST /api/v1/office-reimbursements/{id}/reimburse?account_id=...` records the reimbursement as a REFUND and marks the office item reimbursed.\n\n## Intentionally deferred\n\n- Multi-debt repayment selection UI when more than one open debt exists for a person.\n- Correction commands.\n- Natural-language conversational queries.
