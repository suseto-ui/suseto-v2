from flask import Flask
from services.config import get_config
from routes.core_routes import core_bp

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(get_config())
app.secret_key = app.config['SECRET_KEY']
app.register_blueprint(core_bp)

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False))
