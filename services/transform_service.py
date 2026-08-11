# services/transform_service.py
# Slu\u017eba pro transformaci dat (payloady, QR/1D obsah, atd.).

import base64
import binascii
from typing import Dict, Any, List, Optional, Callable
from urllib.parse import unquote, quote


class TransformService:
    """Slu\u017eba pro r\u016fzn\u00e9 transformace dat.

    Podporuje:
    - base64 encode/decode
    - hex encode/decode
    - URL encode/decode
    - obecn\u00e9 transformace funkcemi
    """

    def decode_base64(self, data: str) -> Dict[str, Any]:
        """Dek\u00f3duje base64 \u0159et\u011bzec na text."""
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
        """Dek\u00f3duje hex \u0159et\u011bzec na text."""
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
        """Dek\u00f3duje URL-encoded \u0159et\u011bzec."""
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

    def transform(
        self,
        data: str,
        transform_fn: Callable[[str], str],
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Aplikuje obecnou transforma\u010dníıı funkci na data.

        transform_fn: funkce, kter\u00e1 bere str a vrac\u00ed str.
        name: voliteln\u00fd n\u00e1zev transformace (pro logov\u00e1n\u00ed).
        """
        try:
            result = transform_fn(data)
            return {
                "success": True,
                "result": result,
                "error": None,
                "name": name,
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": str(e),
                "name": name,
            }

    def batch_transform(
        self,
        items: List[str],
        transform_fn: Callable[[str], str],
        name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Aplikuje transformaci na seznam polo\u017eek."""
        results = []
        for item in items:
            results.append(self.transform(item, transform_fn, name=name))
        return results


# Glob\u00e1ln\u00ed instance pro snadn\u00e9 pou\u017eit\u00ed
transform_service = TransformService()
