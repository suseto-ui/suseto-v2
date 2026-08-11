# services/location_service.py
# Z\u00e1kladn\u00ed slu\u017eba pro pr\u00e1ci s geografickou polohou.

from typing import Dict, Any, List, Optional
from datetime import datetime


class LocationService:
    """Jednoduch\u00fd storage pro geografick\u00e9 polohy.

    Ukl\u00e1d\u00e1 polohy do pam\u011bti (dict) – vhodn\u00e9 pro v\u00fdvoj a rychl\u00e9 lad\u011bn\u00ed.
    V produkci by m\u011blo b\u00fdt napojeno na DB / extern\u00ed storage.
    """

    def __init__(self):
        self._locations: Dict[str, Dict[str, Any]] = {}

    def store_location(
        self,
        label: str,
        latitude: float,
        longitude: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Ulo\u017e\u00ed polohu pod dan\u00fdm labelu.

        Vrac\u00ed dict s informacemi o ulo\u017een\u00e9 poloze.
        """
        entry = {
            "label": label,
            "latitude": latitude,
            "longitude": longitude,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        self._locations[label] = entry
        return entry

    def get_location(self, label: str) -> Optional[Dict[str, Any]]:
        """Z\u00edsk\u00e1 polohu podle labelu.

        Vrac\u00ed None, pokud poloha neexistuje.
        """
        return self._locations.get(label)

    def list_locations(self) -> List[Dict[str, Any]]:
        """Vr\u00e1t\u00ed seznam v\u0161ech ulo\u017een\u00fdch poloh."""
        return list(self._locations.values())

    def clear_locations(self) -> int:
        """Vyma\u017ee v\u0161echny ulo\u017een\u00e9 polohy.

        Vrac\u00ed po\u010det smazan\u00fdch polo\u017eek.
        """
        count = len(self._locations)
        self._locations.clear()
        return count

    def count_locations(self) -> int:
        """Vr\u00e1t\u00ed aktu\u00e1ln\u00ed po\u010det ulo\u017een\u00fdch poloh."""
        return len(self._locations)


# Glob\u00e1ln\u00ed instance pro snadn\u00e9 pou\u017eit\u00ed
location_service = LocationService()
