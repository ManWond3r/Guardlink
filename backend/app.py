# app.py
# This is the main file that starts our Flask server
# It connects everything together - the database, the routes, and the settings

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db, User
from werkzeug.security import generate_password_hash
import os

# Import all our route blueprints
from routes.auth import auth_bp
from routes.guards import guards_bp
from routes.clients import clients_bp
from routes.sites import sites_bp
from routes.roster import roster_bp
from routes.attendance import attendance_bp
from routes.incidents import incidents_bp
from routes.invoices import invoices_bp
from routes.complaints import complaints_bp



def create_app():
    # Create the Flask application
    app = Flask(__name__)

    # Load settings from config.py
    app.config.from_object(Config)

    # Enable CORS so our frontend can talk to this backend
    # Without this the browser would block all requests
    CORS(app, origins="*")

    # Set up the database with our app
    db.init_app(app)

    # Set up JWT authentication
    JWTManager(app)

    # Register all our route blueprints
    # Each blueprint handles a different part of the system
    app.register_blueprint(auth_bp)
    app.register_blueprint(guards_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(sites_bp)
    app.register_blueprint(roster_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(complaints_bp)

    # Create all database tables if they don't exist yet
    with app.app_context():
        db.create_all()

        # Create the admin user if one doesn't exist yet
        # This runs every time the server starts but only creates the admin once
        create_admin()

    return app


def create_admin():
    # Check if an admin user already exists
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        # Create the default admin account
        # You should change this password after first login
        admin = User(
            email=os.getenv("ADMIN_EMAIL", "admin@guardlink.com"),
            password_hash=generate_password_hash(
                os.getenv("ADMIN_PASSWORD", "admin123")
            ),
            role="admin",
            full_name="Admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully")


# This runs the server when you execute: python app.py
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)