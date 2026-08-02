"""
workbench_routes.py — Data & Identifier Analysis Workbench API endpoints
Importuj a zaregistruj v app.py:

  from services.workbench_routes import register_workbench
  register_workbench(app)
"""
from flask import jsonify, request
from services.workbench_service import (
    ingest_identifier,
    run_analysis_pipeline,
    run_reverse_engineering,
    run_test_harness,
)


def register_workbench(app):
    @app.route("/workbench")
    def workbench_page():
        from flask import render_template
        return render_template("pages/workbench.html")

    @app.post("/api/v1/workbench/ingest")
    def wb_ingest():
        data = request.get_json(force=True, silent=True) or {}
        raw = data.get("raw", "").strip()
        if not raw:
            return jsonify({"ok": False, "error": "Missing raw"}), 400
        identifier = ingest_identifier(raw, data.get("meta", {}))
        return jsonify({"ok": True, "identifier": identifier.to_dict()})

    @app.post("/api/v1/workbench/analyze")
    def wb_analyze():
        data = request.get_json(force=True, silent=True) or {}
        identifier = data.get("identifier") or {}
        if not identifier:
            return jsonify({"ok": False, "error": "Missing identifier"}), 400
        result = run_analysis_pipeline(identifier)
        return jsonify({"ok": True, "analysis": result})

    @app.post("/api/v1/workbench/reverse")
    def wb_reverse():
        data = request.get_json(force=True, silent=True) or {}
        raw = data.get("raw", "").strip()
        if not raw:
            return jsonify({"ok": False, "error": "Missing raw"}), 400
        result = run_reverse_engineering(raw)
        return jsonify({"ok": True, "reverse": result})

    @app.post("/api/v1/workbench/test-run")
    def wb_test_run():
        data = request.get_json(force=True, silent=True) or {}
        target = data.get("target", "").strip()
        if not target:
            return jsonify({"ok": False, "error": "Missing target"}), 400
        report = run_test_harness(target, data.get("profile", {}))
        return jsonify({"ok": True, "report": report})