# services/error_logger.py
# Z\u00e1kladn\u00ed slu\u017eba pro logov\u00e1n\u00ed chyb – pam\u011b\u0165ov\u00e1 implementace pro stabilitu backendu.

import time
from typing import Dict, Any, List, Optional


class ErrorLogger:
    """Jednoduch\u00fd logger chyb ulo\u017een\u00fd v pam\u011bti.

    Toto je minim\u00e1ln\u00ed implementace, aby backend nespadl a ostatn\u00ed moduly m\u011bly co volat.
    Re\u00e1ln\u00e1 logika (souborov\u00e9 logy, DB, extern\u00ed syst\u00e9my) bude dopln\u011bna p\u0159i lad\u011bn\u00ed.
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
        """Zaznamen\u00e1 chybu do intern\u00edho seznamu.

        Vrac\u00ed informaci o zaznamenan\u00e9 chyb\u011b.
        """
        entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            "source": source,
            "details": details or {},
        }
        self._errors.append(entry)
        return entry

    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Vr\u00e1t\u00ed posledn\u00edch `limit` chyb se\u0159azen\u00fdch od nejnov\u011bj\u0161\u00edch."""
        return list(reversed(self._errors[-limit:]))

    def clear_errors(self) -> int:
        """Sma\u017ee v\u0161echny ulo\u017een\u00e9 chyby a vr\u00e1t\u00ed po\u010det smazan\u00fdch polo\u017eek."""
        count = len(self._errors)
        self._errors.clear()
        return count


# Glob\u00e1ln\u00ed instance pro snadn\u00e9 pou\u017eit\u00ed v jin\u00fdch modulech
error_logger = ErrorLogger()
