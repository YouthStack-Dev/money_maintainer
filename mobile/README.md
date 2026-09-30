# Money Maintainer Mobile

Android + iOS client for Money Maintainer.

## Architecture

- `mobile/` contains all mobile application code.
- `backend/` remains the source of truth for financial rules and data.
- Mobile screens consume the existing REST API.
- Financial calculations are not duplicated in the mobile client.

## Phase Mobile 1

Initial client foundation:
- authentication/session boundary
- API client boundary
- application navigation
- Home
- Quick Add
- Activity
- reusable loading/error/empty states

The exact native/cross-platform runtime can be introduced without changing the backend contract.
