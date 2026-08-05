from flask import request, session


def current_user():
    if session.get("username"):
        return {"username": session.get("username"), "role": session.get("role")}
    return None


def require_role(*roles):
    user = current_user()
    return bool(user and user.get("role") in roles)


def body():
    return request.get_json(silent=True) or {}
