"""
Dashboard stats for Suseto.
"""

def dashboard_stats():
    return {
        "kpis": [
            {"label": "Total Scans", "value": 1247, "delta": 12},
            {"label": "Unique Items", "value": 389, "delta": 5},
            {"label": "Locations", "value": 4, "delta": 0},
        ],
        "chart": {
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "values": [120, 150, 180, 220, 190, 240, 210],
        }
    }
