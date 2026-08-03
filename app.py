from flask import Flask, Blueprint, jsonify, render_template, request, redirect, url_for
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

core_bp = Blueprint("core", __name__)

@core_bp.route("/")
def home():
    return render_template("pages/home.html")

@core_bp.route("/health")
def health():
    return jsonify({"status": "ok"})

@core_bp.route("/api/v1/system-status")
def system_status():
    return jsonify({"status": "ok", "user": "anonymous"})

@core_bp.route("/api/v1/analyze", methods=["POST"])
def analyze():
    payload = request.get_json(silent=True) or {}
    return jsonify({"ok": True, "payload": payload})

@core_bp.route("/label-print/<item_id>")
def label_print(item_id):
    return render_template("pages/label_print.html", item={"id": item_id})

app.register_blueprint(core_bp)

@app.errorhandler(404)
def not_found(e):
    return render_template("pages/404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("pages/500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)
