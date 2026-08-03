"""
Centralni log chyb pro Suseto.
Pouziti v app.py:
    from services.error_logger import setup_logging
    setup_logging(app)
"""
import logging
import logging.handlers
import os
from flask import request

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
LOG_FILE = os.path.join(LOG_DIR, 'suseto_errors.log')


def setup_logging(app):
    """Nastav rotating file logger a Flask error handlery."""
    os.makedirs(LOG_DIR, exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=2*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    if not any(isinstance(h, logging.handlers.RotatingFileHandler) for h in root.handlers):
        root.addHandler(file_handler)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        app.logger.error(
            "Unhandled exception: %s %s -> %s",
            request.method, request.path, str(e),
            exc_info=True
        )
        return {'error': 'Interni chyba serveru.', 'detail': str(e)}, 500

    @app.errorhandler(404)
    def handle_404(e):
        app.logger.info("404: %s %s", request.method, request.path)
        return {'error': 'Endpoint nenalezen.'}, 404

    @app.errorhandler(405)
    def handle_405(e):
        app.logger.info("405: %s %s", request.method, request.path)
        return {'error': 'Metoda neni povolena.'}, 405

    app.logger.info("Suseto logging initialized. Log: %s", LOG_FILE)


def log_request_error(logger, endpoint: str, error: Exception, payload=None):
    """Helper pro manualni logovani chyb v endpointech."""
    logger.error(
        "Endpoint error [%s] payload=%r: %s",
        endpoint,
        str(payload)[:120] if payload else None,
        str(error),
        exc_info=True
    )


def get_recent_errors(n=50):
    """Vrati poslednich n radku z error logu (pro /debug endpoint)."""
    try:
        if not os.path.exists(LOG_FILE):
            return []
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return [l.rstrip() for l in lines[-n:]]
    except Exception:
        return []
