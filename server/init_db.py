#!/usr/bin/env python3

import sys
import os

# Add the server directory to the path so we can import from app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Recipe

with app.app_context():
    # Drop all tables first
    db.drop_all()
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")