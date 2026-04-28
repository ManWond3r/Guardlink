# sites.py
# This file handles all site-related API routes
# A site is a physical location being guarded
# Each site belongs to one client

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Site, Client

sites_bp = Blueprint("sites", __name__)


@sites_bp.route("/api/sites", methods=["GET"])
@jwt_required()
def get_sites():
    # Return all sites with the client name included
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    sites = Site.query.order_by(Site.created_at.desc()).all()

    result = []
    for site in sites:
        # Get the client name for this site
        client = Client.query.get(site.client_id)
        result.append({
            "id": site.id,
            "name": site.name,
            "location": site.location,
            "client_id": site.client_id,
            "client_name": client.name if client else None,
            "created_at": site.created_at.isoformat()
        })

    return jsonify(result), 200


@sites_bp.route("/api/sites", methods=["POST"])
@jwt_required()
def add_site():
    # Only admin can add a new site
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()

    # Check all required fields are present
    if not data.get("name") or not data.get("location") or not data.get("client_id"):
        return jsonify({"error": "Name, location and client are required"}), 400

    # Make sure the client actually exists before linking to it
    client = Client.query.get(data["client_id"])
    if not client:
        return jsonify({"error": "Client not found"}), 404

    # Create and save the new site
    site = Site(
        name=data["name"],
        location=data["location"],
        client_id=data["client_id"]
    )
    db.session.add(site)
    db.session.commit()

    return jsonify({"message": "Site added successfully", "id": site.id}), 201

@sites_bp.route("/api/sites/<site_id>", methods=["DELETE"])
@jwt_required()
def delete_site(site_id):
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    site = Site.query.get(site_id)
    if not site:
        return jsonify({"error": "Site not found"}), 404

    db.session.delete(site)
    db.session.commit()
    return jsonify({"message": "Site deleted successfully"}), 200


@sites_bp.route("/api/sites/<site_id>/edit", methods=["PUT"])
@jwt_required()
def edit_site(site_id):
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    site = Site.query.get(site_id)
    if not site:
        return jsonify({"error": "Site not found"}), 404

    data = request.get_json()
    if data.get("name"):
        site.name = data["name"]
    if data.get("location"):
        site.location = data["location"]
    if data.get("client_id"):
        client = Client.query.get(data["client_id"])
        if not client:
            return jsonify({"error": "Client not found"}), 404
        site.client_id = data["client_id"]

    db.session.commit()
    return jsonify({"message": "Site updated successfully"}), 200

@sites_bp.route("/api/sites/my-site", methods=["GET"])
@jwt_required()
def get_my_site():
    # This route is for clients to see their site and which guard is on duty
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "client":
        return jsonify({"error": "Client access required"}), 403

    # Find the client record matching the logged in user's email
    from models import Client
    client = Client.query.filter_by(email=current_user["email"]).first()
    if not client:
        return jsonify({"error": "Client not found"}), 404

    # Get all sites belonging to this client
    sites = Site.query.filter_by(client_id=client.id).all()
    if not sites:
        return jsonify([]), 200

    result = []
    for site in sites:
        # Get guards assigned to this site
        from models import Guard
        guards = Guard.query.filter_by(site_id=site.id).all()
        guards_list = []
        for guard in guards:
            guards_list.append({
                "id": guard.id,
                "full_name": guard.full_name,
                "shift": guard.shift,
                "phone": guard.phone
            })
        result.append({
            "id": site.id,
            "name": site.name,
            "location": site.location,
            "guards": guards_list
        })

    return jsonify(result), 200
    