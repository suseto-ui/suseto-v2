from flask import Flask, jsonify, render_template, request, session, Response
import os
import sys
from pathlib import Path

from services.config import CONFIG
from services.decision_engine import analyze_payload
from services.generator_engine import profile_bundle
from services.state_machine import build_state_graph, replay_path, get_state_detail
from services.heuristic_engine import build_frontier
from services.auth_lab import simulate
from services.run_store import save_run, list_runs, get_run
from services.aidc_service import generate_qr, generate_barcode, scan_analysis
from services.aidc_batch import preview_csv, generate_batch
from services.registry_store import profiles, items, add_profile, add_item, set_status, match, export_csv_text, import_csv_text
from services.transform_service import analyze as transform_analyze, time_formats
from services.operations_service import session_create, session_add, session_list, profile as payload_profile, diff as payload_diff, patterns as payload_patterns, gs1, backup, restore
from services.auth_service import list_users, create_user, set_role, toggle_active, verify, delete_user, reset_password, change_password
from services.audit_service import write as audit_write, list_entries as audit_list
from services.decode_service import chain as decode_chain, pattern_library
from services.location_service import list_locations, add_location
from services.timeline_service import add as timeline_add, list_for as timeline_list

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = CONFIG["SECRET_KEY"]
application = app


def current_user():
    if session.get("username"):
        return {"username": session.get("username"), "role": session.get("role")}
    return None


def require_role(*roles):
    user = current_user()
    return user and user.get("role") in roles


def body():
    return request.get_json(silent=True) or {}


@app.route("/")
def home():
    return render_template("pages/rozcestnik.html")


@app.route("/navigator")
def navigator():
    return render_template("pages/navigator.html")


@app.route("/generator")
def generator():
    return render_template("pages/generator.html")


@app.route("/legacy-lab")
def legacy_lab():
    return render_template("pages/legacylab.html")


@app.route("/state-lab")
def state_lab():
    return render_template("pages/statelab.html")


@app.route("/aidc-studio")
def aidc_studio():
    return render_template("pages/aidcstudio.html")


@app.route("/login")
def login_page():
    return render_template(
        "pages/login.html",
        admin_username=CONFIG.get("ADMIN_USERNAME"),
        admin_password=CONFIG.get("DEFAULT_ADMIN_PASSWORD"),
    )


@app.route("/admin")
def admin_page():
    return render_template("pages/admin.html")


@app.route("/profile")
def profile_page():
    return render_template("pages/profile.html")


@app.route("/decode-lab")
def decode_lab():
    return render_template("pages/decodelab.html")


@app.route("/locations")
def locations_page():
    return render_template("pages/locations.html")


@app.route("/status")
def status_page():
    return render_template("pages/status.html")


@app.route("/expected-audit")
def expected_audit_page():
    return render_template("pages/expectedaudit.html")


@app.route("/mobile")
def mobile_page():
    return render_template("pages/mobile.html")


@app.route("/debug")
def debug_page():
    return render_template("pages/debug.html")


@app.route("/edu")
def edu_page():
    return render_template("pages/edu.html")


@app.route("/inventory")
def inventory_page():
    return render_template("pages/inventory.html")


@app.route("/insight-lab")
def insight_lab():
    return render_template("pages/insightlab.html")


@app.route("/label-designer")
def label_designer():
    return render_template("pages/labeldesigner.html")


@app.route("/backup-center")
def backup_center():
    return render_template("pages/backupcenter.html")


@app.route("/transform-lab")
def transform_lab():
    return render_template("pages/transformlab.html")


@app.route("/dashboard")
def dashboard():
    return render_template("pages/dashboard.html")


@app.route("/registry")
def registry():
    return render_template("pages/registry.html")


@app.route("/label-profiles")
def label_profiles():
    return render_template("pages/labelprofiles.html")


@app.route("/aidc-batch")
def aidc_batch():
    return render_template("pages/aidcbatch.html")


@app.route("/scanner-lab")
def scanner_lab():
    return render_template("pages/scannerlab.html")


@app.route("/auth-lab")
def auth_lab():
    return render_template("pages/authlab.html")


@app.route("/runs")
def runs_page():
    return render_template("pages/runs.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "user": current_user()})


@app.get("/api/v1/auth/me")
def auth_me():
    return jsonify({"user": current_user()})


@app.post("/api/v1/auth/login")
def auth_login():
    data = body()
    user = verify(data.get("username"), data.get("password"))
    if not user:
        return jsonify({"error": "Neplatné přihlášení."}), 401
    session["username"] = user["username"]
    session["role"] = user["role"]
    audit_write("login", user["username"], user["role"])
    return jsonify({"user": user})


@app.post("/api/v1/auth/logout")
def auth_logout():
    audit_write("logout", session.get("username", "anonymous"), "")
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/v1/debug/routes")
def api_debug_routes():
    return jsonify({"routes": sorted([str(r.rule) for r in app.url_map.iter_rules()])})


@app.post("/api/v1/debug/ping")
def api_debug_ping():
    return jsonify({"ok": True, "received": body()})


if __name__ == "__main__":
    app.run(debug=True)
