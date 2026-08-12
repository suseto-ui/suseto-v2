# services/workbench_service.py
# Hlavní služba pro Workbench - placeholder kostra

from typing import Dict, Any, List
import uuid

class WorkbenchService:
    """Hlavní služba pro správu úloh ve Workbenchi."""

    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def list_jobs(self) -> List[Dict[str, Any]]:
        """Vrátí seznam všech úloh."""
        return list(self._jobs.values())

    def create_job(self, job_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Vytvoří novou úlohu."""
        job_id = str(uuid.uuid4())[:8]
        job = {
            "id": job_id,
            "type": job_type,
            "payload": payload,
            "status": "created"
        }
        self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Vrátí detail úlohy."""
        return self._jobs.get(job_id, {})

    def cancel_job(self, job_id: str) -> bool:
        """Zruší úlohu."""
        if job_id in self._jobs:
            self._jobs[job_id]["status"] = "cancelled"
            return True
        return False

# Globální instance, kterou importuje workbench_routes.py
workbench_service = WorkbenchService()
