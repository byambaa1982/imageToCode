# tests/test_models.py
"""Unit tests for database models."""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models import (
    Account, Conversion, CreditsTransaction, Order, Package,
    PasswordResetToken, EmailVerificationToken
)
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
def test_account(app):
    """Create a test account."""
    account = Account(
        email='test@example.com',
        username='testuser',
        email_verified=True
    )
    account.set_password('testpassword123')
    db.session.add(account)
    db.session.commit()
    return account


class TestAccount:
    """Test Account model."""
    
    def test_create_account(self, app):
        """Test creating an account."""
        account = Account(email='user@example.com')
        account.set_password('password123')
        db.session.add(account)
        db.session.commit()
        
        assert account.id is not None
        assert account.uuid is not None
        assert account.email == 'user@example.com'
        assert account.password_hash is not None
        assert account.credits_remaining == Decimal('3.00')
        assert account.is_active is True
        assert account.is_admin is False
        
    def test_password_hashing(self, app):
        """Test password hashing and checking."""
        account = Account(email='user@example.com')
        account.set_password('mypassword')
        
        assert account.check_password('mypassword') is True
        assert account.check_password('wrongpassword') is False
        
    def test_has_credits(self, test_account):
        """Test credit checking."""
        assert test_account.has_credits(1.0) is True
        assert test_account.has_credits(3.0) is True
        assert test_account.has_credits(4.0) is False
        
    def test_deduct_credits(self, test_account):
        """Test credit deduction."""
        initial_credits = test_account.credits_remaining
        test_account.deduct_credits(1.0, 'Test conversion')
        
        assert test_account.credits_remaining == initial_credits - Decimal('1.00')
        
        # Check transaction was created
        transaction = CreditsTransaction.query.filter_by(
            account_id=test_account.id,
            transaction_type='usage'
        ).first()
        assert transaction is not None
        assert transaction.amount == Decimal('-1.00')
        
    def test_deduct_credits_insufficient(self, test_account):
        """Test deducting more credits than available."""
        with pytest.raises(ValueError, match='Insufficient credits'):
            test_account.deduct_credits(10.0)
            
    def test_add_credits(self, test_account):
        """Test adding credits."""
        initial_credits = test_account.credits_remaining
        test_account.add_credits(5.0, 'Purchase')
        
        assert test_account.credits_remaining == initial_credits + Decimal('5.00')
        
        # Check transaction was created
        transaction = CreditsTransaction.query.filter_by(
            account_id=test_account.id,
            transaction_type='purchase'
        ).first()
        assert transaction is not None
        assert transaction.amount == Decimal('5.00')
        
    def test_account_lock(self, test_account):
        """Test account locking after failed logins."""
        assert test_account.is_locked() is False
        
        # Simulate failed login attempts
        for i in range(5):
            test_account.increment_failed_login()
        
        assert test_account.is_locked() is True
        assert test_account.failed_login_attempts == 5
        
    def test_reset_failed_login(self, test_account):
        """Test resetting failed login attempts."""
        test_account.failed_login_attempts = 3
        test_account.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
        
        test_account.reset_failed_login()
        
        assert test_account.failed_login_attempts == 0
        assert test_account.locked_until is None


class TestConversion:
    """Test Conversion model."""
    
    def test_create_conversion(self, test_account):
        """Test creating a conversion."""
        conversion = Conversion(
            account_id=test_account.id,
            original_image_url='https://example.com/image.png',
            original_filename='screenshot.png',
            framework='react',
            css_framework='tailwind',
            status='pending'
        )
        db.session.add(conversion)
        db.session.commit()
        
        assert conversion.id is not None
        assert conversion.uuid is not None
        assert conversion.account_id == test_account.id
        assert conversion.status == 'pending'
        assert conversion.retry_count == 0
        
    def test_conversion_relationship(self, test_account):
        """Test account-conversion relationship."""
        conversion = Conversion(
            account_id=test_account.id,
            original_image_url='https://example.com/image.png',
            original_filename='screenshot.png',
            framework='react'
        )
        db.session.add(conversion)
        db.session.commit()
        
        # Access via relationship
        assert conversion.account == test_account
        assert conversion in test_account.conversions.all()


