# Audit findings and fixes

## Found issues
- Monolithic route handling in app.py.
- Hard-coded secrets and bootstrap credentials.
- Missing automated test coverage.
- Inconsistent error handling in decode and batch services.
- No CI workflow for automated validation.

## Implemented fixes
- Added a central config module.
- Protected debug endpoints behind admin role checks.
- Added regression tests for auth, run-store, and AIDC batch heuristics.
- Added a GitHub Actions workflow for CI.
- Improved decode service error handling.

## Recommended next steps
- Extract blueprints for auth/admin/debug APIs.
- Move JSON persistence behind a repository layer.
- Introduce stronger password hashing.
- Expand test coverage to registry and decode flows.
