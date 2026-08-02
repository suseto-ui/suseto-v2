# services/workbench_routes.py
from flask import Blueprint, request, jsonify, render_template, Response
from services.workbench_service import (
    ingest_identifier, run_analysis_pipeline, run_reverse_engineering, run_test_harness
)
from services.workbench_modules import (
    batch_analyze, batch_to_csv, build_timeline, detect_patterns,
    parse_gs1, parse_rfid_dump, analyze_entropy, inspect_jwt,
    scan_credentials, compare_identifiers
)

wb = Blueprint("workbench", __name__)

def ok(data): return jsonify({"ok": True, **data})
def err(msg, code=400): return jsonify({"ok": False, "error": msg}), code

def jbody():
    return request.get_json(force=True, silent=True) or {}

def register_workbench(app):
    app.register_blueprint(wb)

@wb.route("/workbench")
def workbench_page():
    return render_template("pages/workbench.html")

# ── core ──────────────────────────────────────────────────────────────────────
@wb.route("/api/v1/workbench/ingest", methods=["POST"])
def wb_ingest():
    b = jbody()
    raw = b.get("raw","").strip()
    if not raw: return err("Chybi 'raw'")
    ident = ingest_identifier(raw, b.get("meta", {}))
    return ok({"identifier": ident.to_dict()})

@wb.route("/api/v1/workbench/analyze", methods=["POST"])
def wb_analyze():
    b = jbody()
    if not b.get("identifier"): return err("Chybi 'identifier'")
    return ok({"analysis": run_analysis_pipeline(b["identifier"])})

@wb.route("/api/v1/workbench/reverse", methods=["POST"])
def wb_reverse():
    b = jbody()
    raw = b.get("raw","").strip()
    if not raw: return err("Chybi 'raw'")
    return ok({"reverse": run_reverse_engineering(raw)})

@wb.route("/api/v1/workbench/test-run", methods=["POST"])
def wb_test_run():
    b = jbody()
    if not b.get("target"): return err("Chybi 'target'")
    return ok({"report": run_test_harness(b["target"], b.get("profile", {}))})

# ── batch ─────────────────────────────────────────────────────────────────────
@wb.route("/api/v1/workbench/batch", methods=["POST"])
def wb_batch():
    b = jbody()
    csv_text = b.get("csv","")
    if not csv_text: return err("Chybi 'csv' (text CSV)")
    result = batch_analyze(csv_text, b.get("column","code"))
    return ok({"batch": result})

@wb.route("/api/v1/workbench/batch/export", methods=["POST"])
def wb_batch_export():
    b = jbody()
    results = b.get("results", [])
    csv_out = batch_to_csv(results)
    return Response(csv_out, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=workbench_export.csv"})

# ── timeline ──────────────────────────────────────────────────────────────────
@wb.route("/api/v1/workbench/timeline", methods=["POST"])
def wb_timeline():
    b = jbody()
    codes = b.get("codes", [])
    if isinstance(codes, str):
        codes = [c.strip() for c in codes.replace(",","
").split("
") if c.strip()]
    if not codes: return err("Chybi 'codes' (seznam kodu)")
    return ok({"timeline": build_timeline(codes)})

# ── pattern detector ──────────────────────────────────────────────────────────
@wb.route("/api/v1/workbench/patterns", methods=["POST"])
def wb_patterns():
    b = jbody()
    codes = b.get("codes", [])
    if isinstance(codes, str):
        codes = [c.strip() for c in codes.replace(",","
").split("
") if c.strip()]
    if not codes: return err("Chybi 'codes'")
    return ok({"patterns": detect_patterns(codes)})

# ── GS1 / GTIN ────────────────────────────────────────────────────────────────
@wb.route("/api/v1/workbench/gs1", methods=["POST"])
def wb_gs1():
    b = jbody()
    raw = b.get("raw","").strip()
    if not raw: return err("Chybi 'raw'")
    return ok({"gs1": parse_gs1(raw)})

# ── RFID dump ────────────────────────────────────────────────────────────────
@wb.route("/api/v1/workbench/rfid", methods=["POST"])
def wb_rfid():
    b = jbody()
    raw = b.get("raw","").strip()
    if not raw: return err("Chybi 'raw' (hex dump)")
    return ok({"rfid": parse_rfid_dump(raw)})

# ── Entropy ───────────────────────────────────────────────────────────────────
@wb.route("/api/v1/workbench/entropy", methods=["POST"])
def wb_entropy():
    b = jbody()
    raw = b.get("raw","").strip()
    if not raw: return err("Chybi 'raw'")
    return ok({"entropy": analyze_entropy(raw)})

# ── JWT inspector ─────────────────────────────────────────────────────────────
@wb.route("/api/v1/workbench/jwt", methods=["POST"])
def wb_jwt():
    b = jbody()
    raw = b.get("raw","").strip()
    if not raw: return err("Chybi 'raw'")
    return ok({"jwt": inspect_jwt(raw)})

# ── Credential scanner ────────────────────────────────────────────────────────
@wb.route("/api/v1/workbench/credentials", methods=["POST"])
def wb_credentials():
    b = jbody()
    text = b.get("text", b.get("raw",""))
    if not text: return err("Chybi 'text'")
    return ok({"scan": scan_credentials(text)})

# ── Comparison ────────────────────────────────────────────────────────────────
@wb.route("/api/v1/workbench/compare", methods=["POST"])
def wb_compare():
    b = jbody()
    a, bv = b.get("a","").strip(), b.get("b","").strip()
    if not a or not bv: return err("Chybi 'a' a 'b'")
    return ok({"comparison": compare_identifiers(a, bv)})
