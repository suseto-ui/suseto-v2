# routes/registry_routes.py
# Blueprint pro /api/v1/registry/* a /api/v1/label-profiles

from flask import Blueprint, jsonify, request, Response
from routes.helpers import require_role, body
from services.registry_store import profiles, items, add_profile, add_item, set_status, match, export_csv_text, import_csv_text

registry_bp = Blueprint("registry", __name__)


@registry_bp.get("/api/v1/registry")
def registry_list():
    return jsonify({"items": items(request.args.get("q", ""), request.args.get("status", "")), "profiles": profiles()})


@registry_bp.post("/api/v1/registry")
def registry_add():
    try:
        return jsonify(add_item(body())), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@registry_bp.post("/api/v1/registry/<item_id>/status")
def registry_status(item_id):
    try:
        return jsonify(set_status(item_id, body().get("status")))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@registry_bp.get("/api/v1/registry/match")
def registry_match():
    return jsonify({"item": match(request.args.get("payload", ""))})


@registry_bp.get("/api/v1/registry/export")
def registry_export():
    return Response(
        export_csv_text(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=suseto-registry.csv"}
    )


@registry_bp.post("/api/v1/registry/import")
def registry_import():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "Nahraj CSV soubor."}), 400
    try:
        return jsonify(import_csv_text(f.read()))
    except (ValueError, UnicodeDecodeError) as e:
        return jsonify({"error": str(e)}), 400


@registry_bp.get("/api/v1/label-profiles")
def profiles_list():
    return jsonify({"profiles": profiles()})


@registry_bp.post("/api/v1/label-profiles")
def profiles_add():
    try:
        return jsonify(add_profile(body())), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
