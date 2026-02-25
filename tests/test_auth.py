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
# tests/test_auth.py
from flask_login import current_user
from src.auth.models import User

def test_valid_registration(client, app):
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

def test_duplicate_email_registration(client, init_database, app):
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
