
from flask import jsonify, request
from flask_jwt_extended import create_access_token
from sqlalchemy import func
from werkzeug.security import check_password_hash

from app.api import api_bp
from app.models import User


@api_bp.post("/auth/token")
def create_token():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "JSON object is required"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "error": "Email and password are required"
        }), 400

    email = email.strip().lower()

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    user = User.query.filter(
        func.lower(User.EMAIL) == email
    ).first()

    if (
        user is None
        or not user.PASSWORD_HASH
        or not check_password_hash(user.PASSWORD_HASH, password)
        or user.TRANGTHAIND != 1
    ):
        return jsonify({
            "error": "Invalid credentials"
        }), 401

    access_token = create_access_token(
        identity=str(user.MANGUOIDUNG)
    )

    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 1800,
        "user": {
            "id": user.MANGUOIDUNG,
            "name": user.HOTEN,
            "role": (user.ROLE or "").strip().lower()
        }
    }), 200
