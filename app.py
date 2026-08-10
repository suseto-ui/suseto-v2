import os
from flask import Flask, render_template
from routes.core_routes import core_bp
from routes.admin_routes import admin_bp
from routes.timeline_routes import timeline_bp
from services.config import CONFIG
from services.database import db

app = Flask(__name__)
app.secret_key = CONFIG["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = CONFIG.get("DATABASE_URI", "sqlite:///suseto.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializace databáze
db.init_app(app)

# Registrace Blueprintů
app.register_blueprint(core_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(timeline_bp)

# Globální Error Handlery
@app.errorhandler(404)
def page_not_found(e):
    return render_template('pages/rozcestnik.html', error_message="Stránka nenalezena (404)."), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('pages/rozcestnik.html', error_message="Interní chyba serveru (500)."), 500

# Vytvoření tabulek pokud neexistují
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)