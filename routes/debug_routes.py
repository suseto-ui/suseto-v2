# routes/debug_routes.py
# Debug API endpoints — admin only.
# Blueprint stub: endpoints will be migrated from app.py incrementally.

from flask import Blueprint, jsonify
from routes.helpers import require_role, body

debug_bp = Blueprint("debug", __name__, url_prefix="/api/v1/debug")


@debug_bp.post("/ping")
def debug_ping():
    return jsonify({"ok": True, "received": body()})


@debug_bp.get("/routes")
def debug_routes():
    from flask import current_app
    return jsonify({"routes": sorted([str(r.rule) for r in current_app.url_map.iter_rules()])})


# /api/v1/debug/env and /api/v1/debug/install_pip remain in app.py for now.
# Migrate here once app.py refactor is complete.
