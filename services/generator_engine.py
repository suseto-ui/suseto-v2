# services/generator_engine.py
# Gener\u00e1tor QR/1D k\u00f3d\u016f – wrapper nad aidc_core pro generov\u00e1n\u00ed.

from typing import Dict, Any

from .aidc_core import generate_qr as _core_generate_qr, generate_barcode as _core_generate_barcode


class GeneratorEngine:
    """Engine pro generov\u00e1n\u00ed QR a 1D k\u00f3d\u016f.

    Deleguje na aidc_core, aby byla logika centralizovan\u00e1.
    """

    def generate_qr(self, data: str, kind: str = "qr", fmt: str = "png") -> Dict[str, Any]:
        """Generuje QR k\u00f3d pro dan\u00fd payload."""
        return _core_generate_qr(data, kind=kind, fmt=fmt)

    def generate_barcode(self, data: str, kind: str = "code128", fmt: str = "png") -> Dict[str, Any]:
        """Generuje 1D k\u00f3d (barcode) pro dan\u00fd payload."""
        return _core_generate_barcode(data, kind=kind, fmt=fmt)

    def generate(self, kind: str, data: str, fmt: str = "png") -> Dict[str, Any]:
        """Univerz\u00e1ln\u00ed metoda pro generov\u00e1n\u00ed QR/1D k\u00f3d\u016f.

        kind: "qr" nebo "barcode" (p\u0159\u00edpadn\u011b jin\u00fd typ v budoucnu).
        """
        if kind == "qr":
            return self.generate_qr(data, kind=kind, fmt=fmt)
        elif kind == "barcode":
            return self.generate_barcode(data, kind="code128", fmt=fmt)
        else:
            # Placeholder pro nezn\u00e1m\u00fd typ
            return {
                "kind": kind,
                "format": fmt,
                "payload": data,
                "image": None,
                "error": f"Nezn\u00e1m\u00fd typ gener\u00e1toru: {kind}",
            }


# Glob\u00e1ln\u00ed instance pro snadn\u00e9 pou\u017eit\u00ed
generator_engine = GeneratorEngine()
