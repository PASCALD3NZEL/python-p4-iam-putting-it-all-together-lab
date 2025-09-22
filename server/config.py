import os
from flask_sqlalchemy import SQLAlchemy

# Create the database instance (initialized later in app.py)
db = SQLAlchemy()

class Config:
    # Use DATABASE_URL from env if provided, else fallback to SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
