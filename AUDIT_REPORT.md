# Audit report – Suseto v2

## 1. Architecture assessment
- The application is a Flask-based single-file entry point with many service modules and template pages.
- The main structure is understandable for a prototype, but route handling and business logic are tightly coupled in app.py.
- The repository would benefit from a clearer separation between HTTP layer, domain services, and persistence helpers.

## 2. Technical debt
- Hard-coded secrets and default credentials are present in the app and auth service layers.
- The app mixes UI rendering, API handlers, and service orchestration in one file.
- There is no automated regression test suite yet.
- Some modules rely on implicit filesystem state and mutable JSON files in the data directory.

## 3. Security findings
- The Flask secret key and initial admin password are effectively hard-coded and should be configurable through environment variables.
- Authentication uses SHA-256 with a salt, which is acceptable for a prototype but should be re-evaluated for production-grade security.
- The application currently exposes a debug endpoint that can be used to inspect environment data and install packages; access should be limited in production.

## 4. Performance observations
- The current implementation is lightweight and suitable for local use.
- JSON file persistence can become a bottleneck as data volume grows; a proper database layer would be beneficial.
- Repeated reads from JSON files across requests could be optimized by introducing caching or a repository abstraction.

## 5. Testing status
- No automated tests were present initially.
- Added regression tests for authentication and run-store behavior to establish a baseline.

## Recommended changes
1. Move configuration values to environment-driven settings and centralize them in a single config module.
2. Split the monolithic app.py route definitions into smaller blueprints or modules.
3. Introduce a lightweight repository layer for JSON persistence.
4. Restrict or remove debug endpoints in production environments.
5. Expand test coverage for auth, registry, and decode flows.

## Priority order
- P1: eliminate hard-coded secrets and default credentials.
- P2: add automated tests for regression-safe behavior.
- P3: extract route and persistence concerns into dedicated modules.
