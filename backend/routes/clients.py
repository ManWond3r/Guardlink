# clients.py
# This file handles all client-related API routes
# Admin can add clients and view all clients

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Client

clients_bp = Blueprint("clients", __name__)


@clients_bp.route("/api/clients", methods=["GET"])
@jwt_required()
def get_clients():
    # Return a list of all clients
    # Only admin should be able to see all clients
    current_user =json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    clients = Client.query.order_by(Client.created_at.desc()).all()

    result = []
    for client in clients:
        result.append({
            "id": client.id,
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "address": client.address,
            "created_at": client.created_at.isoformat()
        })

    return jsonify(result), 200


@clients_bp.route("/api/clients", methods=["POST"])
@jwt_required()
def add_client():
    # Only admin can add a new client
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()

    # Check required fields
    if not data.get("name") or not data.get("email"):
        return jsonify({"error": "Name and email are required"}), 400

    # Check if a client with this email already exists
    existing = Client.query.filter_by(email=data["email"]).first()
    if existing:
        return jsonify({"error": "A client with this email already exists"}), 400

    # Create and save the new client
    client = Client(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        address=data.get("address")
    )
    db.session.add(client)
    db.session.commit()

    return jsonify({"message": "Client added successfully", "id": client.id}), 201

@clients_bp.route("/api/clients/<client_id>", methods=["DELETE"])
@jwt_required()
def delete_client(client_id):
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Client deleted successfully"}), 200


@clients_bp.route("/api/clients/<client_id>/edit", methods=["PUT"])
@jwt_required()
def edit_client(client_id):
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    data = request.get_json()
    if data.get("name"):
        client.name = data["name"]
    if data.get("email"):
        if data["email"] != client.email:
            existing = Client.query.filter_by(email=data["email"]).first()
            if existing:
                return jsonify({"error": "A client with this email already exists"}), 400
        client.email = data["email"]
    if data.get("phone") is not None:
        client.phone = data["phone"]
    if data.get("address") is not None:
        client.address = data["address"]

    db.session.commit()
    return jsonify({"message": "Client updated successfully"}), 200