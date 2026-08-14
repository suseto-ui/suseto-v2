# services/database.py
# Základní DB wrapper – zatím jen placeholder.

from typing import Any, List, Dict


class Database:
    """Mock databáze pro vývoj.

    V produkci nahrazeno skutečnou DB (SQLAlchemy, atd.).
    """

    def __init__(self):
        self._tables: Dict[str, List[Dict[str, Any]]] = {}

    def insert(self, table: str, row: Dict[str, Any]) -> None:
        self._tables.setdefault(table, []).append(row)

    def select_all(self, table: str) -> List[Dict[str, Any]]:
        return list(self._tables.get(table, []))

    def clear_table(self, table: str) -> int:
        rows = self._tables.get(table, [])
        count = len(rows)
        self._tables[table] = []
        return count


# Globální instance pro snadné použití
database = Database()
# --- COMPATIBILITY WRAPPER FOR app.py ---
# Mock objekt pro SQLAlchemy importy, zajišťuje bezpečný start 
# bez rozbití stávajícího in-memory / custom DB řešení.
class MockDB:
    def init_app(self, app):
        pass

    def create_all(self):
        pass

db = MockDB()
