# services/aidc_core.py
# Jádro AIDC logiky – generování QR/1D kódů a analýza payloadu.

import base64
from typing import Dict, Any

try:
    import qrcode
except ImportError:  # pokud qrcode není k dispozici, necháme jen placeholder
    qrcode = None


def generate_qr(data: str, kind: str = "qr", fmt: str = "png") -> Dict[str, Any]:
    """Generuje QR kód pro daný payload.

    Vrací dict s informacemi o kódu. Pokud není dostupná knihovna qrcode,
    vrátí pouze strukturu s payloadem a typem.
    """
    if not data:
        raise ValueError("Payload je prázdný.")

    if qrcode is None:
        # Minimálně vraťme metadata, aby frontend věděl, co se děje.
        return {"kind": kind, "format": fmt, "payload": data, "image": None}

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    import io
    buf = io.BytesIO()
    if fmt == "png":
        img.save(buf, format="PNG")
    else:
        img.save(buf, format="PNG")  # zatím podporujeme PNG
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("ascii")

    return {
        "kind": kind,
        "format": fmt,
        "payload": data,
        "image": b64,
    }


def generate_barcode(data: str, kind: str = "code128", fmt: str = "png") -> Dict[str, Any]:
    """Placeholder pro generování 1D kódů.

    Aktuálně negeneruje skutečný obrázek (není-li k dispozici knihovna pro 1D kódy),
    ale vrací metadata, aby aplikace nespadla.
    """
    if not data:
        raise ValueError("Payload je prázdný.")

    # TODO: pokud přidáš knihovnu pro 1D kódy (např. python-barcode), můžeš zde
    # generovat skutečný obrázek podobně jako u QR kódu.
    return {
        "kind": kind,
        "format": fmt,
        "payload": data,
        "image": None,
    }


def scan_analysis(payload: str) -> Dict[str, Any]:
    """Základní analýza payloadu pro Scanner / AIDC.

    Vrací jednoduchou klasifikaci: délka, alfanumerické / numerické,
    případně detekci URL.
    """
    text = payload or ""
    is_numeric = text.isdigit()
    is_alpha = text.isalpha()
    is_alnum = text.isalnum()
    looks_like_url = text.startswith("http://") or text.startswith("https://")

    return {
        "payload": text,
        "length": len(text),
        "numeric": is_numeric,
        "alpha": is_alpha,
        "alnum": is_alnum,
        "url": looks_like_url,
    }
