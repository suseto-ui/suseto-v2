# services/decode_service.py
# Základní služba pro dekódování/encodování různých formátů.

import base64
import binascii
from typing import Dict, Any, List
from urllib.parse import unquote, quote


# ---------------------------------------------------------------------------
# Module-level funkce – importuje je routes/decode_routes.py
# ---------------------------------------------------------------------------

def chain(payload: str) -> Dict[str, Any]:
    """Postupně zkouší dekódovat payload přes všechny vrstvy (url → base64 → hex).

    Vrací dict s 'original', 'final' a 'steps' (výsledek každého kroku).
    """
    text = str(payload or "").strip()
    steps = []
    current = text

    # Krok 1: URL decode
    try:
        url_decoded = unquote(current)
        changed = url_decoded != current
        steps.append({"layer": "url", "result": url_decoded, "changed": changed})
        if changed:
            current = url_decoded
    except Exception as e:
        steps.append({"layer": "url", "result": current, "changed": False, "error": str(e)})

    # Krok 2: base64 decode
    try:
        b64_bytes = base64.b64decode(current)
        b64_str = b64_bytes.decode("utf-8")
        steps.append({"layer": "base64", "result": b64_str, "changed": True})
        current = b64_str
    except Exception:
        steps.append({"layer": "base64", "result": current, "changed": False})

    # Krok 3: hex decode
    try:
        hex_bytes = binascii.unhexlify(current)
        hex_str = hex_bytes.decode("utf-8")
        steps.append({"layer": "hex", "result": hex_str, "changed": True})
        current = hex_str
    except Exception:
        steps.append({"layer": "hex", "result": current, "changed": False})

    return {
        "original": text,
        "final": current,
        "steps": steps,
    }


def pattern_library(payloads: List[str]) -> List[Dict[str, Any]]:
    """Prožene každý payload z listu přes chain analýzu.

    Vrací list výsledků ve stejném pořadí jako vstupní payloads.
    """
    return [chain(p) for p in (payloads or [])]


# ---------------------------------------------------------------------------
# OO vrstva – zachována beze změny
# ---------------------------------------------------------------------------

class DecodeService:
    """Služba pro dekódování a encodování běžných formátů.

    Podporuje:
    - base64
    - hex
    - URL encoding/decoding
    """

    def decode_base64(self, data: str) -> Dict[str, Any]:
        """Dekóduje base64 řetězec na text.

        Vrací dict s 'success', 'result' a 'error'.
        """
        try:
            decoded_bytes = base64.b64decode(data)
            decoded_str = decoded_bytes.decode("utf-8")
            return {"success": True, "result": decoded_str, "error": None}
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    def encode_base64(self, data: str) -> Dict[str, Any]:
        """Encoduje text do base64."""
        try:
            encoded_bytes = base64.b64encode(data.encode("utf-8"))
            encoded_str = encoded_bytes.decode("ascii")
            return {"success": True, "result": encoded_str, "error": None}
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    def decode_hex(self, data: str) -> Dict[str, Any]:
        """Dekóduje hex řetězec na text."""
        try:
            decoded_bytes = binascii.unhexlify(data)
            decoded_str = decoded_bytes.decode("utf-8")
            return {"success": True, "result": decoded_str, "error": None}
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    def encode_hex(self, data: str) -> Dict[str, Any]:
        """Encoduje text do hex."""
        try:
            encoded_bytes = binascii.hexlify(data.encode("utf-8"))
            encoded_str = encoded_bytes.decode("ascii")
            return {"success": True, "result": encoded_str, "error": None}
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    def decode_url(self, data: str) -> Dict[str, Any]:
        """Dekóduje URL-encoded řetězec."""
        try:
            decoded_str = unquote(data)
            return {"success": True, "result": decoded_str, "error": None}
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    def encode_url(self, data: str) -> Dict[str, Any]:
        """Encoduje text pro URL."""
        try:
            encoded_str = quote(data)
            return {"success": True, "result": encoded_str, "error": None}
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}
