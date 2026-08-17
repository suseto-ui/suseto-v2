# routes/aidc_routes.py
# Blueprint pro /api/v1/aidc/*
import base64

from flask import Blueprint, jsonify, request
from routes.helpers import current_user, require_role, body
from services.aidc_service import generate_qr, generate_barcode, scan_analysis
from services.aidc_batch import preview_csv, generate_batch
from admin.services import log_scan
aidc_bp = Blueprint('aidc', __name__)
aidc_bp = Blueprint("aidc", __name__, url_prefix="/api/v1/aidc")

@aidc_bp.route('/scan-lab', methods=['POST'])
def process_scan():
    # ... existující kód pro spracování obrázku ...
    image = request.files.get('image')
    raw_result = "1234567890123"  # Získa se ze scanneru
    
    # Zápis do globální administrátorské databáze
    log_scan(
        scan_type='EAN13',
        raw_data=raw_result,
        parsed_json='{"gtin": "1234567890123"}',
        image_file=image,
        ip_address=request.remote_addr
    )
    
    return jsonify({"status": "success", "result": raw_result})


@aidc_bp.post("/generate")
def aidc_generate():
    """Generuje jeden QR nebo 1D barcode podle zadaného payloadu.

    Očekává JSON tělo:
    {
      "data": "payload",
      "kind": "qr" | "code128" | "ean13" | "upca",
      "format": "png" | "svg"
    }

    Vrací JSON s informacemi o vygenerovaném kódu (např. base64-encoded obraz).
    """
    if not current_user():
        return jsonify({"error": "Přihlas se."}), 401

    d = body()
    data = d.get("data", "")
    kind = d.get("kind", "qr")
    fmt = d.get("format", "png")

    try:
        result = generate_qr(data, kind, fmt) if kind == "qr" else generate_barcode(data, kind, fmt)
        encoded_result = base64.b64encode(result).decode('utf-8')
        return jsonify({"ok": True, "result": encoded_result})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@aidc_bp.post("/analyze-scan")
def aidc_analyze_scan():
    """Analyzuje jeden payload ze Scanner Labu.

    Očekává JSON tělo:
    {
      "payload": "text nebo data z QR/barcode"
    }

    Vrací JSON s klasifikací a doporučením (jak je navržené v scan_analysis).
    """
    if not current_user():
        return jsonify({"error": "Přihlas se."}), 401

    d = body()
    payload = d.get("payload", "")
    result = scan_analysis(payload)
    return jsonify({"ok": True, "analysis": result})


@aidc_bp.post("/batch/preview")
def aidc_batch_preview():
    """Předběžný náhled CSV dávky pro AIDC Batch.

    Očekává multipart/form-data s `file` (CSV UTF-8) a volitelným `column`.

    Vrací JSON s preview daty (např. prvních pár payloadů a zjištěnými sloupci).
    """
    if not require_role("admin", "operator"):
        return jsonify({"error": "Vyžadována role operator nebo admin."}), 403

    f = request.files.get("file")
    if not f:
        return jsonify({"error": "Nahraj CSV soubor."}), 400

    column = request.form.get("column")
    try:
        preview = preview_csv(f.read(), column)
        return jsonify({"ok": True, "preview": preview})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@aidc_bp.post("/batch/generate")
def aidc_batch_generate():
    """Generuje ZIP dávku QR/1D kódů z CSV podle parametrů.

    Očekává multipart/form-data s `file` (CSV), `column`, `kind`, `format`.

    Vrací JSON s informací o výsledném ZIP (např. path nebo token), samotný ZIP
    se může stahovat přes samostatný endpoint.
    """
    if not require_role("admin", "operator"):
        return jsonify({"error": "Vyžadována role operator nebo admin."}), 403

    f = request.files.get("file")
    if not f:
        return jsonify({"error": "Nahraj CSV soubor."}), 400

    column = request.form.get("column")
    kind = request.form.get("kind", "qr")
    fmt = request.form.get("format", "png")

    try:
        batch_info = generate_batch(f.read(), column, kind, fmt)
        return jsonify({"ok": True, "batch": batch_info})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# --- COMPATIBILITY WRAPPER FOR aidc_studio.js ---
from flask import send_file, request, jsonify
import io

@aidc_bp.route('/generate', methods=['POST'])
def generate_code_endpoint():
    """
    Routa obsluhující frontend aidc_studio.js.
    Zajišťuje, že backend vrátí binární Blob, nikoliv stringified JSON.
    """
    data = request.get_json() or {}
    kind = data.get('kind', 'qr')
    payload = data.get('data', '')
    fmt = data.get('format', 'png')

    if not payload:
        return jsonify({"error": "Chybí data pro generování"}), 400

    # Delegace na opravený core (přes aidc_service, pokud existuje, jinak napřímo)
    if kind == 'qr':
        from services.aidc_core import _core_generate_qr
        result = _core_generate_qr(payload, format=fmt)
    else:
        from services.aidc_core import _core_generate_barcode
        result = _core_generate_barcode(payload, barcode_type=kind, format=fmt)

    if not result.get("success"):
        return jsonify({"error": result.get("error", "Generování selhalo")}), 400

    # Klíčový krok: Vrácení binárních dat (BLOB) pro zobrazení obrázku v UI
    return send_file(
        io.BytesIO(result['bytes']),
        mimetype=result['mime_type'],
        as_attachment=False,  # Frontend si vytvoří URL objekt sám
        download_name=f"suseto-code.{fmt}"
    )
