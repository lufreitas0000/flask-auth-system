# tests/test_auth.py
# simulate submitting the HTML forms using HTTP POST requests.

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

def test_valid_login_and_logout(client, init_database):
    """Test that an existing user can log in, view the dashboard, and log out."""
    # 1. Log In
    response = client.post('/auth/login', data={
        'email': 'existing@test.com',
        'password': 'password123'
    }, follow_redirects=True)

    assert b"Welcome back!" in response.data

    # 2. Access Dashboard
    dashboard_response = client.get('/dashboard')
    assert dashboard_response.status_code == 200
    assert b"Your Dashboard" in dashboard_response.data
    assert b"existing@test.com" in dashboard_response.data

    # 3. Log Out
    logout_response = client.get('/auth/logout', follow_redirects=True)
    assert b"You have been logged out." in logout_response.data

def test_invalid_login(client, init_database):
    """Test that wrong passwords get rejected."""
    response = client.post('/auth/login', data={
        'email': 'existing@test.com',
        'password': 'WrongPassword!!!'
    }, follow_redirects=True)

    assert b"Invalid email or password." in response.data
