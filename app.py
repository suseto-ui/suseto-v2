import os
from flask import Flask, jsonify, render_template, request, session, Response
from routes.helpers import current_user, require_role, body

# Registrace Blueprintů
from routes.auth_routes import auth_bp
from routes.aidc_routes import aidc_bp
from routes.admin_routes import admin_bp
from routes.registry_routes import registry_bp
from routes.timeline_routes import timeline_bp
from routes.debug_routes import debug_bp
from routes.core_routes import core_bp

from services.config import CONFIG
from services.database import db

from services.audit_service import write as audit_write
from services.auth_service import verify

# Vytvoření aplikace
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = CONFIG["SECRET_KEY"]

# Konfigurace Flask-SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = CONFIG.get("DATABASE_URI", "sqlite:///suseto.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
application = app

# Registrace Blueprintů
app.register_blueprint(auth_bp)
app.register_blueprint(aidc_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(registry_bp)
app.register_blueprint(timeline_bp)
app.register_blueprint(debug_bp)
app.register_blueprint(core_bp)

# Zaregistrování Workbench přes specifickou funkci
from services.workbench_routes import register_workbench
register_workbench(app)


# Globální Error Handlery (aby na uživatele nepadaly syrové tracebacky)
@app.errorhandler(404)
def page_not_found(e):
    return render_template('pages/rozcestnik.html', error_message="Stránka nenalezena (404)."), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('pages/rozcestnik.html', error_message="Interní chyba serveru (500)."), 500


# -------------------------------------------------------------
# FRONTEND UI STRÁNKY
# -------------------------------------------------------------

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


# -------------------------------------------------------------
# HLAVNÍ GLOBÁLNÍ API (které zůstaly v app.py)
# -------------------------------------------------------------

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

# Vytvoření DB tabulek, pokud neexistují
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)