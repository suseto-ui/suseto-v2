# GitHub implementation pack

## Epic: Stabilize and refactor the app without losing behavior

### Feature 1: Environment config
- Story: add `services/config.py`.
- Story: load config in `app.py` via `FLASK_CONFIG`.
- Test: app boots in development/staging/production/testing.

### Feature 2: Core blueprint
- Story: move remaining core routes into `routes/core_routes.py`.
- Test: health, transform, analyze, state, runs still respond the same.

### Feature 3: Domain blueprints
- Story: keep auth/admin/registry/inventory/decode/aidc/timeline in blueprints.
- Test: all endpoints preserve URL, request body, and response shape.

### Feature 4: CI/CD and notifications
- Story: GitHub Actions workflow with path filters and cache.
- Story: Slack notification job on final workflow result.
- Test: docs-only changes skip heavy jobs; code changes run the proper jobs.

### Feature 5: Regression safety
- Story: smoke import for `app.py`.
- Story: endpoint regression checks.
- Test: no functional drift after refactor.

## Implementation rule
- One atomic bulk commit for all categorized code.
- Keep user experience unchanged.
- Keep API contracts unchanged unless explicitly planned.
