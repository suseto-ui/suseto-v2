import sys
import os
import logging
from flask import Flask, jsonify, render_template, request, session, Response
from routes.helpers import current_user, require_role, body

# Registrace Blueprintů
from routes.auth_routes import auth_bp
from routes.aidc_routes import aidc_bp
from routes.admin_routes import admin_bp
from routes.registry_routes import registry_bp
from routes.timeline_routes import timeline_bp
from routes.debug_routes import debug_bp
from routes.core_routes import core_bp

from services.config import CONFIG
from services.database import db

from services.audit_service import write as audit_write
from services.auth_service import verify

logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.secret_key = CONFIG["SECRET_KEY"]

    # Konfigurace Flask-SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = CONFIG.get("DATABASE_URI", "sqlite:///suseto.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    # Registrace Blueprintů - TYHLE OBSLUHUJÍ VŠECHNU LOGIKU
    app.register_blueprint(auth_bp)
    app.register_blueprint(aidc_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(registry_bp)
    app.register_blueprint(timeline_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(core_bp)

    # Zaregistrování Workbench přes specifickou funkci
    from services.workbench_routes import register_workbench
    register_workbench(app)

    # Globální Error Handlery
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('pages/rozcestnik.html', error_message="Stránka nenalezena (404)."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('pages/rozcestnik.html', error_message="Interní chyba serveru (500)."), 500

    # TYTO OBÁLKOVÉ ROUTY SMAZÁNY! 
    # Všechna logika typu /aidc-studio, /decode-lab, /generator teď proudí čistě
    # do tvých Blueprintů v routes/* a ty obsluhují renderování správných šablon s daty.

    # Ponecháme pouze rozcestník, který zřejmě žádný blueprint nemá a je základem aplikace.
    @app.route("/")
    def home():
        return render_template("pages/rozcestnik.html")

    @app.route("/login")
    def login_page():
        return render_template(
            "pages/login.html",
            admin_username=CONFIG.get("ADMIN_USERNAME"),
            admin_password=CONFIG.get("DEFAULT_ADMIN_PASSWORD"),
        )
        
    @app.get("/api/v1/auth/me")
    def auth_me():
        return jsonify({"user": current_user()})

    @app.post("/api/v1/auth/login")
    def auth_login():
        data = body()
        user = verify(data.get("username"), data.get("password"))
        if not user:
            return jsonify({"error": "Neplatné přihlášení."}), 401
        
        session["username"] = user["username"]
        session["role"] = user["role"]
        audit_write("login", user["username"], user["role"])
        
        return jsonify({"user": user})

    @app.post("/api/v1/auth/logout")
    def auth_logout():
        audit_write("logout", session.get("username", "anonymous"), "")
        session.clear()
        return jsonify({"ok": True})

    # Vytvoření DB tabulek
    with app.app_context():
        db.create_all()

    return app

app = create_app()
application = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)