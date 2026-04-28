# incidents.py
# This file handles incident reporting
# This replaces the paper Occurrence Book (OB)
# Admin can log incidents and view all past incidents

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Incident, Site, Guard

incidents_bp = Blueprint("incidents", __name__)


@incidents_bp.route("/api/incidents", methods=["GET"])
@jwt_required()
def get_incidents():
    # Return all incidents with site and guard names included
    current_user =json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    incidents = Incident.query.order_by(Incident.reported_at.desc()).all()

    result = []
    for incident in incidents:
        # Get the site name
        site = Site.query.get(incident.site_id)

        # Get the guard name if one was linked to this incident
        guard = None
        if incident.guard_id:
            guard = Guard.query.get(incident.guard_id)

        result.append({
            "id": incident.id,
            "site_id": incident.site_id,
            "site_name": site.name if site else None,
            "guard_id": incident.guard_id,
            "guard_name": guard.full_name if guard else None,
            "description": incident.description,
            "reported_at": incident.reported_at.isoformat()
        })

    return jsonify(result), 200


@incidents_bp.route("/api/incidents", methods=["POST"])
@jwt_required()
def add_incident():
    # Log a new incident
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()

    # Site and description are required, guard is optional
    if not data.get("site_id") or not data.get("description"):
        return jsonify({"error": "Site and description are required"}), 400

    # Make sure the site exists
    site = Site.query.get(data["site_id"])
    if not site:
        return jsonify({"error": "Site not found"}), 404

    incident = Incident(
        site_id=data["site_id"],
        guard_id=data.get("guard_id") or None,
        description=data["description"]
    )
    db.session.add(incident)
    db.session.commit()

    return jsonify({"message": "Incident logged successfully", "id": incident.id}), 201

@incidents_bp.route("/api/incidents/<incident_id>", methods=["DELETE"])
@jwt_required()
def delete_incident(incident_id):
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    incident = Incident.query.get(incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    db.session.delete(incident)
    db.session.commit()
    return jsonify({"message": "Incident deleted successfully"}), 200