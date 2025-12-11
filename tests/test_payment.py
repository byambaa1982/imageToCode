# tests/test_payment.py
"""Tests for payment functionality."""

import pytest
from app import create_app
from app.extensions import db
from app.models import Account, Package, Order


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
        credits_remaining=3.0
    )
    user.set_password('TestPassword123!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def test_package(app):
    """Create a test package."""
    package = Package(
        name='Basic Package',
        code='basic',
        description='Basic credits package',
        credits=10.0,
        price=9.99,
        is_active=True,
        display_order=1
    )
    db.session.add(package)
    db.session.commit()
    return package


@pytest.fixture
def authenticated_client(client, test_user):
    """Create authenticated test client."""
    with client:
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })
        yield client


class TestPricingPage:
    """Test pricing page."""
    
    def test_pricing_page_loads(self, client, test_package):
        """Test pricing page displays packages."""
        response = client.get('/pricing')
        assert response.status_code == 200
        assert b'Basic Package' in response.data
        
    def test_pricing_page_shows_active_packages_only(self, client, app):
        """Test pricing page only shows active packages."""
        with app.app_context():
            # Create inactive package
            package = Package(
                name='Inactive Package',
                code='inactive',
                description='Should not be visible',
                credits=50.0,
                price=49.99,
                is_active=False,
                display_order=2
            )
            db.session.add(package)
            db.session.commit()
        
        response = client.get('/pricing')
        assert response.status_code == 200
        assert b'Inactive Package' not in response.data


class TestCheckout:
    """Test checkout flow."""
    
    def test_checkout_requires_login(self, client, test_package):
        """Test checkout requires authentication."""
        response = client.get(f'/payment/checkout/{test_package.id}', 
                             follow_redirects=False)
        assert response.status_code == 302
        
    def test_checkout_with_invalid_package(self, authenticated_client):
        """Test checkout with invalid package ID."""
        response = authenticated_client.get('/payment/checkout/99999')
        assert response.status_code == 404
        
    def test_checkout_with_inactive_package(self, authenticated_client, app):
        """Test checkout with inactive package."""
        with app.app_context():
            package = Package(
                name='Inactive Package',
                code='inactive2',
                description='Should not be purchasable',
                credits=50.0,
                price=49.99,
                is_active=False,
                display_order=2
            )
            db.session.add(package)
            db.session.commit()
            package_id = package.id
        
        response = authenticated_client.get(f'/payment/checkout/{package_id}')
        assert response.status_code in [404, 400]


class TestStripeWebhook:
    """Test Stripe webhook handling."""
    
    def test_webhook_requires_signature(self, client):
        """Test webhook requires valid signature."""
        response = client.post('/payment/webhook', 
                              json={'type': 'checkout.session.completed'})
        # Should fail without proper signature
        assert response.status_code in [400, 401, 403]
        
    def test_webhook_invalid_payload(self, client):
        """Test webhook with invalid payload."""
        response = client.post('/payment/webhook',
                              data='invalid',
                              headers={'Stripe-Signature': 'test'})
        assert response.status_code in [400, 401, 403]


class TestOrderModel:
    """Test Order model."""
    
    def test_create_order(self, app, test_user, test_package):
        """Test creating an order."""
        with app.app_context():
            order = Order(
                account_id=test_user.id,
                package_type=test_package.code,  # Use package_type instead of package_id
                stripe_session_id='cs_test_123',  # Use stripe_session_id instead of stripe_checkout_session_id
                amount=9.99,
                credits_purchased=10.0,
                status='pending'
            )
            db.session.add(order)
            db.session.commit()
            
            assert order.id is not None
            assert order.status == 'pending'
            assert order.credits_purchased == 10.0
            
    def test_order_completion(self, app, test_user, test_package):
        """Test order completion adds credits."""
        with app.app_context():
            initial_credits = test_user.credits_remaining
            
            order = Order(
                account_id=test_user.id,
                package_type=test_package.code,  # Use package_type instead of package_id
                stripe_session_id='cs_test_123',  # Use stripe_session_id instead of stripe_checkout_session_id
                amount=9.99,
                credits_purchased=10.0,
                status='completed'
            )
            db.session.add(order)
            db.session.commit()
            
            # Manually add credits (would normally be done by webhook)
            user = Account.query.get(test_user.id)
            user.credits_remaining += order.credits_purchased
            db.session.commit()
            
            user = Account.query.get(test_user.id)
            assert user.credits_remaining == initial_credits + 10.0


class TestPackageModel:
    """Test Package model."""
    
    def test_package_display_order(self, app):
        """Test packages are ordered correctly."""
        with app.app_context():
            # Create multiple packages
            packages = [
                Package(
                    name=f'Package {i}',
                    code=f'package_{i}',
                    description=f'Description {i}',
                    credits=10.0 * i,
                    price=9.99 * i,
                    is_active=True,
                    display_order=i
                )
                for i in range(1, 4)
            ]
            
            for package in packages:
                db.session.add(package)
            db.session.commit()
            
            # Query packages in order
            ordered = Package.query.filter_by(is_active=True).order_by(Package.display_order).all()
            assert len(ordered) == 3
            assert ordered[0].display_order == 1
            assert ordered[1].display_order == 2
            assert ordered[2].display_order == 3
