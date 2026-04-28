# roster.py
# This file handles the duty roster
# The duty roster shows which guard is assigned to which site
# Admin can reassign guards from this page

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Guard, Site

roster_bp = Blueprint("roster", __name__)


@roster_bp.route("/api/roster", methods=["GET"])
@jwt_required()
def get_roster():
    # Return all guards with their current site assignment
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    guards = Guard.query.order_by(Guard.full_name).all()
    sites = Site.query.order_by(Site.name).all()

    # Build the guards list with site names
    guards_list = []
    for guard in guards:
        site_name = None
        if guard.site_id:
            site = Site.query.get(guard.site_id)
            if site:
                site_name = site.name

        guards_list.append({
            "id": guard.id,
            "full_name": guard.full_name,
            "shift": guard.shift,
            "site_id": guard.site_id,
            "site_name": site_name
        })

    # Also return all sites so the frontend can show them in the dropdown
    sites_list = []
    for site in sites:
        from models import Client
        client = Client.query.get(site.client_id)
        sites_list.append({
            "id": site.id,
            "name": site.name,
            "location": site.location,
            "client_name": client.name if client else None
        })

    return jsonify({
        "guards": guards_list,
        "sites": sites_list
    }), 200


@roster_bp.route("/api/roster/<guard_id>", methods=["PATCH"])
@jwt_required()
def assign_guard(guard_id):
    # Assign a guard to a different site
    current_user =json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    guard = Guard.query.get(guard_id)
    if not guard:
        return jsonify({"error": "Guard not found"}), 404

    data = request.get_json()

    # site_id can be empty string or null to unassign the guard
    site_id = data.get("site_id")
    guard.site_id = site_id if site_id else None

    db.session.commit()
    return jsonify({"message": "Guard assigned successfully"}), 200