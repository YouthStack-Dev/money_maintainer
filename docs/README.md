# Money Maintainer Documentation

This directory documents the backend as implemented on the current development branch.

## Documentation map
- PHASE_ROADMAP.md — Phase 1 through Phase 5 scope and current implementation status.
- API_REFERENCE.md — complete endpoint inventory, grouped by phase/resource, including method, path, permission and behavior.
- DOMAIN_RULES.md — ledger rules, ownership/isolation, lifecycle rules and cross-feature behavior.

## Source of truth
The API documentation is maintained against the FastAPI routers under backend/app/*/router.py.
FastAPI also exposes generated interactive OpenAPI documentation when the application is running: /docs, /openapi.json and /redoc.

## Branch policy
Phase 1 remains stable on main.
All Phase 2 work is developed on phase-2. Phase 3 work should follow the same phase-branch workflow unless the project owner explicitly changes it.

## Current implementation
| Phase | Scope | Status |
|---|---|---|
| Phase 1 | Financial Core | Complete |
| Phase 2 | Financial Control | Complete |
| Phase 3 | Wealth Management | Planned |
| Phase 4 | Intelligence / Automation | Planned |
| Phase 5 | Advanced Platform | Planned |

## Phase 2 milestones
| Milestone | Feature | Status |
|---|---|---|
| 2A | Recurring Transactions | Complete |
| 2B | Debt & Lending | Complete |
| 2C | Credit Card Control | Complete |
| 2D | Financial Goals | Complete |
| 2E | Cash-Flow Planning | Complete |
| 2F | Financial Alerts | Complete |

Documentation describes the current implementation. It does not imply that a feature is externally deployed or that automated tests were executed remotely unless that is separately verified.