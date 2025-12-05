# tests/test_app.py
"""Basic application tests."""

import pytest
from app import create_app
from app.extensions import db
from config import config


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


def test_app_exists(app):
    """Test that app exists."""
    assert app is not None


def test_app_is_testing(app):
    """Test that app is in testing mode."""
    assert app.config['TESTING']


def test_home_page(client):
    """Test home page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Screenshot to Code' in response.data


def test_login_page(client):
    """Test login page loads."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Sign in' in response.data


def test_register_page(client):
    """Test register page loads."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Create your account' in response.data


def test_404_page(client):
    """Test 404 error page."""
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
    assert b'404' in response.data


def test_pricing_page(client):
    """Test pricing page loads."""
    response = client.get('/main/pricing')
    assert response.status_code == 200


def test_about_page(client):
    """Test about page loads."""
    response = client.get('/main/about')
    assert response.status_code == 200


def test_api_health(client):
    """Test API health endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'healthy'
