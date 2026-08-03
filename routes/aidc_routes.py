# routes/aidc_routes.py
# Blueprint pro /api/v1/aidc/*

from flask import Blueprint, jsonify, request
from routes.helpers import body
from services.aidc_service import generate_qr, generate_barcode, scan_analysis
from services.aidc_batch import preview_csv, generate_batch
from services.registry_store import match
from services.run_store import save_run

aidc_bp = Blueprint("aidc", __name__, url_prefix="/api/v1/aidc")


@aidc_bp.post("/generate")
def aidc_generate():
    d = body()
    kind = d.get("kind", "qr")
    fmt = d.get("format", "png")
    data = d.get("data", "")
    return generate_qr(data, fmt) if kind == "qr" else generate_barcode(data, kind, fmt)


@aidc_bp.post("/analyze-scan")
def aidc_analyze_scan():
    d = body()
    result = scan_analysis(d.get("payload", ""))
    result["registry_match"] = match(result["payload"])
    saved = save_run({
        "kind": "aidc_scan",
        "input": {"payload_preview": result["payload"][:120]},
        "summary": {"classification": result["classification"], "length": result.get("length", 0)}
    })
    return jsonify({**result, "run": saved})


@aidc_bp.post("/batch-preview")
def aidc_batch_preview():
    result, status = preview_csv(request.files.get("file"))
    return jsonify(result), status


@aidc_bp.post("/batch-generate")
def aidc_batch_generate():
    return generate_batch(
        request.files.get("file"),
        request.form.get("column", "0"),
        request.form.get("kind", "qr"),
        request.form.get("format", "png")
    )
