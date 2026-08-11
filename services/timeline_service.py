# services/timeline_service.py
# Z\u00e1kladn\u00ed slu\u017eba pro \u010dasovou osu ud\u00e1lost\u00ed (timeline).

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class TimelineService:
    """Jednoduch\u00fd storage pro \u010dasovou osu ud\u00e1lost\u00ed.

    Ukl\u00e1d\u00e1 data do pam\u011bti (list) – vhodn\u00e9 pro v\u00fdvoj a rychl\u00e9 lad\u011bn\u00ed.
    V produkci by m\u011blo b\u00fdt napojeno na DB / extern\u00ed storage.
    """

    def __init__(self):
        self._events: List[Dict[str, Any]] = []

    def add_event(
        self,
        event_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        entity_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """P\u0159idat ud\u00e1lost do timeline.

        Vrac\u00ed dict s informacemi o ud\u00e1losti.
        """
        event_id = str(uuid.uuid4())[:8]
        entry = {
            "event_id": event_id,
            "event_type": event_type,
            "description": description,
            "entity_id": entity_id,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._events.append(entry)
        return entry

    def get_events(
        self,
        limit: int = 50,
        event_type: Optional[str] = None,
        entity_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Vr\u00e1t\u00ed ud\u00e1losti (posledn\u00edch `limit`).

        event_type: voliteln\u00fd filtr podle typu ud\u00e1losti.
        entity_id: voliteln\u00fd filtr podle entity.
        """
        events = self._events
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        if entity_id:
            events = [e for e in events if e["entity_id"] == entity_id]
        # Se\u0159adit od nejnov\u011bj\u0161\u00edho
        events.sort(key=lambda e: e["timestamp"], reverse=True)
        return events[:limit]

    def clear_events(self) -> int:
        """Vyma\u017ee v\u0161echny ud\u00e1losti.

        Vrac\u00ed po\u010det smazan\u00fdch polo\u017eek.
        """
        count = len(self._events)
        self._events.clear()
        return count

    def count_events(self) -> int:
        """Vr\u00e1t\u00ed aktu\u00e1ln\u00ed po\u010det ud\u00e1lost\u00ed."""
        return len(self._events)


# Glob\u00e1ln\u00ed instance pro snadn\u00e9 pou\u017eit\u00ed
timeline_service = TimelineService()
