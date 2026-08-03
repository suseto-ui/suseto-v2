from services.error_logger import setup_logging
import os
import sys

paths_to_add = [
    "/home/Suseto/.local/lib/python3.13/site-packages",
    "/home/suseto/.local/lib/python3.13/site-packages",
    "/usr/local/lib/python3.13/site-packages"
]
for p in paths_to_add:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

from flask import Flask, jsonify, render_template, request
from services.config import CONFIG
from services.registry_store import items
from services.workbench_routes import register_workbench

from routes.helpers import require_role, body
from routes.debug_routes import debug_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.registry_routes import registry_bp
from routes.inventory_routes import inventory_bp
from routes.decode_routes import decode_bp
from routes.aidc_routes import aidc_bp
from routes.timeline_routes import timeline_bp
from routes.core_routes import core_bp

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = CONFIG["SECRET_KEY"]
application = app

setup_logging(app)
register_workbench(app)

for bp in (debug_bp, auth_bp, admin_bp, registry_bp, inventory_bp, decode_bp, aidc_bp, timeline_bp, core_bp):
    app.register_blueprint(bp)

# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------
@app.route("/")
def home(): return render_template("pages/rozcestnik.html")
@app.route("/navigator")
def navigator(): return render_template("pages/navigator.html")
@app.route("/generator")
def generator(): return render_template("pages/generator.html")
@app.route("/legacy-lab")
def legacy_lab(): return render_template("pages/legacy_lab.html")
@app.route("/state-lab")
def state_lab(): return render_template("pages/state_lab.html")
@app.route("/aidc-studio")
def aidc_studio(): return render_template("pages/aidc_studio.html")
@app.route("/login")
def login_page(): return render_template("pages/login.html", admin_username=CONFIG["ADMIN_USERNAME"], admin_password=CONFIG["DEFAULT_ADMIN_PASSWORD"])
@app.route("/admin")
def admin_page(): return render_template("pages/admin.html")
@app.route("/profile")
def profile_page(): return render_template("pages/profile.html")
@app.route("/decode-lab")
def decode_lab(): return render_template("pages/decode_lab.html")
@app.route("/locations")
def locations_page(): return render_template("pages/locations.html")
@app.route("/status")
def status_page(): return render_template("pages/status.html")
@app.route("/expected-audit")
def expected_audit_page(): return render_template("pages/expected_audit.html")
@app.route("/mobile")
def mobile_page(): return render_template("pages/mobile.html")
@app.route("/debug")
def debug_page(): return render_template("pages/debug.html")
@app.route("/edu")
def edu_page(): return render_template("pages/edu.html")
@app.route("/inventory")
def inventory(): return render_template("pages/inventory.html")
@app.route("/insight-lab")
def insight_lab(): return render_template("pages/insight_lab.html")
@app.route("/label-designer")
def label_designer(): return render_template("pages/label_designer.html")
@app.route("/backup-center")
def backup_center(): return render_template("pages/backup_center.html")
@app.route("/transform-lab")
def transform_lab(): return render_template("pages/transform_lab.html")
@app.route("/dashboard")
def dashboard(): return render_template("pages/dashboard.html")
@app.route("/registry")
def registry(): return render_template("pages/registry.html")
@app.route("/label-profiles")
def label_profiles(): return render_template("pages/label_profiles.html")
@app.route("/aidc-batch")
def aidc_batch(): return render_template("pages/aidc_batch.html")
@app.route("/scanner-lab")
def scanner_lab(): return render_template("pages/scanner_lab.html")
@app.route("/auth-lab")
def auth_lab(): return render_template("pages/auth_lab.html")
@app.route("/runs")
def runs(): return render_template("pages/runs.html")
@app.route("/health")
def health(): return jsonify({"status": "ok", "modules": ["navigator","generator","state_lab","auth_lab","run_history","aidc_studio","aidc_batch","registry","label_profiles","scanner_lab","transform_lab","dashboard","inventory","insight_lab","label_designer","backup_center"], "mode": "sandbox-only"})

# ---------------------------------------------------------------------------
# Legacy stubs (TODO: move to routes/debug_routes.py in next sprint)
# ---------------------------------------------------------------------------
@app.post("/api/v1/debug/install_pip")
def api_debug_install_pip():
    if not require_role("admin"):
        return jsonify({"error": "Vy\u017eadov\u00e1na role admin."}), 403
    import subprocess
    try:
        result = subprocess.run(
            ["python3", "-m", "pip", "install", "--user", "qrcode[pil]", "python-barcode[images]", "Pillow"],
            capture_output=True, text=True
        )
        output = result.stdout + "\n" + result.stderr
        import site
        from pathlib import Path
        user_site = Path.home() / '.local' / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
        if user_site.exists():
            site.addsitedir(str(user_site))
        return jsonify({"ok": True, "log": output})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@app.get("/api/v1/debug/env")
def api_debug_env():
    import time
    from pathlib import Path
    import flask
    if not require_role("admin"):
        return jsonify({"error": "Vy\u017eadov\u00e1na role admin."}), 403
    res = {"python": sys.version.split(" ")[0], "flask": flask.__version__}
    data_dir = Path(app.root_path) / 'data'
    try:
        data_dir.mkdir(exist_ok=True)
        test_file = data_dir / '.write_test'
        test_file.write_text('test')
        test_file.unlink()
        res['data_write'] = "OK"
    except Exception as e:
        res['data_write'] = f"FAIL: {str(e)}"
    files_to_check = ['app.py', 'static/js/decode_lab.js', 'static/js/menu-delay.js', 'static/js/debug.js', 'templates/pages/decode_lab.html']
    res['files'] = {}
    for f in files_to_check:
        p = Path(app.root_path) / f
        res['files'][f] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(p.stat().st_mtime)) if p.exists() else "MISSING"
    deps = {}
    for pkg, attr in [("qrcode", "__version__"), ("barcode", "version"), ("PIL", "__version__")]:
        try:
            m = __import__(pkg)
            deps[pkg] = getattr(m, attr, getattr(m, '__version__', 'OK'))
        except Exception as e:
            deps[pkg] = f"ERROR: {str(e)}"
    res['deps'] = deps
    res['sys_path'] = sys.path
    return jsonify(res)

@app.route("/label-print/<item_id>")
def label_print(item_id):
    found = next((x for x in items() if x["id"] == item_id), None)
    if not found:
        return "Not found", 404
    return render_template("pages/label_print.html", item=found)
