"""
Simple locations data for Suseto.
"""

LOCATIONS = [
    {"id": "cz-praha", "name": "Praha, CZ", "lat": 50.0755, "lng": 14.4378},
    {"id": "cz-brno", "name": "Brno, CZ", "lat": 49.1951, "lng": 16.6068},
    {"id": "sk-bratislava", "name": "Bratislava, SK", "lat": 48.1486, "lng": 17.1077},
    {"id": "de-berlin", "name": "Berlin, DE", "lat": 52.5200, "lng": 13.4050},
]

def load_locations():
    return LOCATIONS
