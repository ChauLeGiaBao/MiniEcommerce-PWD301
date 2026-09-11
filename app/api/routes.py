from flask import jsonify
from app.api import api_bp


@api_bp.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "API is running"
    })