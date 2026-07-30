# PR review notes

## Summary
- Introduces a central config module for secret and admin defaults.
- Adds an audit report documenting architecture, debt, security, performance, and testing findings.
- Adds initial regression tests for auth and run-store flows.

## Review findings
- The changes are directionally correct and reduce hard-coded configuration.
- The new tests are lightweight and useful, but the suite should be expanded as the app grows.
- The debug endpoint is now admin-protected, which is an improvement.
- The repository would still benefit from further extraction of app.py into blueprints.

## Suggested follow-ups
1. Create dedicated blueprints for auth, admin, and debug APIs.
2. Add tests for registry and decode services.
3. Move persistence to a repository abstraction instead of raw JSON file access.
4. Replace the simple SHA-256 hashing approach with a stronger password hashing algorithm for production.
