# services/aidc_batch.py
# Pomocný modul pro AIDC Batch – náhled CSV a generování dávky.

import csv
import io
from typing import List, Dict, Any, Optional


def preview_csv(csv_bytes: bytes, column: Optional[str] = None) -> Dict[str, Any]:
    """Vrátí náhled CSV souboru.

    - csv_bytes: obsah CSV souboru v bajtech (UTF-8)
    - column: volitelné jméno sloupce s payloadem

    Vrací dict:
    {
      "columns": ["col1", "col2", ...],
      "sample": [ {"col1": "...", "col2": "..."}, ... ],
      "payload_column": "colX" nebo None
    }
    """
    text = csv_bytes.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows: List[Dict[str, Any]] = []
    for i, row in enumerate(reader):
        rows.append(row)
        if i >= 9:
            break

    columns = reader.fieldnames or []
    payload_col = column if column in columns else (columns[0] if columns else None)

    return {
        "columns": columns,
        "sample": rows,
        "payload_column": payload_col,
    }


def generate_batch(csv_bytes: bytes, column: Optional[str], kind: str, fmt: str) -> Dict[str, Any]:
    """Připraví informace o dávce pro generování QR/1D kódů.

    - csv_bytes: obsah CSV souboru
    - column: jméno sloupce s payloadem (pokud None, vezme první sloupec)
    - kind: "qr", "code128", "ean13", "upca" ...
    - fmt: "png" nebo "svg"

    Vrací dict:
    {
      "count": počet platných payloadů,
      "kind": kind,
      "format": fmt,
      "column": použité jméno sloupce
    }
    """
    text = csv_bytes.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    columns = reader.fieldnames or []
    if not columns:
        raise ValueError("CSV soubor neobsahuje žádné sloupce.")

    payload_col = column if column in columns else columns[0]
    count = 0
    for row in reader:
        value = (row.get(payload_col) or "").strip()
        if value:
            count += 1

    return {
        "count": count,
        "kind": kind,
        "format": fmt,
        "column": payload_col,
    }
