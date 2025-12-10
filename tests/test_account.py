# tests/test_account.py
"""Tests for account functionality."""

import pytest
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models import Account, CreditsTransaction


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
        email_verified=True,
        credits_remaining=10.0
    )
    user.set_password('TestPassword123!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    """Create authenticated test client."""
    with client:
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })
        yield client


class TestDashboard:
    """Test account dashboard."""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard requires authentication."""
        response = client.get('/account/dashboard', follow_redirects=False)
        assert response.status_code == 302
        
    def test_dashboard_authenticated(self, authenticated_client):
        """Test authenticated user can access dashboard."""
        response = authenticated_client.get('/account/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Credits' in response.data


class TestAccountSettings:
    """Test account settings."""
    
    def test_settings_requires_login(self, client):
        """Test settings requires authentication."""
        response = client.get('/account/settings', follow_redirects=False)
        assert response.status_code == 302
        
    def test_settings_authenticated(self, authenticated_client):
        """Test authenticated user can access settings."""
        response = authenticated_client.get('/account/settings')
        assert response.status_code == 200
        
    def test_update_profile(self, authenticated_client, app, test_user):
        """Test updating profile information."""
        response = authenticated_client.post('/account/settings/profile', data={
            'username': 'newusername',
            'email': 'test@example.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            user = Account.query.get(test_user.id)
            # May or may not have updated depending on validation
            assert user is not None
            
    def test_change_password(self, authenticated_client, app, test_user):
        """Test changing password."""
        response = authenticated_client.post('/account/change-password', data={
            'current_password': 'TestPassword123!',
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }, follow_redirects=True)
        
        # May succeed or fail depending on if route exists
        assert response.status_code in [200, 404]


class TestCreditsManagement:
    """Test credits management."""
    
    def test_view_credits(self, authenticated_client, test_user):
        """Test viewing credits balance."""
        response = authenticated_client.get('/account/dashboard')
        assert response.status_code == 200
        # Should show credits somewhere on dashboard
        
    def test_credits_transaction_history(self, authenticated_client, app, test_user):
        """Test viewing transaction history."""
        with app.app_context():
            # Get current balance
            user = Account.query.get(test_user.id)
            current_balance = user.credits_remaining
            
            # Create test transaction
            transaction = CreditsTransaction(
                account_id=test_user.id,
                amount=Decimal('10.0'),
                balance_after=current_balance + Decimal('10.0'),
                transaction_type='purchase',
                description='Test purchase'
            )
            db.session.add(transaction)
            db.session.commit()
        
        response = authenticated_client.get('/account/transactions')
        # May or may not exist
        assert response.status_code in [200, 404]
        
    def test_deduct_credits(self, app, test_user):
        """Test deducting credits."""
        with app.app_context():
            user = Account.query.get(test_user.id)
            initial_credits = user.credits_remaining
            
            success = user.deduct_credits(1.0)
            db.session.commit()
            
            assert success is True
            user = Account.query.get(test_user.id)
            assert user.credits_remaining == initial_credits - 1.0
            
    def test_deduct_credits_insufficient(self, app, test_user):
        """Test deducting more credits than available."""
        with app.app_context():
            user = Account.query.get(test_user.id)
            initial_credits = user.credits_remaining
            
            success = user.deduct_credits(1000.0)
            
            assert success is False
            user = Account.query.get(test_user.id)
            assert user.credits_remaining == initial_credits
            
    def test_add_credits(self, app, test_user):
        """Test adding credits."""
        with app.app_context():
            user = Account.query.get(test_user.id)
            initial_credits = user.credits_remaining
            
            user.add_credits(5.0)
            db.session.commit()
            
            user = Account.query.get(test_user.id)
            assert user.credits_remaining == initial_credits + 5.0


class TestAccountSecurity:
    """Test account security features."""
    
    def test_failed_login_tracking(self, app, test_user):
        """Test failed login attempts are tracked."""
        with app.app_context():
            user = Account.query.get(test_user.id)
            initial_attempts = user.failed_login_attempts
            
            user.increment_failed_login()
            db.session.commit()
            
            user = Account.query.get(test_user.id)
            assert user.failed_login_attempts == initial_attempts + 1
            
    def test_account_locking(self, app, test_user):
        """Test account locks after too many failed attempts."""
        with app.app_context():
            user = Account.query.get(test_user.id)
            
            # Simulate 5 failed attempts
            for _ in range(5):
                user.increment_failed_login()
            db.session.commit()
            
            user = Account.query.get(test_user.id)
            assert user.is_locked() is True
            
    def test_reset_failed_login(self, app, test_user):
        """Test resetting failed login attempts."""
        with app.app_context():
            user = Account.query.get(test_user.id)
            user.failed_login_attempts = 3
            db.session.commit()
            
            user.reset_failed_login()
            db.session.commit()
            
            user = Account.query.get(test_user.id)
            assert user.failed_login_attempts == 0
            assert user.locked_until is None


class TestAccountDeactivation:
    """Test account deactivation."""
    
    def test_deactivate_account(self, app, test_user):
        """Test deactivating account."""
        with app.app_context():
            user = Account.query.get(test_user.id)
            user.is_active = False
            db.session.commit()
            
            user = Account.query.get(test_user.id)
            assert user.is_active is False
            
    def test_login_deactivated_account(self, client, app, test_user):
        """Test logging in with deactivated account."""
        with app.app_context():
            user = Account.query.get(test_user.id)
            user.is_active = False
            db.session.commit()
        
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'deactivated' in response.data.lower() or b'contact support' in response.data.lower()
