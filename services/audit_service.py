# services/audit_service.py
# Základní auditní služba – logování akcí (kdo co kdy udělal).

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class AuditService:
    """Jednoduchý audit log pro backend.

    Ukládá záznamy do paměti (list) – vhodné pro vývoj a rychlé ladění.
    V produkci by mělo být napojeno na DB / externí logging systém.
    """

    def __init__(self):
        self._entries: List[Dict[str, Any]] = []

    def log_action(
        self,
        actor: str,
        action: str,
        target: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Zaznamená akci do audit logu."""
        entry_id = str(uuid.uuid4())[:8]
        entry = {
            "id": entry_id,
            "actor": actor,
            "action": action,
            "target": target,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._entries.append(entry)
        return entry

    def list_actions(
        self,
        limit: int = 100,
        actor: Optional[str] = None,
        action: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Vrátí seznam auditních záznamů."""
        entries = self._entries
        if actor:
            entries = [e for e in entries if e["actor"] == actor]
        if action:
            entries = [e for e in entries if e["action"] == action]
        entries.sort(key=lambda e: e["timestamp"], reverse=True)
        return entries[:limit]

    def clear(self) -> int:
        """Vymaže všechny auditní záznamy."""
        count = len(self._entries)
        self._entries.clear()
        return count

    def count(self) -> int:
        """Vrátí počet auditních záznamů."""
        return len(self._entries)


# Globální instance pro snadné použití
audit_service = AuditService()
# --- COMPATIBILITY WRAPPER FOR routes ---
def write(*args, **kwargs):
    """
    Kompatibilní modulová funkce očekávaná routami a admin vrstvou.
    Deleguje volání na novější instanční metodu log_action.
    """
    return audit_service.log_action(*args, **kwargs)
