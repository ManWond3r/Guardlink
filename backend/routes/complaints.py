# complaints.py
# This file handles complaints submitted by clients
# When a client submits a complaint, the admin gets an email notification
# Admin can view all complaints and mark them as resolved

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Complaint, Client
from utils.email import send_complaint_email
import os

complaints_bp = Blueprint("complaints", __name__)


@complaints_bp.route("/api/complaints", methods=["GET"])
@jwt_required()
def get_complaints():
    # Admin sees all complaints, client sees only their own
    current_user = json.loads(get_jwt_identity())

    if current_user["role"] == "admin":
        # Admin gets all complaints
        complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    else:
        # Client gets only their own complaints
        client = Client.query.filter_by(email=current_user["email"]).first()
        if not client:
            return jsonify([]), 200
        complaints = Complaint.query.filter_by(
            client_id=client.id
        ).order_by(Complaint.created_at.desc()).all()

    result = []
    for complaint in complaints:
        client = Client.query.get(complaint.client_id)
        result.append({
            "id": complaint.id,
            "client_id": complaint.client_id,
            "client_name": client.name if client else None,
            "message": complaint.message,
            "status": complaint.status,
            "reply": complaint.reply,
            "created_at": complaint.created_at.isoformat()
        })

    return jsonify(result), 200


@complaints_bp.route("/api/complaints", methods=["POST"])
@jwt_required()
def add_complaint():
    # Only clients can submit complaints
    current_user =json.loads(get_jwt_identity())
    if current_user["role"] != "client":
        return jsonify({"error": "Client access required"}), 403

    data = request.get_json()

    if not data.get("message"):
        return jsonify({"error": "Message is required"}), 400

    # Find the client record that matches the logged in user's email
    client = Client.query.filter_by(email=current_user["email"]).first()
    if not client:
        return jsonify({"error": "Client record not found"}), 404

    # Save the complaint
    complaint = Complaint(
        client_id=client.id,
        message=data["message"]
    )
    db.session.add(complaint)
    db.session.commit()

    # Send email notification to admin
    admin_email = os.getenv("ADMIN_EMAIL")
    if admin_email:
        send_complaint_email(
            admin_email=admin_email,
            client_name=client.name,
            client_email=client.email,
            message=data["message"]
        )

    return jsonify({"message": "Complaint submitted successfully"}), 201


@complaints_bp.route("/api/complaints/<complaint_id>", methods=["PATCH"])
@jwt_required()
def update_complaint(complaint_id):
    # Only admin can update complaint status
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404

    data = request.get_json()
    if "status" in data:
        complaint.status = data["status"]

    db.session.commit()
    return jsonify({"message": "Complaint updated successfully"}), 200

@complaints_bp.route("/api/complaints/<complaint_id>", methods=["DELETE"])
@jwt_required()
def delete_complaint(complaint_id):
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404

    db.session.delete(complaint)
    db.session.commit()
    return jsonify({"message": "Complaint deleted successfully"}), 200


@complaints_bp.route("/api/complaints/<complaint_id>/reply", methods=["POST"])
@jwt_required()
def reply_complaint(complaint_id):
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404

    data = request.get_json()
    if not data.get("reply"):
        return jsonify({"error": "Reply message is required"}), 400

    # Get client details to send email
    client = Client.query.get(complaint.client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    # Send reply email to client
    from utils.email import send_email
    subject = f"Re: Your Complaint | GuardLink Security"
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #1B2E24; color: #ffffff; border-radius: 8px; overflow: hidden;">
        <div style="background: #2D6A4F; padding: 32px 40px; border-bottom: 2px solid #52B788;">
            <h1 style="margin: 0; font-size: 28px; color: #ffffff;">Guard<span style="color: #D4A017;">Link</span></h1>
            <p style="color: #52B788; font-size: 12px; letter-spacing: 2px; margin: 4px 0 0;">Complaint Response</p>
        </div>
        <div style="padding: 40px;">
            <p style="color: #52B788;">Dear {client.name},</p>
            <p style="color: #ccc; margin: 16px 0;">Thank you for reaching out to us. Here is our response to your complaint:</p>
            <div style="background: #243d2e; border: 1px solid #2D6A4F; border-radius: 6px; padding: 20px; margin: 20px 0;">
                <p style="color: #aaa; font-size: 12px; margin-bottom: 8px;">YOUR COMPLAINT:</p>
                <p style="color: #ccc; font-style: italic;">"{complaint.message}"</p>
            </div>
            <div style="background: #243d2e; border: 1px solid #52B788; border-radius: 6px; padding: 20px; margin: 20px 0;">
                <p style="color: #52B788; font-size: 12px; margin-bottom: 8px;">OUR RESPONSE:</p>
                <p style="color: #fff;">{data["reply"]}</p>
            </div>
            <p style="color: #888; margin-top: 24px;">If you have any further concerns, please don't hesitate to contact us.</p>
        </div>
        <div style="background: #2D6A4F; padding: 20px 40px; text-align: center;">
            <p style="color: #52B788; font-size: 11px; letter-spacing: 2px; margin: 0;">GUARDLINK SECURITY · NAIROBI, KENYA</p>
        </div>
    </div>
    """
    send_email(client.email, subject, html_body)

    # Save the reply and mark as resolved
    complaint.reply = data["reply"]
    complaint.status = "resolved"
    db.session.commit()

    return jsonify({"message": "Reply sent successfully"}), 200