# routes/inventory_routes.py
# Blueprint pro /api/v1/inventory/*, /api/v1/insight/*, /api/v1/gs1/*

from flask import Blueprint, jsonify, session
from routes.helpers import current_user, require_role, body
from services.operations_service import session_create, session_add, session_list, profile as payload_profile, diff as payload_diff, patterns as payload_patterns, gs1
from services.audit_service import write as audit_write
from services.timeline_service import add as timeline_add

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.get("/api/v1/inventory/sessions")
def inventory_sessions():
    if not current_user():
        return jsonify({"error": "Přihlas se."}), 401
    return jsonify({"sessions": session_list()})


@inventory_bp.post("/api/v1/inventory/sessions")
def inventory_create():
    if not require_role("admin", "operator"):
        return jsonify({"error": "Vyžadována role operator nebo admin."}), 403
    res = session_create(body().get("name"))
    audit_write("create_session", session.get("username"), res["name"])
    timeline_add(res["id"], "create_session", session.get("username"), res["name"])
    return jsonify(res), 201


@inventory_bp.post("/api/v1/inventory/sessions/<session_id>/scan")
def inventory_scan(session_id):
    if not require_role("admin", "operator"):
        return jsonify({"error": "Vyžadována role operator nebo admin."}), 403
    try:
        res = session_add(session_id, body().get("payload", ""))
        audit_write("scan_to_session", session.get("username"), session_id)
        timeline_add(body().get("payload", ""), "scan", session.get("username"), session_id)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@inventory_bp.post("/api/v1/insight/profile")
def insight_profile():
    return jsonify(payload_profile(body().get("payload", "")))


@inventory_bp.post("/api/v1/insight/diff")
def insight_diff():
    return jsonify(payload_diff(body().get("payloads", [])))


@inventory_bp.post("/api/v1/insight/patterns")
def insight_patterns():
    return jsonify({"patterns": payload_patterns(body().get("payloads", []))})


@inventory_bp.post("/api/v1/gs1/validate")
def gs1_validate():
    return jsonify(gs1(body().get("value", "")))
