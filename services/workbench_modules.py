# services/workbench_modules.py
# Definice modulů pro Workbench - placeholder kostra

from typing import Dict, Any

class BaseModule:
    """Základní třída pro všechny workbench moduly."""
    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "unimplemented"}

class QRCodeModule(BaseModule):
    """Modul pro generování QR kódů."""
    pass

class BarcodeModule(BaseModule):
    """Modul pro generování 1D kódů."""
    pass

class DecodeModule(BaseModule):
    """Modul pro dekódování."""
    pass

class TransformModule(BaseModule):
    """Modul pro transformace dat."""
    pass

# Registr dostupných modulů
AVAILABLE_MODULES = {
    "qr": QRCodeModule,
    "barcode": BarcodeModule,
    "decode": DecodeModule,
    "transform": TransformModule,
}
