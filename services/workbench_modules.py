# services/workbench_modules.py
# Definice modulu pro Workbench

class BaseModule:
    def process(self, payload):
        return {"status": "unimplemented"}

class QRCodeModule(BaseModule):
    pass

class BarcodeModule(BaseModule):
    pass

class DecodeModule(BaseModule):
    pass

class TransformModule(BaseModule):
    pass

AVAILABLE_MODULES = {
    "qr": QRCodeModule,
    "barcode": BarcodeModule,
    "decode": DecodeModule,
    "transform": TransformModule,
}
