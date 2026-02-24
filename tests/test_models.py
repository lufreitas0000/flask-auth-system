# tests/test_models.py
from src.auth.models import User
from werkzeug.security import generate_password_hash, check_password_hash

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
