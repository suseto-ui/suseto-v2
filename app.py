import sys
import os
import logging
from flask import Flask, render_template

logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__)

    # Import Blueprintů
    from routes.core_routes import core_bp
    from routes.timeline_routes import timeline_bp

    # Registrace Blueprintů
    app.register_blueprint(core_bp)
    app.register_blueprint(timeline_bp)

    @app.route("/")
    def home():
        return render_template("pages/rozcestnik.html")
    
    @app.route("/navigator")
    def navigator():
        return render_template("pages/navigator.html")
        
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('pages/rozcestnik.html', error_message="Stránka nenalezena (404)."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('pages/rozcestnik.html', error_message="Interní chyba serveru (500)."), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)