# services/decode_service.py
# Z\u00e1kladn\u00ed slu\u017eba pro dek\u00f3dov\u00e1n\u00ed/encodov\u00e1n\u00ed r\u016fzn\u00fdch form\u00e1t\u016f.

import base64
import binascii
from typing import Dict, Any
from urllib.parse import unquote, quote


class DecodeService:
    """Slu\u017eba pro dek\u00f3dov\u00e1n\u00ed a encodov\u00e1n\u00ed b\u011b\u017en\u00fdch form\u00e1t\u016f.

    Podporuje:
    - base64
    - hex
    - URL encoding/decoding
    """

    def decode_base64(self, data: str) -> Dict[str, Any]:
        """Dek\u00f3duje base64 \u0159et\u011bzec na text.

        Vrac\u00ed dict s 'success', 'result' a 'error'.
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
