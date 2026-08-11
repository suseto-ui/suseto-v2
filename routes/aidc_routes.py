# routes/aidc_routes.py
# Blueprint pro /api/v1/aidc/*

from flask import Blueprint, jsonify, request
from routes.helpers import current_user, require_role, body
from services.aidc_service import generate_qr, generate_barcode, scan_analysis
from services.aidc_batch import preview_csv, generate_batch


aidc_bp = Blueprint("aidc", __name__, url_prefix="/api/v1/aidc")


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
        return jsonify({"ok": True, "result": result})
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
