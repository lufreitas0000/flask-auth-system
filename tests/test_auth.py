# tests/test_auth.py
# simulate submitting the HTML forms using HTTP POST requests.

from flask import Flask
from flask.testing import FlaskClient
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from src.auth.models import User, AuditLog
from freezegun import freeze_time
from datetime import datetime, timezone, timedelta

def test_valid_login_and_logout(client: FlaskClient, init_database: SQLAlchemy):
    """Test state changes upon login and logout."""
    # Wrap the login in a 'with client:' block to keep the context alive!
    with client:
        client.post('/auth/login', data={'email': 'existing@test.com', 'password': 'password123'})

        # Assert State: User is officially authenticated in the session
        assert current_user.is_authenticated is True
        assert current_user.email == 'existing@test.com'

        client.get('/auth/logout')

        # Assert State: User session is destroyed
        assert current_user.is_authenticated is False

def test_invalid_login(client: FlaskClient, init_database: SQLAlchemy):
    """Test that wrong passwords trigger the atomic rate limit counter."""
    client.post('/auth/login', data={'email': 'existing@test.com', 'password': 'WrongPassword!!!'})

    # Assert State: Check the actual database row
    user = User.query.filter_by(email='existing@test.com').first()

    assert user.failed_login_attempts == 1
    assert user.is_locked is False
# tests/test_auth.py
from flask_login import current_user
from src.auth.models import User

def test_valid_registration(client: FlaskClient, app: Flask):
    """Test that a new user is actually saved to the database."""
    client.post('/auth/register', data={
        'email': 'newuser@test.com',
        'password': 'SecurePassword123',
        'confirm_password': 'SecurePassword123'
    })

    # State Assertion: Query the database to prove the user exists
    with app.app_context():
        saved_user = User.query.filter_by(email='newuser@test.com').first()
        assert saved_user is not None
        assert saved_user.email == 'newuser@test.com'
        assert saved_user.failed_login_attempts == 0

def test_duplicate_email_registration(client: FlaskClient, init_database: SQLAlchemy, app: Flask):
    """Test that duplicate emails are rejected at the logic layer."""
    # Attempt to register the email that init_database already created
    response = client.post('/auth/register', data={
        'email': 'existing@test.com',
        'password': 'NewPassword123',
        'confirm_password': 'NewPassword123'
    })

    # State Assertion: We should still only have exactly ONE user with this email
    with app.app_context():
        users_with_email = User.query.filter_by(email='existing@test.com').all()
        assert len(users_with_email) == 1

def test_logged_in_user_redirects(client: FlaskClient, init_database: SQLAlchemy):
    """Test that authenticated users cannot access the login/register pages."""
    # 1. Log the user in
    client.post('/auth/login', data={'email': 'existing@test.com', 'password': 'password123'})

    # 2. Try to visit the register page
    response = client.get('/auth/register', follow_redirects=False)

    # 3. Assert they are redirected (302 status code) instead of seeing the page (200)
    assert response.status_code == 302
    assert '/dashboard' in response.location or '/' in response.location

def test_account_lockout(client: FlaskClient, init_database: SQLAlchemy, app: Flask):
    """Test that after many failed attempts locks the account."""
    max_attempts = app.config.get('MAX_LOGIN_ATTEMPTS', 5)
    # Fail the login max_attempts times in a row
    for _ in range(max_attempts):
        response = client.post('/auth/login', data={'email': 'existing@test.com', 'password': 'wrong'})
    from src.auth.models import User
    user = User.query.filter_by(email='existing@test.com').first()

    assert user.failed_login_attempts == max_attempts
    assert user.is_locked is True
    assert current_user.is_authenticated is False
    assert response.status_code == 200



def test_lockout_duration(client: FlaskClient, init_database: SQLAlchemy, app: Flask):
    """Test that the account unlocks automatically."""

    # 1. Dynamically find out how many attempts it takes to lock an account
    max_attempts = app.config.get('MAX_LOGIN_ATTEMPTS', 5)

    for _ in range(max_attempts):
        client.post('/auth/login', data={'email': 'existing@test.com', 'password': 'wrong'})

    # 2. Extract the exact time the lock was applied
    with app.app_context():
        user = User.query.filter_by(email='existing@test.com').first()
        assert user.is_locked is True
        lock_time = user.locked_until

    # 3. INTERMEDIATE TEST: Fast-forward 14 minutes
    fourteen_mins_later = lock_time - timedelta(minutes=1)
    with freeze_time(fourteen_mins_later):
        response = client.post('/auth/login', data={'email': 'existing@test.com', 'password': 'password123'})

        # State Assertion 1: They should stay on the login page (200 OK)
        assert response.status_code == 200
        # State Assertion 2: The Flask-Login session must NOT be authenticated
        assert current_user.is_authenticated is False

    # 4. FINAL TEST: Fast-forward 16 minutes (Should UNLOCK)
    sixteen_mins_later = lock_time + timedelta(minutes=1)
    with freeze_time(sixteen_mins_later):
        response = client.post('/auth/login', data={'email': 'existing@test.com', 'password': 'password123'})

        # State Assertion 1: They should be redirected to the dashboard (302)
        assert response.status_code == 302
        assert '/dashboard' in response.location
        # State Assertion 2: The Flask-Login session must be active
        assert current_user.is_authenticated is True

        with app.app_context():
            user = User.query.filter_by(email='existing@test.com').first()
            assert user.is_locked is False
            assert user.failed_login_attempts == 0
