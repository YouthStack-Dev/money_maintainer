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
- Transfers remain deferred until explicit source/destination parsing is added.

## Safety rule

Ambiguous relationships are returned as NEEDS_CONFIRMATION; they are not silently converted into an expense.

## Accounting boundary

The feature reuses the existing debt and transaction ledger. It does not create a second financial ledger.

## Endpoint

POST /api/v1/financial-relationships

Request: {"text":"7000 lending to Giri"}

A high-confidence relationship is saved immediately. Medium/low-confidence relationships return a structured candidate and missing fields for confirmation.

## Intentionally deferred

- Office reimbursement / office-float mode.
- Multi-debt repayment disambiguation UI.
- Explicit transfer source/destination parsing.
- Correction commands.
- Natural-language conversational queries.