class TestCreditsTransaction:
    """Test CreditsTransaction model."""
    
    def test_create_transaction(self, test_account):
        """Test creating a credits transaction."""
        transaction = CreditsTransaction(
            account_id=test_account.id,
            amount=Decimal('5.00'),
            balance_after=Decimal('8.00'),
            transaction_type='purchase',
            description='Bought 5 credits'
        )
        db.session.add(transaction)
        db.session.commit()
        
        assert transaction.id is not None
        assert transaction.account_id == test_account.id
        assert transaction.amount == Decimal('5.00')
        assert transaction.balance_after == Decimal('8.00')
        assert transaction.transaction_type == 'purchase'


class TestOrder:
    """Test Order model."""
    
    def test_create_order(self, test_account):
        """Test creating an order."""
        order = Order(
            account_id=test_account.id,
            amount=Decimal('9.99'),
            currency='USD',
            package_type='pro_pack',
            credits_purchased=Decimal('10.00'),
            status='pending'
        )
        db.session.add(order)
        db.session.commit()
        
        assert order.id is not None
        assert order.account_id == test_account.id
        assert order.amount == Decimal('9.99')
        assert order.status == 'pending'
        
    def test_completed_order_with_transaction(self, test_account):
        """Test order with credits transaction."""
        order = Order(
            account_id=test_account.id,
            amount=Decimal('5.00'),
            package_type='starter_pack',
            credits_purchased=Decimal('5.00'),
            status='completed',
            stripe_payment_id='pi_test123'
        )
        db.session.add(order)
        db.session.commit()
        
        # Add credits transaction
        transaction = CreditsTransaction(
            account_id=test_account.id,
            order_id=order.id,
            amount=Decimal('5.00'),
            balance_after=Decimal('8.00'),
            transaction_type='purchase',
            description='Starter Pack purchase'
        )
        db.session.add(transaction)
        db.session.commit()
        
        # Check relationship
        assert transaction.order == order
        assert transaction in order.credit_transactions.all()


class TestPackage:
    """Test Package model."""
    
    def test_create_package(self, app):
        """Test creating a package."""
        package = Package(
            name='Test Package',
            code='test_pack',
            description='Test description',
            price=Decimal('9.99'),
            credits=Decimal('10.00'),
            is_active=True,
            is_featured=True,
            badge='Best Value',
            display_order=1
        )
        db.session.add(package)
        db.session.commit()
        
        assert package.id is not None
        assert package.code == 'test_pack'
        assert package.price == Decimal('9.99')
        assert package.is_active is True


class TestPasswordResetToken:
    """Test PasswordResetToken model."""
    
    def test_create_token(self, test_account):
        """Test creating a password reset token."""
        token = PasswordResetToken(
            account_id=test_account.id,
            token_hash='hashed_token_value',
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.session.add(token)
        db.session.commit()
        
        assert token.id is not None
        assert token.account_id == test_account.id
        assert token.used is False
        
    def test_token_expiration(self, test_account):
        """Test token expiration check."""
        # Create expired token
        token = PasswordResetToken(
            account_id=test_account.id,
            token_hash='hashed_token_value',
            expires_at=datetime.utcnow() - timedelta(hours=1)
        )
        db.session.add(token)
        db.session.commit()
        
        assert token.is_expired() is True
        
        # Create valid token
        token2 = PasswordResetToken(
            account_id=test_account.id,
            token_hash='hashed_token_value2',
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.session.add(token2)
        db.session.commit()
        
        assert token2.is_expired() is False


class TestEmailVerificationToken:
    """Test EmailVerificationToken model."""
    
    def test_create_token(self, test_account):
        """Test creating an email verification token."""
        token = EmailVerificationToken(
            account_id=test_account.id,
            token_hash='hashed_token_value',
            expires_at=datetime.utcnow() + timedelta(days=1)
        )
        db.session.add(token)
        db.session.commit()
        
        assert token.id is not None
        assert token.account_id == test_account.id
        assert token.verified is False
        
    def test_token_expiration(self, test_account):
        """Test token expiration check."""
        token = EmailVerificationToken(
            account_id=test_account.id,
            token_hash='hashed_token_value',
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        db.session.add(token)
        db.session.commit()
        
        assert token.is_expired() is True
