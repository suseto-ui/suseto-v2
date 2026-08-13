# services/aidc_service.py
# Aplikační vrstva AIDC – orchestrace volá funkce z aidc_core.

from typing import Dict, Any, List, Optional

from .aidc_core import (
    generate_qr as _core_generate_qr,
    generate_barcode as _core_generate_barcode,
    scan_analysis as _core_scan_analysis,
)


# ---------------------------------------------------------------------------
# Module-level compat wrappers – tyto funkce importuje routes/aidc_routes.py
# ---------------------------------------------------------------------------

def generate_qr(data: str, kind: str = "qr", fmt: str = "png") -> Dict[str, Any]:
    """Generuje QR kód pro daný payload. Vrací JSON-serializovatelný dict."""
    return _core_generate_qr(data, kind=kind, fmt=fmt)


def generate_barcode(data: str, kind: str = "code128", fmt: str = "png") -> Dict[str, Any]:
    """Generuje 1D kód (barcode) pro daný payload. Vrací JSON-serializovatelný dict."""
    return _core_generate_barcode(data, kind=kind, fmt=fmt)


def scan_analysis(payload: str) -> Dict[str, Any]:
    """Základní analýza payloadu pro Scanner / AIDC. Vrací JSON-serializovatelný dict."""
    return _core_scan_analysis(payload)


# ---------------------------------------------------------------------------
# OO vrstva – zachována beze změny
# ---------------------------------------------------------------------------

class AidcService:
    """Hlavní služba pro generování QR/1D kódů a analýzu payloadu."""

    def generate_qr(self, data: str, kind: str = "qr", fmt: str = "png") -> Dict[str, Any]:
        return generate_qr(data, kind=kind, fmt=fmt)

    def generate_barcode(self, data: str, kind: str = "code128", fmt: str = "png") -> Dict[str, Any]:
        return generate_barcode(data, kind=kind, fmt=fmt)

    def analyze_payload(self, payload: str) -> Dict[str, Any]:
        return scan_analysis(payload)


class AidcBatchService:
    """Služba pro dávkové generování QR/1D kódů."""

    def __init__(self):
        self._core = AidcService()

    def generate_batch_qr(self, payloads: List[str], kind: str = "qr", fmt: str = "png") -> List[Dict[str, Any]]:
        return [self._core.generate_qr(p, kind=kind, fmt=fmt) for p in payloads]

    def generate_batch_barcode(self, payloads: List[str], kind: str = "code128", fmt: str = "png") -> List[Dict[str, Any]]:
        return [self._core.generate_barcode(p, kind=kind, fmt=fmt) for p in payloads]


class AidcStudioService:
    """Služba pro AIDC Studio – interaktivní generování a náhledy."""

    def __init__(self):
        self._core = AidcService()

    def preview_qr(self, data: str, kind: str = "qr", fmt: str = "png") -> Dict[str, Any]:
        return self._core.generate_qr(data, kind=kind, fmt=fmt)

    def preview_barcode(self, data: str, kind: str = "code128", fmt: str = "png") -> Dict[str, Any]:
        return self._core.generate_barcode(data, kind=kind, fmt=fmt)

    def analyze(self, payload: str) -> Dict[str, Any]:
        return self._core.analyze_payload(payload)
