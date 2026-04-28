# guards.py
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Guard, Site

guards_bp = Blueprint("guards", __name__)


@guards_bp.route("/api/guards", methods=["GET"])
@jwt_required()
def get_guards():
    guards = Guard.query.order_by(Guard.created_at.desc()).all()
    result = []
    for guard in guards:
        site_name = None
        if guard.site_id:
            site = Site.query.get(guard.site_id)
            if site:
                site_name = site.name
        result.append({
            "id": guard.id,
            "full_name": guard.full_name,
            "id_number": guard.id_number,
            "phone": guard.phone,
            "shift": guard.shift,
            "site_id": guard.site_id,
            "site_name": site_name,
            "created_at": guard.created_at.isoformat()
        })
    return jsonify(result), 200


@guards_bp.route("/api/guards", methods=["POST"])
@jwt_required()
def add_guard():
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()
    if not data.get("full_name") or not data.get("id_number"):
        return jsonify({"error": "Full name and ID number are required"}), 400

    existing = Guard.query.filter_by(id_number=data["id_number"]).first()
    if existing:
        return jsonify({"error": "A guard with this ID number already exists"}), 400

    guard = Guard(
        full_name=data["full_name"],
        id_number=data["id_number"],
        phone=data.get("phone"),
        shift=data.get("shift", "day")
    )
    db.session.add(guard)
    db.session.commit()
    return jsonify({"message": "Guard added successfully", "id": guard.id}), 201


@guards_bp.route("/api/guards/<guard_id>", methods=["PATCH"])
@jwt_required()
def update_guard(guard_id):
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    guard = Guard.query.get(guard_id)
    if not guard:
        return jsonify({"error": "Guard not found"}), 404

    data = request.get_json()
    if "site_id" in data:
        guard.site_id = data["site_id"] if data["site_id"] else None
    if "shift" in data:
        guard.shift = data["shift"]

    db.session.commit()
    return jsonify({"message": "Guard updated successfully"}), 200

@guards_bp.route("/api/guards/<guard_id>", methods=["DELETE"])
@jwt_required()
def delete_guard(guard_id):
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    guard = Guard.query.get(guard_id)
    if not guard:
        return jsonify({"error": "Guard not found"}), 404

    db.session.delete(guard)
    db.session.commit()
    return jsonify({"message": "Guard deleted successfully"}), 200


@guards_bp.route("/api/guards/<guard_id>/edit", methods=["PUT"])
@jwt_required()
def edit_guard(guard_id):
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    guard = Guard.query.get(guard_id)
    if not guard:
        return jsonify({"error": "Guard not found"}), 404

    data = request.get_json()
    if data.get("full_name"):
        guard.full_name = data["full_name"]
    if data.get("id_number"):
        # Check duplicate only if id_number changed
        if data["id_number"] != guard.id_number:
            existing = Guard.query.filter_by(id_number=data["id_number"]).first()
            if existing:
                return jsonify({"error": "A guard with this ID number already exists"}), 400
        guard.id_number = data["id_number"]
    if data.get("phone") is not None:
        guard.phone = data["phone"]
    if data.get("shift"):
        guard.shift = data["shift"]

    db.session.commit()
    return jsonify({"message": "Guard updated successfully"}), 200