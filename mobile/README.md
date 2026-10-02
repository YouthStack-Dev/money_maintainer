# Money Maintainer Mobile

Flutter mobile application for Money Maintainer.

## Scope

This folder is the mobile application only. Backend and existing web code remain outside it.

## Architecture

- `lib/app/` — application bootstrap and routing
- `lib/core/` — configuration, constants, errors, theme, utilities
- `lib/features/` — feature modules
- `lib/shared/` — reusable UI and common components
- `test/` — unit and widget tests

## Environments

The app will support separate development, staging/test, and production API configuration. No production endpoint is hard-coded into the UI.

## Platforms

Android and iOS are first-class targets. Native platform scaffolding will be generated and configured as part of the foundation phase.

## Current status

Step 1 foundation only. No authentication, dashboard, transaction, or business feature has been implemented yet.
