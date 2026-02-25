# tests/test_auth.py
# simulate submitting the HTML forms using HTTP POST requests.

from flask_login import current_user
from src.auth.models import User

def test_valid_login_and_logout(client, init_database):
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

def test_invalid_login(client, init_database):
    """Test that wrong passwords trigger the atomic rate limit counter."""
    client.post('/auth/login', data={'email': 'existing@test.com', 'password': 'WrongPassword!!!'})

    # Assert State: Check the actual database row
    user = User.query.filter_by(email='existing@test.com').first()

    assert user.failed_login_attempts == 1
    assert user.is_locked is False

def test_valid_registration(client):
    """Test that a new user can register."""
    response = client.post('/auth/register', data={
        'email': 'newuser@test.com',
        'password': 'SecurePassword123',
        'confirm_password': 'SecurePassword123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Account created successfully" in response.data

def test_duplicate_email_registration(client, init_database):
    """Test that a user cannot register an email that already exists."""
    # We use the 'init_database' fixture here, which already contains 'existing@test.com'
    response = client.post('/auth/register', data={
        'email': 'existing@test.com',
        'password': 'SecurePassword123',
        'confirm_password': 'SecurePassword123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Email address is already registered." in response.data

def test_logged_in_user_redirects(client, init_database):
    """Test that authenticated users cannot access the login/register pages."""
    # 1. Log the user in
    client.post('/auth/login', data={'email': 'existing@test.com', 'password': 'password123'})

    # 2. Try to visit the register page
    response = client.get('/auth/register', follow_redirects=False)

    # 3. Assert they are redirected (302 status code) instead of seeing the page (200)
    assert response.status_code == 302
    assert '/dashboard' in response.location or '/' in response.location

def test_account_lockout(client, init_database):
    """Test that 5 failed attempts locks the account."""
    # Fail the login 5 times in a row
    for _ in range(5):
        client.post('/auth/login', data={'email': 'existing@test.com', 'password': 'wrong'})

    # Check the database state
    from src.auth.models import User
    user = User.query.filter_by(email='existing@test.com').first()

    assert user.failed_login_attempts == 5
    assert user.is_locked is True
