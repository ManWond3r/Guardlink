# models.py
# This file defines what our database tables look like
# Each class here becomes one table in the database
# SQLAlchemy reads these classes and creates the actual tables for us

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

# This is the database object we will use everywhere in the app
db = SQLAlchemy()

# Helper function to generate a unique ID for each record
def generate_uuid():
    return str(uuid.uuid4())


class User(db.Model):
    # This table stores login information for both admins and clients
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)  # either 'admin' or 'client'
    full_name = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Client(db.Model):
    # Stores details of each client (companies that pay for security)
    __tablename__ = "clients"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String)
    address = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # This links clients to their invoices and complaints
    invoices = db.relationship("Invoice", backref="client", lazy=True)
    complaints = db.relationship("Complaint", backref="client", lazy=True)


class Site(db.Model):
    # A site is a physical location being guarded
    __tablename__ = "sites"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    client_id = db.Column(db.String, db.ForeignKey("clients.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Links site to its guards and incidents
    guards = db.relationship("Guard", backref="site", lazy=True)
    incidents = db.relationship("Incident", backref="site", lazy=True)


class Guard(db.Model):
    # Stores information about each security guard
    __tablename__ = "guards"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    full_name = db.Column(db.String, nullable=False)
    id_number = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String)
    shift = db.Column(db.String)  # 'day' or 'night'
    site_id = db.Column(db.String, db.ForeignKey("sites.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Links guard to their attendance records
    attendance = db.relationship("Attendance", backref="guard", lazy=True)


class Attendance(db.Model):
    # Records whether a guard showed up on a given day
    __tablename__ = "attendance"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    guard_id = db.Column(db.String, db.ForeignKey("guards.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    arrived = db.Column(db.Boolean, default=False)
    noted_by = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Incident(db.Model):
    # Records security incidents - replaces the paper Occurrence Book
    __tablename__ = "incidents"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    site_id = db.Column(db.String, db.ForeignKey("sites.id"), nullable=False)
    guard_id = db.Column(db.String, db.ForeignKey("guards.id"), nullable=True)
    description = db.Column(db.Text, nullable=False)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)


class Invoice(db.Model):
    # Monthly invoices generated for each client
    __tablename__ = "invoices"

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    client_id = db.Column(db.String, db.ForeignKey("clients.id"), nullable=False)
    month = db.Column(db.String, nullable=False)  # format: YYYY-MM
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, default="unpaid")  # 'unpaid' or 'paid'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Complaint(db.Model):
    __tablename__ = "complaints"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    client_id = db.Column(db.String, db.ForeignKey("clients.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String, default="open")
    reply = db.Column(db.Text, nullable=True)  # admin's reply
    created_at = db.Column(db.DateTime, default=datetime.utcnow)