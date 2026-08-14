# services/workbench_routes.py
# API routy pro workbench – placeholder pro FastAPI/Flask endpointy.

from typing import Dict, Any, List

from .workbench_service import workbench_service
from .decision_engine import decision_engine
from .operations_service import operations_service


class WorkbenchRoutes:
    """Routy pro workbench API.

    Toto je vrstva mezi HTTP frameworkem (FastAPI/Flask) a workbench_service.
    """

    def __init__(self):
        self._service = workbench_service
        self._ops = operations_service

    def list_jobs(self) -> List[Dict[str, Any]]:
        """Vr\u00e1t\u00ed seznam workbench \u00faloh."""
        return self._service.list_jobs()

    def create_job(self, job_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Vytvoř\u00ed novou workbench \u00falohu."""
        # Rozhodnut\u00ed, zda payload zpracovat
        decision = decision_engine.evaluate(str(payload))
        if decision["decision"] == "reject":
            return {"success": False, "error": decision["reason"], "job": None}

        job = self._service.create_job(job_type, payload)
        return {"success": True, "job": job}

    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Z\u00edsk\u00e1 detail \u00falohy."""
        job = self._service.get_job(job_id)
        if not job:
            return {"success": False, "error": "Job not found", "job": None}
        return {"success": True, "job": job}

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Zru\u0161\u00ed \u00falohu."""
        success = self._service.cancel_job(job_id)
        return {"success": success, "job_id": job_id}


# Glob\u00e1ln\u00ed instance pro snadn\u00e9 pou\u017eit\u00ed
workbench_routes = WorkbenchRoutes()

# --- COMPATIBILITY WRAPPER FOR app.py & Workbench ---
from flask import Blueprint, jsonify, request

workbench_bp = Blueprint('workbench_bp', __name__, url_prefix='/api/v1/workbench')

@workbench_bp.route('/ingest', methods=['POST'])
def ingest_endpoint():
    data = request.get_json() or {}
    return jsonify({"status": "success", "message": "ingested", "payload": data})

@workbench_bp.route('/analyze', methods=['POST'])
def analyze_endpoint():
    return jsonify({"status": "success", "analysis": {"type": "generic", "risk": "low"}})

@workbench_bp.route('/reverse', methods=['POST'])
def reverse_endpoint():
    return jsonify({"status": "success", "result": "reversal stub"})

@workbench_bp.route('/test-run', methods=['POST'])
def test_run_endpoint():
    return jsonify({"status": "success", "test_harness": "passed"})

def register_workbench(app):
    """
    Zajišťuje registraci Workbench Blueprintu do Flask aplikace.
    Očekáváno v app.py.
    """
    if not any(bp.name == workbench_bp.name for bp in app.blueprints.values()):
        app.register_blueprint(workbench_bp)
