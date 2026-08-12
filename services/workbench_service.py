# services/workbench_service.py
# Hlavni sluzba pro Workbench

from typing import Dict, Any, List
import uuid

class WorkbenchService:
    def __init__(self):
        self._jobs = {}

    def list_jobs(self):
        return list(self._jobs.values())

    def create_job(self, job_type, payload):
        job_id = str(uuid.uuid4())[:8]
        job = {"id": job_id, "type": job_type, "payload": payload, "status": "created"}
        self._jobs[job_id] = job
        return job

    def get_job(self, job_id):
        return self._jobs.get(job_id, {})

    def cancel_job(self, job_id):
        if job_id in self._jobs:
            self._jobs[job_id]["status"] = "cancelled"
            return True
        return False

workbench_service = WorkbenchService()
