from flask import Blueprint, jsonify, request, render_template
from routes.helpers import current_user, body

core_bp = Blueprint("core", __name__)


<<<<<<< HEAD
@core_bp.get('/health')
=======
@core_bp.get("/health")
>>>>>>> 78f6633 (fix(lint): E401 multi-imports, E722 bare except, E302 blank lines, aidc_core typo [S105])
def health():
    return jsonify({"status": "ok", "mode": "sandbox-only"})


<<<<<<< HEAD
@core_bp.get('/api/v1/system-status')
=======
@core_bp.get("/api/v1/system-status")
>>>>>>> 78f6633 (fix(lint): E401 multi-imports, E722 bare except, E302 blank lines, aidc_core typo [S105])
def api_system_status():
    return jsonify({"user": current_user()})


<<<<<<< HEAD
@core_bp.post('/api/v1/analyze')
=======
@core_bp.post("/api/v1/analyze")
>>>>>>> 78f6633 (fix(lint): E401 multi-imports, E722 bare except, E302 blank lines, aidc_core typo [S105])
def api_analyze():
    d = body()
    return jsonify(
        {"ok": True, "payload": d.get("payload") or request.form.get("payload", "")}
    )


<<<<<<< HEAD
@core_bp.route('/label-print/<item_id>')
=======
@core_bp.route("/label-print/<item_id>")
>>>>>>> 78f6633 (fix(lint): E401 multi-imports, E722 bare except, E302 blank lines, aidc_core typo [S105])
def label_print(item_id):
    return render_template("pages/label_print.html", item={"id": item_id})
