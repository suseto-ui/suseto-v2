# routes/auth_routes.py
# Blueprint pro /api/v1/auth/*

from flask import Blueprint, jsonify, session
from routes.helpers import current_user, body
from services.auth_service import verify, change_password
from services.audit_service import write as audit_write

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.get("/me")
def auth_me():
    return jsonify({"user": current_user()})


@auth_bp.post("/login")
def auth_login():
    u = verify(body().get("username", ""), body().get("password", ""))
    if not u:
        return jsonify({"error": "Neplatné přihlášení."}), 401
    session["username"] = u["username"]
    session["role"] = u["role"]
    audit_write("login", u["username"], u["role"])
    return jsonify({"user": u})


@auth_bp.post("/logout")
def auth_logout():
    audit_write("logout", session.get("username", "anonymous"), "")
    session.clear()
    return jsonify({"ok": True})


@auth_bp.post("/change-password")
def auth_change_password():
    if not current_user():
        return jsonify({"error": "Přihlas se."}), 401
    try:
        res = change_password(
            session.get("username"),
            body().get("old_password", ""),
            body().get("new_password", "")
        )
        audit_write("change_password", session.get("username"), "")
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
