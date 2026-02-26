# tests/test_models.py
from src.auth.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask

def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, password hash, and default values are defined correctly
    """
    user = User(email='test@test.com', password_hash='dummy_hash')

    assert user.email == 'test@test.com'
    assert user.password_hash == 'dummy_hash'

def test_password_hashing():
    """
    GIVEN a plaintext password
    WHEN it is hashed
    THEN ensure the hash can be verified and rejects wrong passwords
    """
    password = "MySuperSecretPassword123"
    hashed = generate_password_hash(password)

    # It should not store the plaintext
    assert hashed != password
    # It should verify the correct password
    assert check_password_hash(hashed, password) is True
    # It should reject a wrong password
    assert check_password_hash(hashed, "wrongpassword") is False

def test_password_reset_token(app: Flask, init_database):
    """
    GIVEN a User model
    WHEN get_reset_token is called
    THEN verify the token can be decoded to the correct user, and rejects invalid/expired tokens
    """
    with app.app_context():
        user = User.query.filter_by(email='existing@test.com').first()
        token = user.get_reset_token()

        # 1. Verify a valid token successfully returns the user
        returned_user = User.verify_reset_token(token)
        assert returned_user is not None
        assert returned_user.id == user.id

        # 2. Verify a tampered/fake token returns None
        assert User.verify_reset_token('fake-hacker-token-data') is None

        # 3. Verify an expired token returns None (by artificially testing an age limit of -1 seconds)
        assert User.verify_reset_token(token, expires_sec=-1) is None
