# auth.py
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Store user info as a JSON string inside the token
    token = create_access_token(
        identity=json.dumps({"id": user.id, "role": user.role, "email": user.email})
    )

    return jsonify({
        "token": token,
        "role": user.role,
        "full_name": user.full_name
    }), 200


@auth_bp.route("/api/me", methods=["GET"])
@jwt_required()
def me():
    current_user = json.loads(get_jwt_identity())
    return jsonify(current_user), 200