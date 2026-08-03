"""
Simple registry data for Suseto.
"""

REGISTRY = [
    {"id": "gtin", "name": "GTIN", "description": "Global Trade Item Number"},
    {"id": "gs1", "name": "GS1", "description": "GS1 barcode standards"},
    {"id": "wifi", "name": "WIFI", "description": "Wi-Fi QR payload"},
    {"id": "url", "name": "URL", "description": "Web address"},
]

def load_registry():
    return REGISTRY
