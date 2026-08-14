# services/aidc_core.py
import io
import base64
import logging

logger = logging.getLogger(__name__)

# --- BEZPEČNÉ IMPORTY ZÁVISLOSTÍ ---
try:
    import qrcode
    import qrcode.image.svg
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    import barcode
    from barcode.writer import ImageWriter, SVGWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False


def generate_qr(data: str, format: str = 'png', **kwargs) -> dict:
    """
    Plnohodnotný generátor QR kódů.
    Vrací slovník obsahující raw bajty (pro send_file) i base64 (pro JSON),
    čímž zachovává zpětnou kompatibilitu pro všechny vrstvy.
    """
    if not QRCODE_AVAILABLE:
        return {"success": False, "error": "Knihovna qrcode chybí. Spusťte pip install qrcode", "bytes": None}

    try:
        fmt = str(format).lower()
        out = io.BytesIO()

        if fmt == 'svg':
            factory = qrcode.image.svg.SvgImage
            img = qrcode.make(data, image_factory=factory, box_size=kwargs.get('box_size', 10), border=kwargs.get('border', 4))
            img.save(out)
            mime_type = "image/svg+xml"
        else:
            qr = qrcode.QRCode(
                version=kwargs.get('version', 1),
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=kwargs.get('box_size', 10),
                border=kwargs.get('border', 4),
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(out, format='PNG')
            mime_type = "image/png"

        img_bytes = out.getvalue()
        b64 = base64.b64encode(img_bytes).decode('utf-8')

        return {
            "success": True,
            "format": fmt,
            "mime_type": mime_type,
            "bytes": img_bytes,
            "image": f"data:{mime_type};base64,{b64}"
        }
    except Exception as e:
        logger.error(f"Chyba QR Core: {e}")
        return {"success": False, "error": str(e), "bytes": None}


def generate_barcode(data: str, barcode_type: str = 'code128', format: str = 'png', **kwargs) -> dict:
    """
    Plnohodnotný generátor čárových kódů. Dříve vracel jen metadata,
    nyní fyzicky generuje PNG a SVG obrázky.
    """
    if not BARCODE_AVAILABLE:
        return {"success": False, "error": "Knihovna python-barcode chybí. Spusťte pip install python-barcode pillow", "bytes": None}

    try:
        fmt = str(format).lower()
        b_type = str(barcode_type).lower()

        # Bezpečná detekce typu čárového kódu s fallbackem
        try:
            barcode_class = barcode.get_barcode_class(b_type)
        except barcode.errors.BarcodeNotFoundError:
            barcode_class = barcode.get_barcode_class('code128')

        writer = SVGWriter() if fmt == 'svg' else ImageWriter()
        bc = barcode_class(data, writer=writer)
        out = io.BytesIO()

        # Konfigurace vzhledu podle typu
        writer_options = {
            'module_width': kwargs.get('module_width', 0.2),
            'module_height': kwargs.get('module_height', 15.0),
            'font_size': kwargs.get('font_size', 10),
            'text_distance': kwargs.get('text_distance', 5.0),
            'quiet_zone': kwargs.get('quiet_zone', 6.5)
        }

        bc.write(out, options=writer_options)
        img_bytes = out.getvalue()

        mime_type = "image/svg+xml" if fmt == 'svg' else "image/png"
        b64 = base64.b64encode(img_bytes).decode('utf-8')

        return {
            "success": True,
            "format": fmt,
            "mime_type": mime_type,
            "bytes": img_bytes,
            "image": f"data:{mime_type};base64,{b64}",
            "metadata": {"type": b_type, "data": data}
        }
    except Exception as e:
        logger.error(f"Chyba Barcode Core: {e}")
        return {"success": False, "error": str(e), "bytes": None}


def scan_analysis(image_data, **kwargs) -> dict:
    """
    Placeholder pro budoucí analýzu naskenovaných kódů (OpenCV / pyzbar).
    """
    return {
        "success": True,
        "status": "unimplemented",
        "message": "Analýza fyzického obrazu zatím není v core aktivní.",
        "decoded_data": None
    }


# --- BACKWARD COMPATIBILITY ALIASES ---
# Abychom zachytili případné další interní importy ze starších modulů
_core_generate_qr = generate_qr
_core_generate_barcode = generate_barcode
_core_scan_analysis = scan_analysis
