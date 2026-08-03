# routes/helpers.py
# Shared helpers used across all route modules.
# Import in route blueprints: from routes.helpers import current_user, require_role, body

from flask import request, session


def current_user():
    """Return the logged-in user dict or None."""
    if session.get("username"):
        return {"username": session.get("username"), "role": session.get("role")}
    return None


def require_role(*roles):
    """Return True if the current user has one of the given roles."""
    u = current_user()
    return u is not None and u.get("role") in roles


def body():
    """Parse JSON request body, return empty dict on failure."""
    return request.get_json(silent=True) or {}
