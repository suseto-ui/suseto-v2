# services/aidc_service.py
# Aplikační··vrstva AIDC – orchestrace volá··funkce z aidc_core.

from typing import Dict, Any, List, Optional

from .aidc_core import (     generate_qr as _core_generate_qr,     generate_barcode as _core_generate_barcode,     scan_analysis as _core_scan_analysis, )  def generate_qr(data: str, kind: str = "qr", fmt: str = "png") -> Dict[str, Any]:     return _core_generate_qr(data, kind=kind, fmt=fmt)  def generate_barcode(data: str, kind: str = "code128", fmt: str = "png") -> Dict[str, Any]:     return _core_generate_barcode(data, kind=kind, fmt=fmt)  def scan_analysis(payload: str) -> Dict[str, Any]:     return _core_scan_analysis(payload)


class AidcService:
    """Hlavní··služba pro generov\u00e1n\u00ed QR/1D k\u00f3d\u016f a anal\u00fdzu payloadu."""

    def generate_qr(self, data: str, kind: str = "qr", fmt: str = "png") -> Dict[str, Any]:
        """Generuje QR k\u00f3d pro dan\u00fd payload."""
        return generate_qr(data, kind=kind, fmt=fmt)

    def generate_barcode(self, data: str, kind: str = "code128", fmt: str = "png") -> Dict[str, Any]:
        """Generuje 1D k\u00f3d (barcode) pro dan\u00fd payload."""
        return generate_barcode(data, kind=kind, fmt=fmt)

    def analyze_payload(self, payload: str) -> Dict[str, Any]:
        """Provede anal\u00fdzu payloadu (d\u00e9lka, typ, URL atd.)."""
        return scan_analysis(payload)


class AidcBatchService:
    """Služba pro d\u00e1vkov\u00e9 generov\u00e1n\u00ed QR/1D k\u00f3d\u016f."""

    def __init__(self):
        self._core = AidcService()

    def generate_batch_qr(
        self,
        payloads: List[str],
        kind: str = "qr",
        fmt: str = "png",
    ) -> List[Dict[str, Any]]:
        """Generuje sadu QR k\u00f3d\u016f pro seznam payload\u016f."""
        results = []
        for p in payloads:
            results.append(self._core.generate_qr(p, kind=kind, fmt=fmt))
        return results

    def generate_batch_barcode(
        self,
        payloads: List[str],
        kind: str = "code128",
        fmt: str = "png",
    ) -> List[Dict[str, Any]]:
        """Generuje sadu 1D k\u00f3d\u016f pro seznam payload\u016f."""
        results = []
        for p in payloads:
            results.append(self._core.generate_barcode(p, kind=kind, fmt=fmt))
        return results


class AidcStudioService:
    """Služba pro AIDC Studio – interaktivn\u00ed generov\u00e1n\u00ed a n\u00e1hledy."""

    def __init__(self):
        self._core = AidcService()

    def preview_qr(self, data: str, kind: str = "qr", fmt: str = "png") -> Dict[str, Any]:
        """Vytvoř\u00ed n\u00e1hled QR k\u00f3du pro AIDC Studio."""
        return self._core.generate_qr(data, kind=kind, fmt=fmt)

    def preview_barcode(self, data: str, kind: str = "code128", fmt: str = "png") -> Dict[str, Any]:
        """Vytvoř\u00ed n\u00e1hled 1D k\u00f3du pro AIDC Studio."""
        return self._core.generate_barcode(data, kind=kind, fmt=fmt)

    def analyze(self, payload: str) -> Dict[str, Any]:
        """Anal\u00fdza payloadu pro zobrazen\u00ed v AIDC Studio."""
        return self._core.analyze_payload(payload)
