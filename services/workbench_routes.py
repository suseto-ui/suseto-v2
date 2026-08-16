# services/workbench_routes.py
# Registers the /workbench page and /api/v1/workbench/* REST endpoints.
from flask import Blueprint, request, jsonify, render_template
from services.workbench_service import (
    ingest_identifier,
    run_analysis_pipeline,
    run_reverse_engineering,
    run_test_harness,
)

wb = Blueprint("workbench", __name__)


def _body():
    return request.get_json(silent=True) or {}


@wb.route("/workbench")
def workbench_page():
    return render_template("pages/workbench.html")


@wb.post("/api/v1/workbench/ingest")
def api_ingest():
    d = _body()
    raw = d.get("raw", "").strip()
    if not raw:
        return jsonify({"ok": False, "error": "Chybí pole 'raw'."}), 400
    result = ingest_identifier(raw, d.get("meta", {}))
    return jsonify({"ok": True, "identifier": result})


@wb.post("/api/v1/workbench/analyze")
def api_analyze():
    d = _body()
    identifier = d.get("identifier")
    if not identifier:
        return jsonify({"ok": False, "error": "Chybí pole 'identifier'."}), 400
    result = run_analysis_pipeline(identifier)
    return jsonify({"ok": True, **result})


@wb.post("/api/v1/workbench/reverse")
def api_reverse():
    d = _body()
    raw = d.get("raw", "").strip()
    if not raw:
        return jsonify({"ok": False, "error": "Chybí pole 'raw'."}), 400
    result = run_reverse_engineering(raw)
    return jsonify({"ok": True, **result})


@wb.post("/api/v1/workbench/test-run")
def api_test_run():
    d = _body()
    target = d.get("target", "").strip()
    if not target:
        return jsonify({"ok": False, "error": "Chybí pole 'target'."}), 400
    report = run_test_harness(target, d.get("profile", {}))
    return jsonify({"ok": True, **report})


def register_workbench(app):
    """Call this from app.py to mount the workbench blueprint."""
    app.register_blueprint(wb)
