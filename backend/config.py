# config.py
# This file holds all the settings for our application
# We read sensitive values from a .env file so they are not hardcoded

import os
from dotenv import load_dotenv

# Load the .env file so we can read the variables inside it
load_dotenv()

class Config:
    # Secret key used to sign JWT tokens - keep this private
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "guardlink-secret-key-change-this")
    
    # Database connection string - tells SQLAlchemy how to connect to PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/guardlink")
    
    # This turns off a feature we don't need - it just reduces memory usage
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # How long a JWT token lasts before the user has to log in again (1 day)
    JWT_ACCESS_TOKEN_EXPIRES = 86400
    