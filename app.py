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

from flask import Flask, jsonify, render_template, request, session, Response

from services.config import CONFIG
from services.decision_engine import analyze_payload
from services.generator_engine import profile_bundle
from services.state_machine import build_state_graph, replay_path, get_state_detail
from services.heuristic_engine import build_frontier
from services.auth_lab import simulate
from services.run_store import save_run, list_runs, get_run
from services.registry_store import items
from services.transform_service import analyze as transform_analyze, time_formats
from services.workbench_routes import register_workbench

from routes.helpers import current_user, require_role, body
from routes.debug_routes import debug_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.registry_routes import registry_bp
from routes.inventory_routes import inventory_bp
from routes.decode_routes import decode_bp
from routes.aidc_routes import aidc_bp
from routes.timeline_routes import timeline_bp

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = CONFIG["SECRET_KEY"]
application = app

from services.error_logger import setup_logging
setup_logging(app)
register_workbench(app)

for bp in (debug_bp, auth_bp, admin_bp, registry_bp, inventory_bp, decode_bp, aidc_bp, timeline_bp):
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
def health(): return jsonify({"status":"ok","modules":["navigator","generator","state_lab","auth_lab","run_history","aidc_studio","aidc_batch","registry","label_profiles","scanner_lab","transform_lab","dashboard","inventory","insight_lab","label_designer","backup_center"],"mode":"sandbox-only"})

# ---------------------------------------------------------------------------
# API routes (not yet moved to blueprints)
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
    files_to_check = ['app.py','static/js/decode_lab.js','static/js/menu-delay.js','static/js/debug.js','templates/pages/decode_lab.html']
    res['files'] = {}
    for f in files_to_check:
        p = Path(app.root_path) / f
        if p.exists():
            res['files'][f] = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(p.stat().st_mtime))
        else:
            res['files'][f] = "MISSING"
    deps = {}
    try:
        import qrcode; deps['qrcode'] = getattr(qrcode, '__version__', 'OK')
    except Exception as e:
        deps['qrcode'] = f"ERROR: {str(e)}"
    try:
        import barcode; deps['barcode'] = getattr(barcode, 'version', getattr(barcode, '__version__', 'OK'))
    except Exception as e:
        deps['barcode'] = f"ERROR: {str(e)}"
    try:
        import PIL; deps['Pillow'] = PIL.__version__
    except Exception as e:
        deps['Pillow'] = f"ERROR: {str(e)}"
    res['deps'] = deps
    res['sys_path'] = sys.path
    return jsonify(res)

@app.get("/api/v1/system-status")
def api_system_status():
    from pathlib import Path
    data_dir = Path(app.root_path) / 'data'
    from services.location_service import list_locations
    from services.timeline_service import list_for as timeline_list
    from services.audit_service import list_entries as audit_list
    return jsonify({"user": current_user(), "files": [p.name for p in data_dir.glob('*')] if data_dir.exists() else [], "locations": len(list_locations()), "timeline_entries": len(timeline_list()), "audit_entries": len(audit_list())})

@app.post("/api/v1/expected-audit")
def api_expected_audit():
    rows = body().get("expected", []); scanned = body().get("scanned", [])
    exp = {str(x).strip() for x in rows if str(x).strip()}; sc = {str(x).strip() for x in scanned if str(x).strip()}
    return jsonify({"found": sorted(exp & sc), "missing": sorted(exp - sc), "unexpected": sorted(sc - exp)})

@app.post("/api/v1/transform/analyze")
def transform_api():
    d = body(); return jsonify(transform_analyze(d.get("payload", ""), d.get("key", "")))

@app.get("/api/v1/transform/time")
def transform_time(): return jsonify(time_formats())

@app.route("/label-print/<item_id>")
def label_print(item_id):
    found = next((x for x in items() if x["id"] == item_id), None)
    if not found: return "Not found", 404
    return render_template("pages/label_print.html", item=found)

@app.post("/api/v1/analyze")
def api_analyze():
    d = body(); return jsonify(analyze_payload(d.get("payload") or request.form.get("payload", "")))

@app.post("/api/v1/generate-profile")
def api_generate_profile():
    d = body(); return jsonify(profile_bundle(d.get("seed") or "sample-seed"))

@app.post("/api/v1/state-graph")
def api_state_graph(): return jsonify(build_state_graph(body().get("seed") or "demo"))

@app.post("/api/v1/state-detail")
def api_state_detail(): return jsonify(get_state_detail(body().get("state_id", "root")))

@app.post("/api/v1/replay")
def api_replay(): return jsonify(replay_path(body().get("path") or ["root", "profile", "filter", "validate"]))

@app.post("/api/v1/heuristic-run")
def heuristic_run():
    d = body()
    result = build_frontier(d.get("seed", "demo"), d.get("strategy", "best_first"), d.get("budget", 8), d.get("weights"))
    saved = save_run({"kind": "heuristic", "input": {"seed": d.get("seed", "demo"), "strategy": result["strategy"], "budget": result["budget"], "weights": result["weights"]}, "summary": {"top_score": result["frontier"][0]["score"] if result["frontier"] else 0, "count": len(result["frontier"])}})
    return jsonify({**result, "run": saved})

@app.post("/api/v1/auth-simulate")
def auth_simulate():
    d = body()
    result = simulate(d)
    saved = save_run({"kind": "auth_simulation", "input": d, "summary": {"scenario": result["scenario"], "risk": result["risk"], "sandbox": True}})
    return jsonify({**result, "run": saved})

@app.get("/api/v1/runs")
def api_runs(): return jsonify({"runs": list_runs()})

@app.get("/api/v1/runs/<run_id>")
def api_run(run_id):
    r = get_run(run_id)
    return (jsonify(r), 200) if r else (jsonify({"error": "not_found"}), 404)
