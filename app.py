import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from functools import wraps
from services.config import CONFIG
from services.error_logger import setup_logging
from services.decode_service import chain, pattern_library
from services.locations import load_locations
from services.registry import load_registry
from services.dashboard import dashboard_stats

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")

# Nastaveni loggeru AZ po definici app
setup_logging(app)

# --- Auth ---
def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.cookies.get(CONFIG["SESSION_COOKIE"]):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper

def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.cookies.get(CONFIG["SESSION_COOKIE"]):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper

@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    if data.get("username") == CONFIG["ADMIN_USERNAME"] and data.get("password") == CONFIG["DEFAULT_ADMIN_PASSWORD"]:
        response = jsonify({"ok": True, "user": "admin"})
        response.set_cookie(CONFIG["SESSION_COOKIE"], "admin-session", httponly=True, samesite="lax")
        return response
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/v1/auth/logout", methods=["POST"])
def logout():
    response = jsonify({"ok": True})
    response.delete_cookie(CONFIG["SESSION_COOKIE"])
    return response

@app.route("/api/v1/auth/me", methods=["GET"])
def auth_me():
    session = request.cookies.get(CONFIG["SESSION_COOKIE"])
    user = "admin" if session else None
    return jsonify({"user": user, "ok": True})

# --- Health / Debug ---
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/api/v1/debug/ping", methods=["POST"])
def ping():
    data = request.get_json() or {}
    return jsonify({"ok": True, "received": data})

@app.route("/api/v1/debug/routes", methods=["GET"])
def list_routes():
    routes = [r.rule for r in app.url_map.iter_rules()]
    return jsonify({"routes": sorted(routes)})

# --- Decode ---
@app.route("/api/v1/decode/chain", methods=["POST"])
@require_auth
def decode_chain():
    data = request.get_json() or {}
    payload = data.get("payload", "")
    result = chain(payload)
    return jsonify(result)

@app.route("/api/v1/decode/library", methods=["POST"])
@require_auth
def decode_library():
    data = request.get_json() or {}
    payloads = data.get("payloads", [])
    result = pattern_library(payloads)
    return jsonify(result)

# --- Registry & Locations ---
@app.route("/api/v1/registry", methods=["GET"])
def get_registry():
    return jsonify({"items": load_registry()})

@app.route("/api/v1/locations", methods=["GET"])
@require_auth
def get_locations():
    return jsonify({"locations": load_locations()})

# --- Dashboard ---
@app.route("/api/v1/dashboard/stats", methods=["GET"])
@require_auth
def get_dashboard_stats():
    return jsonify(dashboard_stats())

# --- Static Frontend ---
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path and os.path.isfile(os.path.join("frontend", path)):
        return send_from_directory("frontend", path)
    return send_from_directory("frontend", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
