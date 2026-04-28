# invoices.py
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Invoice, Client
from utils.email import send_invoice_email

invoices_bp = Blueprint("invoices", __name__)


@invoices_bp.route("/api/invoices", methods=["GET"])
@jwt_required()
def get_invoices():
    current_user = json.loads(get_jwt_identity())

    if current_user["role"] == "admin":
        invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    else:
        client = Client.query.filter_by(email=current_user["email"]).first()
        if not client:
            return jsonify([]), 200
        invoices = Invoice.query.filter_by(client_id=client.id).order_by(Invoice.created_at.desc()).all()

    result = []
    for invoice in invoices:
        client = Client.query.get(invoice.client_id)
        result.append({
            "id": invoice.id,
            "client_id": invoice.client_id,
            "client_name": client.name if client else None,
            "month": invoice.month,
            "amount": invoice.amount,
            "status": invoice.status,
            "created_at": invoice.created_at.isoformat()
        })

    return jsonify(result), 200


@invoices_bp.route("/api/invoices", methods=["POST"])
@jwt_required()
def add_invoice():
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()

    if not data.get("client_id") or not data.get("month") or not data.get("amount"):
        return jsonify({"error": "Client, month and amount are required"}), 400

    client = Client.query.get(data["client_id"])
    if not client:
        return jsonify({"error": "Client not found"}), 404

    invoice = Invoice(
        client_id=data["client_id"],
        month=data["month"],
        amount=float(data["amount"]),
        status=data.get("status", "unpaid")
    )
    db.session.add(invoice)
    db.session.commit()

    try:
        from datetime import datetime
        month_formatted = datetime.strptime(data["month"], "%Y-%m").strftime("%B %Y")
    except:
        month_formatted = data["month"]

    send_invoice_email(
        client_name=client.name,
        client_email=client.email,
        month=month_formatted,
        amount=data["amount"],
        status=invoice.status
    )

    return jsonify({"message": "Invoice created successfully", "id": invoice.id}), 201


@invoices_bp.route("/api/invoices/<invoice_id>", methods=["PATCH"])
@jwt_required()
def update_invoice(invoice_id):
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404

    data = request.get_json()
    if "status" in data:
        invoice.status = data["status"]

    db.session.commit()
    return jsonify({"message": "Invoice updated successfully"}), 200

@invoices_bp.route("/api/invoices/<invoice_id>", methods=["DELETE"])
@jwt_required()
def delete_invoice(invoice_id):
    current_user = json.loads(get_jwt_identity())
    if current_user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404

    db.session.delete(invoice)
    db.session.commit()
    return jsonify({"message": "Invoice deleted successfully"}), 200