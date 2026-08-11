# services/run_store.py
# Storage pro "runy" – z\u00e1znamy o spu\u0161t\u011bn\u00edch \u00faloh (workbench, AIDC batchy, atd.).

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class RunStore:
    """Jednoduch\u00fd storage pro z\u00e1znamy o spu\u0161t\u011bn\u00edch (runy).

    Ukl\u00e1d\u00e1 data do pam\u011bti (dict) – vhodn\u00e9 pro v\u00fdvoj a rychl\u00e9 lad\u011bn\u00ed.
    V produkci by m\u011blo b\u00fdt napojeno na DB / extern\u00ed storage.
    """

    def __init__(self):
        self._runs: Dict[str, Dict[str, Any]] = {}

    def create_run(
        self,
        label: str,
        run_type: str = "generic",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Vytvoř\u00ed nov\u00fd run z\u00e1znam.

        Vrac\u00ed dict s informacemi o runu (v\u010detn\u011b vygenerovan\u00e9ho run_id).
        """
        run_id = str(uuid.uuid4())[:8]
        entry = {
            "run_id": run_id,
            "label": label,
            "run_type": run_type,
            "status": "created",
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
        }
        self._runs[run_id] = entry
        return entry

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Z\u00edsk\u00e1 run podle run_id."""
        return self._runs.get(run_id)

    def update_status(
        self,
        run_id: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Aktualizuje status runu.

        status: nap\u0159. "running", "completed", "failed", "cancelled".
        """
        if run_id not in self._runs:
            return None

        entry = self._runs[run_id]
        entry["status"] = status
        if details:
            entry["metadata"].update(details)
        entry["updated_at"] = datetime.utcnow().isoformat()

        if status == "running" and not entry["started_at"]:
            entry["started_at"] = datetime.utcnow().isoformat()
        if status in ("completed", "failed", "cancelled") and not entry["completed_at"]:
            entry["completed_at"] = datetime.utcnow().isoformat()

        return entry

    def list_runs(self, limit: int = 50, run_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Vr\u00e1t\u00ed seznam run\u016f (posledn\u00edch `limit`).

        run_type: voliteln\u00fd filtr podle typu runu.
        """
        runs = list(self._runs.values())
        if run_type:
            runs = [r for r in runs if r["run_type"] == run_type]
        # Seřadit podle created_at od nejnovějšího
        runs.sort(key=lambda r: r["created_at"], reverse=True)
        return runs[:limit]

    def delete_run(self, run_id: str) -> bool:
        """Sma\u017ee run podle run_id.

        Vrac\u00ed True, pokud byl run smaz\u00e1n, False pokud neexistoval.
        """
        if run_id in self._runs:
            del self._runs[run_id]
            return True
        return False

    def clear_runs(self) -> int:
        """Vyma\u017ee v\u0161echny runy.

        Vrac\u00ed po\u010det smazan\u00fdch polo\u017eek.
        """
        count = len(self._runs)
        self._runs.clear()
        return count

    def count_runs(self) -> int:
        """Vr\u00e1t\u00ed aktu\u00e1ln\u00ed po\u010det run\u016f."""
        return len(self._runs)


# Glob\u00e1ln\u00ed instance pro snadn\u00e9 pou\u017eit\u00ed
run_store = RunStore()
