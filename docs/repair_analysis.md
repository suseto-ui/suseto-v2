# Repair analysis

## Focus: app.py and imports

### Status
- Repository is already modularized into route modules.
- The primary remaining risk is import/registration mismatch between `app.py` and the modules under `routes/`.

### What to verify first
1. `app.py` should only create the Flask app and register blueprints.
2. Each module in `routes/` must export a blueprint object with a stable name.
3. Route modules must not import `app` directly from `app.py`.
4. Shared utilities should live in `routes/helpers.py` or `services/`.

### Likely failure classes
- Missing blueprint registration in `app.py`.
- Circular imports caused by route modules importing `app`.
- Name mismatch between imported blueprint symbols and exported symbols in route files.
- Missing or renamed service functions referenced by route modules.

### Recommended order
1. Validate `app.py` imports.
2. Validate blueprint exports in `routes/*.py`.
3. Validate shared helper imports.
4. Run tests after import cleanup.
