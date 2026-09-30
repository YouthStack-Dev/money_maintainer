# Conversational Finance

## Purpose

3F-D adds a read-only natural-language query layer above the existing Money Maintainer financial model.

The conversational layer does not create, update or delete financial records. It reads the existing ledger and domain records and returns an answer plus structured data.

## Endpoint

POST /api/v1/conversational-finance

Request fields:
- text: the user's financial question
- context: optional context returned by an earlier response

Response fields:
- status
- intent
- human-readable answer
- structured data
- context for follow-up questions
- suggested follow-up queries

## Supported questions

### Spending
- How much did I spend this month?
- Show my September expenses
- Show my last month expenses
- How much did I spend on petrol?

Spending is based on active EXPENSE transactions. Transfers are not counted as spending. Refunds are kept separate from expense totals.

### Money owed to the user
- Who owes me?
- Who owes me the most?
- How much does Teja owe me?

Uses active LENT debts and outstanding amounts, grouped by person.

### Money the user owes
- How much do I owe?
- How much do I owe Teja?

Combines outstanding BORROWED debts with configured credit-card debt.

### Credit cards
- How much is pending on my CC?
- What is my SBI card balance?

Returns configured cards, outstanding balance, available credit and next payment due date.

### Budgets
- How much budget is remaining?

Compares active current-period budgets with current-period EXPENSE transactions.

### Savings / cash flow
- How much can I save this month?
- What is my savings this month?

Returns income + refunds - expenses for the selected period. This is a ledger-derived cash-flow figure, not a prediction.

### Net worth
- What is my net worth?
- Show my wealth

Uses the existing net-worth calculation.

### Financial summary
General finance/overview questions return current-month income, spending, refunds, net cash flow and current net worth.

## Period handling

Supported periods:
- this month
- last month
- today
- yesterday
- named months such as September or Sep
- named month with year such as September 2026

If no period is supplied for spending/savings, the current month is used.

## Follow-up context

The response returns the selected period and category where applicable.

A client can send that context back with a follow-up such as "What about petrol?" while retaining the selected period.

The conversational layer remains stateless on the server. Clients can persist the returned context as part of their conversation state.

## Accounting boundaries

The endpoint is read-only. It does not create or modify transactions, debts, cards, budgets, goals or investments.

## Security

The route maps to the existing transactions.read permission and requires an authenticated user. Queries filter financial records by the authenticated user ID.

## Intent model

Current intents:
- SPENDING
- MONEY_OWED_TO_ME
- MONEY_I_OWE
- CREDIT_CARD_STATUS
- NET_WORTH
- BUDGET_STATUS
- SAVINGS
- FINANCIAL_SUMMARY

The parser is deterministic in 3F-D. It does not call an external LLM or add an AI dependency to the financial ledger.
