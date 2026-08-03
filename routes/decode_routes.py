# routes/decode_routes.py
# Blueprint pro /api/v1/decode/*

from flask import Blueprint, jsonify
from routes.helpers import current_user, body
from services.decode_service import chain as decode_chain, pattern_library

decode_bp = Blueprint("decode", __name__, url_prefix="/api/v1/decode")


@decode_bp.post("/chain")
def api_decode_chain():
    if not current_user():
        return jsonify({"error": "Přihlas se."}), 401
    return jsonify(decode_chain(body().get("payload", "")))


@decode_bp.post("/library")
def api_decode_library():
    if not current_user():
        return jsonify({"error": "Přihlas se."}), 401
    return jsonify(pattern_library(body().get("payloads", [])))
