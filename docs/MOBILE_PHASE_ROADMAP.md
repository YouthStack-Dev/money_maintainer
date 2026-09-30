# Mobile App Roadmap

## Phase Mobile 1 — Foundation

Status: In progress

Repository location: `mobile/`

### First slice
1. App shell and navigation
2. Authentication/session integration
3. API client
4. Home
5. Quick Add
6. Activity
7. Loading/error/empty states

### Following slices
- Money: debts, credit cards, reimbursements
- Planning: budgets, goals, recurring transactions
- Ask: conversational finance
- Corrections
- Settings/accounts/categories
- Notifications and offline-friendly UX

## Architecture rule

The mobile app is a client of the FastAPI backend. It must not recreate ledger, debt, credit-card, net-worth or budget accounting rules locally.
