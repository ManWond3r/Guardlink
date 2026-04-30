# attendance.py
# This file handles attendance tracking
# Admin can mark each guard as present or absent for today

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Attendance, Guard, Site
from datetime import date

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/api/attendance", methods=["GET"])
@jwt_required()
def get_attendance():
    # Return all guards with their attendance status for today
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    today = date.today()

    # Get all guards
    guards = Guard.query.order_by(Guard.full_name).all()

    # Get today's attendance records
    today_records = Attendance.query.filter_by(date=today).all()

    # Put attendance records in a dictionary for quick lookup by guard_id
    attendance_map = {}
    for record in today_records:
        attendance_map[record.guard_id] = record

    result = []
    for guard in guards:
        # Get the site name if the guard is assigned to one
        site_name = None
        if guard.site_id:
            site = Site.query.get(guard.site_id)
            if site:
                site_name = site.name

        # Check if this guard has an attendance record for today
        record = attendance_map.get(guard.id)

        result.append({
            "guard_id": guard.id,
            "full_name": guard.full_name,
            "shift": guard.shift,
            "site_name": site_name,
            "attendance_id": record.id if record else None,
            "arrived": record.arrived if record else None,
            "date": str(today)
        })

    return jsonify(result), 200


@attendance_bp.route("/api/attendance", methods=["POST"])
@jwt_required()
def mark_attendance():
    # Mark a guard as present or absent for today
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()

    if not data.get("guard_id") or data.get("arrived") is None:
        return jsonify({"error": "Guard ID and arrived status are required"}), 400

    today = date.today()

    # Check if there is already an attendance record for this guard today
    existing = Attendance.query.filter_by(
        guard_id=data["guard_id"],
        date=today
    ).first()

    if existing:
        # If a record already exists just update it
        existing.arrived = data["arrived"]
        db.session.commit()
        return jsonify({"message": "Attendance updated"}), 200
    else:
        # Otherwise create a new record
        record = Attendance(
            guard_id=data["guard_id"],
            date=today,
            arrived=data["arrived"],
            noted_by="Admin"
        )
        db.session.add(record)
        db.session.commit()
        return jsonify({"message": "Attendance marked"}), 201