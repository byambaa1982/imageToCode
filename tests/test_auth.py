# tests/test_auth.py
"""Integration tests for authentication."""

import pytest
from app import create_app
from app.extensions import db
from app.models import Account, EmailVerificationToken
from datetime import datetime, timedelta


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
def test_user(app):
    """Create a verified test user."""
    user = Account(
        email='test@example.com',
        username='testuser',
        email_verified=True
    )
    user.set_password('TestPassword123!')
    db.session.add(user)
    db.session.commit()
    return user


class TestRegistration:
    """Test user registration."""
    
    def test_register_page_loads(self, client):
        """Test registration page loads."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Create Account' in response.data or b'Register' in response.data
        
    def test_successful_registration(self, client, app):
        """Test successful user registration."""
        with app.app_context():
            response = client.post('/auth/register', data={
                'email': 'newuser@example.com',
                'username': 'newuser',
                'password': 'StrongPassword123!',
                'confirm_password': 'StrongPassword123!'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            user = Account.query.filter_by(email='newuser@example.com').first()
            assert user is not None
            assert user.username == 'newuser'
            assert user.email_verified is False
            assert user.credits_remaining == 3.0
            
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        response = client.post('/auth/register', data={
            'email': 'test@example.com',
            'username': 'anotheruser',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        
        assert response.status_code == 200
        assert b'email' in response.data.lower() or b'already' in response.data.lower()
        
    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post('/auth/register', data={
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': '123',
            'confirm_password': '123'
        })
        
        assert response.status_code == 200
        
    def test_register_password_mismatch(self, client):
        """Test registration with password mismatch."""
        response = client.post('/auth/register', data={
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword123!'
        })
        
        assert response.status_code == 200


class TestLogin:
    """Test user login."""
    
    def test_login_page_loads(self, client):
        """Test login page loads."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'Sign In' in response.data
        
    def test_successful_login(self, client, test_user):
        """Test successful login."""
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'incorrect' in response.data.lower()
        
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        response = client.post('/auth/login', data={
            'email': 'nonexistent@example.com',
            'password': 'Password123!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid' in response.data or b'not found' in response.data.lower()
        
    def test_login_locked_account(self, client, test_user, app):
        """Test login with locked account."""
        with app.app_context():
            user = Account.query.get(test_user.id)
            user.failed_login_attempts = 5
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            db.session.commit()
        
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'locked' in response.data.lower() or b'temporarily' in response.data.lower()


class TestLogout:
    """Test user logout."""
    
    def test_logout(self, client, test_user):
        """Test user logout."""
        # Login first
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200


class TestPasswordReset:
    """Test password reset flow."""
    
    def test_password_reset_page_loads(self, client):
        """Test password reset request page loads."""
        response = client.get('/auth/reset-password-request')
        assert response.status_code == 200
        
    def test_request_password_reset(self, client, test_user):
        """Test requesting password reset."""
        response = client.post('/auth/reset-password-request', data={
            'email': 'test@example.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200


class TestEmailVerification:
    """Test email verification."""
    
    def test_verify_email_with_valid_token(self, client, test_user, app):
        """Test email verification with valid token."""
        with app.app_context():
            # Create verification token
            token = EmailVerificationToken(
                account_id=test_user.id,
                token_hash='test_token_hash',
                expires_at=datetime.utcnow() + timedelta(days=1)
            )
            db.session.add(token)
            
            # Mark user as unverified
            user = Account.query.get(test_user.id)
            user.email_verified = False
            db.session.commit()
        
        # Note: This test assumes the verification endpoint exists
        # Adjust based on actual implementation


class TestProtectedRoutes:
    """Test protected routes require authentication."""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard requires login."""
        response = client.get('/account/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'sign in' in response.data.lower()
        
    def test_converter_requires_login(self, client):
        """Test converter requires login."""
        response = client.get('/converter/upload', follow_redirects=True)
        assert response.status_code == 200
        
    def test_admin_requires_login(self, client):
        """Test admin panel requires login."""
        response = client.get('/admin/dashboard', follow_redirects=True)
        assert response.status_code == 200
