# Hromadný commit — návrh obsahu

## Součásti commitů
- `services/config.py` — config podle prostředí.
- `routes/core_routes.py` — core API blok.
- `routes/auth_routes.py` — auth blueprint.
- `routes/admin_routes.py` — admin blueprint.
- `routes/registry_routes.py` — registry blueprint.
- `routes/inventory_routes.py` — inventory + insight + gs1.
- `routes/decode_routes.py` — decode blueprint.
- `routes/aidc_routes.py` — AIDC blueprint.
- `routes/timeline_routes.py` — timeline + locations + dashboard + backup.
- `routes/debug_routes.py` — debug blueprint.
- `routes/helpers.py` — společné helpery.
- `routes/__init__.py` — package marker.
- `app.py` — registrace všech blueprintů a vyčištění duplikátů.
- `.github/workflows/ci.yml` — CI with path filters, smoke tests, Slack.

## Cíl
Vše dostat do jednoho atomického commitu, aby se nespouštělo několik po sobě jdoucích workflow běhů a aby se snadno rollbackovalo.
