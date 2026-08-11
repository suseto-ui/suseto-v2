# services/error_logger.py
# Z\u00e1kladn\u00ed slu\u017eba pro logov\u00e1n\u00ed chyb – pam\u011b\u0165ov\u00fd storage pro chyby.

import time
from typing import Dict, Any, List, Optional
from datetime import datetime


class ErrorLogger:
    """Jednoduch\u00fd logger chyb pro backend.

    Ukl\u00e1d\u00e1 chyby do pam\u011bti (list) – vhodn\u00e9 pro v\u00fdvoj a rychl\u00e9 lad\u011bn\u00ed.
    V produkci by m\u011blo b\u00fdt napojeno na DB / extern\u00ed logging syst\u00e9m.
    """

    def __init__(self):
        self._errors: List[Dict[str, Any]] = []

    def log_error(
        self,
        message: str,
        level: str = "ERROR",
        source: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Zaznamen\u00e1 chybu.

        Vrac\u00ed dict s informacemi o zaznamenan\u00e9 chyb\u011b.
        """
        entry = {
            "id": len(self._errors) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "timestamp_unix": time.time(),
            "level": level,
            "message": message,
            "source": source,
            "details": details or {},
        }
        self._errors.append(entry)
        return entry

    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Vr\u00e1t\u00ed posledn\u00edch `limit` chyb."""
        return self._errors[-limit:]

    def clear_errors(self) -> int:
        """Vyma\u017ee v\u0161echny ulo\u017een\u00e9 chyby.

        Vrac\u00ed po\u010det smazan\u00fdch polo\u017eek.
        """
        count = len(self._errors)
        self._errors.clear()
        return count

    def count_errors(self) -> int:
        """Vr\u00e1t\u00ed aktu\u00e1ln\u00ed po\u010det ulo\u017een\u00fdch chyb."""
        return len(self._errors)


# Glob\u00e1ln\u00ed instance pro snadn\u00e9 pou\u017eit\u00ed
error_logger = ErrorLogger()
