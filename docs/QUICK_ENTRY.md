# Quick Entry — 3F-A

## Purpose

Quick Entry converts short natural-language money events into existing transaction records. It does not create a second ledger or replace the Transactions domain.

## Endpoint

POST `/api/v1/quick-entry`

Request example:

```json
{"text":"110 petrol"}
```

The endpoint parses one or more entries, saves only high-confidence candidates, and returns candidates that still need confirmation.

## Supported in 3F-A

- Expense: amount + description
- Income: salary/income wording
- Refund: refund/cashback wording
- Explicit account matching by account or institution name
- Category inference from existing active categories
- Explicit dates: `21/08`, `21/08/2026`, `Sep 1`
- Batch input separated by `;` or new lines
- Batch entries inherit the previous explicit date
- Confidence levels: HIGH, MEDIUM, LOW
- Partial batch save when some entries are high confidence

## Safety rules

- Ambiguous account selection is not silently guessed.
- Account-only input such as `SBI 500` is not silently recorded as an expense.
- Transfers are parsed but deliberately deferred to the later financial-actions stage.
- Final records are normal `Transaction` rows.

## Current limitation

There is no user-level default account field yet. When multiple accounts exist and no account is explicit, Quick Entry asks for account confirmation. A future 3F-A follow-up can add an explicit default-account preference.
