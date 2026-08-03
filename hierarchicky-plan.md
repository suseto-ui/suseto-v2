# Hierarchický plán implementace

## Epic 1: Stabilizace prostředí a konfigurace

### Feature 1.1: Environment config
- Story: `services/config.py` pro development, staging, production, testing.
- Story: `app.py` načítá config přes `FLASK_CONFIG`.
- Test: app startuje ve všech režimech bez změny chování.

### Feature 1.2: CI/CD baseline
- Story: GitHub Actions s path filtry a cache.
- Story: Smoke import a testy pro Python 3.12/3.13.
- Story: Slack notifikace finálního stavu pipeline.

## Epic 2: Modulární Flask architektura

### Feature 2.1: Core routes
- Story: `routes/core_routes.py`.
- Test: health, transform, analyze, state, runs.

### Feature 2.2: Auth & admin
- Story: `routes/auth_routes.py`.
- Story: `routes/admin_routes.py`.
- Test: login/logout, role checks, audit export.

### Feature 2.3: Registry & inventory
- Story: `routes/registry_routes.py`.
- Story: `routes/inventory_routes.py`.
- Test: registry CRUD, inventory sessions, insight, gs1.

### Feature 2.4: AIDC, decode, timeline
- Story: `routes/aidc_routes.py`.
- Story: `routes/decode_routes.py`.
- Story: `routes/timeline_routes.py`.
- Test: QR/barcode, decode, locations, dashboard, backup.

### Feature 2.5: Shared helpers
- Story: `routes/helpers.py`.
- Story: `routes/__init__.py`.
- Test: helper behavior remains identical.

## Epic 3: Regression safety

### Feature 3.1: Contract preservation
- Story: keep URLs unchanged.
- Story: keep payload keys unchanged.
- Story: keep error messages unchanged where used by UI.

### Feature 3.2: Validation
- Story: endpoint smoke tests.
- Story: import test for `app.py`.
- Story: CI gate on modified paths only.

## Epic 4: Delivery

### Feature 4.1: Bulk commit
- Story: one atomic git commit for all categorized code.
- Story: one PR / one workflow run.

### Feature 4.2: Observability
- Story: Slack notification on workflow result.
- Story: staging deploy step placeholder.
