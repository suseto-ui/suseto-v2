# routes/admin_routes.py
# Blueprint pro /api/v1/admin/*

from flask import Blueprint, jsonify, session, Response
from routes.helpers import require_role, body
from services.auth_service import (
    list_users,
    create_user,
    set_role,
    toggle_active,
    delete_user,
    reset_password,
)
from services.audit_service import write as audit_write, list_entries as audit_list
import csv
import io

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


@admin_bp.get("/users")
def admin_users():
    if not require_role("admin"):
        return jsonify({"error": "Vyžadována role admin."}), 403
    return jsonify({"users": list_users()})


@admin_bp.post("/users")
def admin_user_create():
    if not require_role("admin"):
        return jsonify({"error": "Vyžadována role admin."}), 403
    try:
        res = create_user(
            body().get("username"), body().get("password"), body().get("role", "viewer")
        )
        audit_write("create_user", session.get("username"), res["username"])
        return jsonify(res), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@admin_bp.post("/users/role")
def admin_user_role():
    if not require_role("admin"):
        return jsonify({"error": "Vyžadována role admin."}), 403
    try:
        res = set_role(body().get("username"), body().get("role", "viewer"))
        audit_write(
            "set_role",
            session.get("username"),
            f"{body().get('username')}->{body().get('role')}",
        )
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@admin_bp.post("/users/toggle")
def admin_user_toggle():
    if not require_role("admin"):
        return jsonify({"error": "Vyžadována role admin."}), 403
    try:
        res = toggle_active(body().get("username"))
        audit_write("toggle_active", session.get("username"), body().get("username"))
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@admin_bp.post("/users/delete")
def admin_user_delete():
    if not require_role("admin"):
        return jsonify({"error": "Vyžadována role admin."}), 403
    try:
        res = delete_user(body().get("username"))
        audit_write("delete_user", session.get("username"), body().get("username"))
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@admin_bp.post("/users/reset-password")
def admin_user_reset_password():
    if not require_role("admin"):
        return jsonify({"error": "Vyžadována role admin."}), 403
    try:
        res = reset_password(body().get("username"), body().get("new_password", ""))
        audit_write("reset_password", session.get("username"), body().get("username"))
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@admin_bp.get("/audit")
def admin_audit():
    if not require_role("admin"):
        return jsonify({"error": "Vyžadována role admin."}), 403
    return jsonify({"entries": audit_list()})


@admin_bp.get("/audit/export")
def api_audit_export():
    if not require_role("admin"):
        return jsonify({"error": "Vyžadována role admin."}), 403
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["at", "action", "actor", "detail"])
    for r in audit_list():
        cw.writerow([r.get("at"), r.get("action"), r.get("actor"), r.get("detail")])
    return Response(
        si.getvalue().encode("utf-8-sig"),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit.csv"},
    )
