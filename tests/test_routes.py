# tests/test_routes.py

def test_home_page(client):
    """Test that the index page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to the Flask Auth System" in response.data

def test_register_page(client):
    """Test that the register page loads."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b"Create an Account" in response.data

def test_login_page(client):
    """Test that the login page loads."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b"Welcome Back" in response.data

def test_dashboard_access_denied(client):
    """Test that an anonymous user is redirected to login if they try to view the dashboard."""
    response = client.get('/dashboard', follow_redirects=True)
    # They should be redirected to the login page
    assert response.status_code == 200
    assert b"Please log in to access this page." in response.data
    assert b"Welcome Back" in response.data # Confirms we are on the login page
