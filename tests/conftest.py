# tests/conftest.py
import os
from flask import Flask
import pytest
from src import create_app
from src.extensions import db
from src.auth.models import User

@pytest.fixture
def app():
    """Creates a fresh Flask application and fresh RAM database for each test."""

    # FIX: Force the in-memory database BEFORE the app factory runs
    # This prevents SQLAlchemy from trying to build an engine for instance/app.db
    os.environ['DATABASE_URL'] = "sqlite://"

    app = create_app()

    # Override configuration for testing
    app.config.update({
        "TESTING": True,
        #"SQLALCHEMY_DATABASE_URI": "sqlite://", # 'sqlite://' with no path means "in-memory only"
        "WTF_CSRF_ENABLED": False, # Disable CSRF tokens just for automated testing
    })

    # Create the database tables in RAM
    with app.app_context():
        # Create fresh tables in RAM (Instantaneous)
        db.create_all()
        yield app # This hands the app over to the test
        db.drop_all() # When the test finishes, destroy the database in RAM

@pytest.fixture
def client(app: Flask):
    """A test client for the app to simulate browser requests."""
    return app.test_client()

@pytest.fixture
def init_database(app: Flask):
    """A fixture that provides a pre-populated database with one test user."""
    with app.app_context():
        from werkzeug.security import generate_password_hash
        user = User(email="existing@test.com", password_hash=generate_password_hash("password123"))
        db.session.add(user)
        db.session.commit()
        return db
