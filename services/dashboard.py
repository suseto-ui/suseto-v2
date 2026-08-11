# services/dashboard.py
# Služba pro data na dashboardu (přehledy, statistiky).

from typing import Dict, Any
from datetime import datetime

from .run_store import run_store
from .operations_service import operations_service


class DashboardService:
    """Služba pro sestavení dat pro dashboard.

    Čerpá z run_store, operations_service a dalších zdrojů.
    """

    def get_summary(self) -> Dict[str, Any]:
        """Vrátí základní souhrn pro dashboard."""
        runs_count = run_store.count_runs()
        ops_count = operations_service.count()
        now = datetime.utcnow().isoformat()
        return {
            "timestamp": now,
            "runs_count": runs_count,
            "operations_count": ops_count,
        }


# Globální instance pro snadné použití
dashboard_service = DashboardService()
