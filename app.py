from flask import Flask, jsonify, render_template
from services.config import CONFIG

# create app
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = CONFIG["SECRET_KEY"]
application = app

# centralized helpers
from routes.helpers import current_user, require_role, body  # noqa: E402

# register blueprints (API implementations live in routes/*.py)
from routes.auth_routes import auth_bp  # noqa: E402
from routes.aidc_routes import aidc_bp  # noqa: E402
from routes.admin_routes import admin_bp  # noqa: E402
from routes.registry_routes import registry_bp  # noqa: E402
from routes.timeline_routes import timeline_bp  # noqa: E402
from routes.debug_routes import debug_bp  # noqa: E402

app.register_blueprint(auth_bp)
app.register_blueprint(aidc_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(registry_bp)
app.register_blueprint(timeline_bp)
app.register_blueprint(debug_bp)

# register workbench blueprint / endpoints (service-style register)
from services.workbench_routes import register_workbench  # noqa: E402
register_workbench(app)


# UI page routes (keep these in app.py)
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


if __name__ == "__main__":
    app.run(debug=True)
