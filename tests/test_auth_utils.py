# tests/test_auth_utils.py
"""Tests for authentication and security utilities."""

import pytest
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from app import create_app
from app.extensions import db
from app.models import Account, PasswordResetToken, EmailVerificationToken
from app.auth.utils import (
    generate_verification_token, 
    verify_token,
    is_safe_url,
    generate_secure_filename,
    validate_password_strength,
    hash_password_reset_token,
    verify_password_reset_token,
    check_rate_limit,
    sanitize_input,
    detect_sql_injection,
    validate_email_format
)
from app.security import validate_csrf_token, generate_csrf_token


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
def test_user(app):
    """Create a test user."""
    user = Account(
        email='test@example.com',
        username='testuser',
        email_verified=True
    )
    user.set_password('TestPassword123!')
    db.session.add(user)
    db.session.commit()
    return user


class TestTokenGeneration:
    """Test token generation and verification utilities."""
    
    def test_generate_verification_token(self, app, test_user):
        """Test email verification token generation."""
        token = generate_verification_token(test_user.id)
        
        assert token is not None
        assert len(token) == 32  # Standard token length
        assert token.isalnum() or any(c in token for c in 'abcdef0123456789')
        
        # Verify token was stored in database
        db_token = EmailVerificationToken.query.filter_by(account_id=test_user.id).first()
        assert db_token is not None
        assert db_token.expires_at > datetime.utcnow()
    
    def test_verify_valid_token(self, app, test_user):
        """Test verification of valid token."""
        token = generate_verification_token(test_user.id)
        
        is_valid, user_id = verify_token(token, 'email_verification')
        
        assert is_valid is True
        assert user_id == test_user.id
    
    def test_verify_invalid_token(self, app):
        """Test verification of invalid token."""
        is_valid, user_id = verify_token('invalid_token_12345', 'email_verification')
        
        assert is_valid is False
        assert user_id is None
    
    def test_verify_expired_token(self, app, test_user):
        """Test verification of expired token."""
        token = generate_verification_token(test_user.id)
        
        # Manually expire the token
        db_token = EmailVerificationToken.query.filter_by(account_id=test_user.id).first()
        db_token.expires_at = datetime.utcnow() - timedelta(hours=1)
        db.session.commit()
        
        is_valid, user_id = verify_token(token, 'email_verification')
        
        assert is_valid is False
        assert user_id is None
    
    def test_verify_used_token(self, app, test_user):
        """Test verification of already used token."""
        token = generate_verification_token(test_user.id)
        
        # Mark token as used
        db_token = EmailVerificationToken.query.filter_by(account_id=test_user.id).first()
        db_token.verified = True
        db.session.commit()
        
        is_valid, user_id = verify_token(token, 'email_verification')
        
        assert is_valid is False
        assert user_id is None


class TestPasswordResetSecurity:
    """Test password reset security utilities."""
    
    def test_hash_password_reset_token(self):
        """Test password reset token hashing."""
        token = "secure_reset_token_123"
        hashed = hash_password_reset_token(token)
        
        assert hashed != token  # Should be hashed
        assert len(hashed) == 64  # SHA256 hex length
        
        # Same token should produce same hash
        hashed2 = hash_password_reset_token(token)
        assert hashed == hashed2
    
    def test_verify_password_reset_token_valid(self, app, test_user):
        """Test verification of valid password reset token."""
        token = "secure_reset_token_123"
        hashed_token = hash_password_reset_token(token)
        
        # Create password reset token entry
        reset_token = PasswordResetToken(
            account_id=test_user.id,
            token_hash=hashed_token,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.session.add(reset_token)
        db.session.commit()
        
        is_valid, user_id = verify_password_reset_token(token)
        
        assert is_valid is True
        assert user_id == test_user.id
    
    def test_verify_password_reset_token_invalid(self, app):
        """Test verification of invalid password reset token."""
        is_valid, user_id = verify_password_reset_token("invalid_token")
        
        assert is_valid is False
        assert user_id is None
    
    def test_verify_password_reset_token_expired(self, app, test_user):
        """Test verification of expired password reset token."""
        token = "expired_reset_token_123"
        hashed_token = hash_password_reset_token(token)
        
        # Create expired password reset token
        reset_token = PasswordResetToken(
            account_id=test_user.id,
            token_hash=hashed_token,
            expires_at=datetime.utcnow() - timedelta(hours=1)  # Expired
        )
        db.session.add(reset_token)
        db.session.commit()
        
        is_valid, user_id = verify_password_reset_token(token)
        
        assert is_valid is False
        assert user_id is None
    
    def test_verify_password_reset_token_used(self, app, test_user):
        """Test verification of already used password reset token."""
        token = "used_reset_token_123"
        hashed_token = hash_password_reset_token(token)
        
        # Create used password reset token
        reset_token = PasswordResetToken(
            account_id=test_user.id,
            token_hash=hashed_token,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            used=True  # Already used
        )
        db.session.add(reset_token)
        db.session.commit()
        
        is_valid, user_id = verify_password_reset_token(token)
        
        assert is_valid is False
        assert user_id is None


class TestURLSafety:
    """Test URL safety validation utilities."""
    
    def test_is_safe_url_valid_relative(self):
        """Test safe relative URLs."""
        safe_urls = [
            '/dashboard',
            '/account/settings',
            '/converter/upload',
            '/',
            '/main/pricing'
        ]
        
        for url in safe_urls:
            assert is_safe_url(url) is True
    
    def test_is_safe_url_invalid_external(self):
        """Test rejection of external URLs."""
        unsafe_urls = [
            'http://evil.com',
            'https://malicious.site',
            '//attacker.com',
            'javascript:alert("xss")',
            'data:text/html,<script>alert(1)</script>'
        ]
        
        for url in unsafe_urls:
            assert is_safe_url(url) is False
    
    def test_is_safe_url_valid_same_domain(self):
        """Test acceptance of same-domain URLs."""
        # Assuming app runs on localhost in testing
        same_domain_urls = [
            'http://localhost/dashboard',
            'http://127.0.0.1/account',
            'https://localhost/secure-page'
        ]
        
        with patch('app.auth.utils.request') as mock_request:
            mock_request.host = 'localhost'
            mock_request.scheme = 'http'
            
            for url in same_domain_urls:
                assert is_safe_url(url) is True


class TestPasswordSecurity:
    """Test password security utilities."""
    
    def test_validate_password_strength_strong(self):
        """Test validation of strong passwords."""
        strong_passwords = [
            'StrongPassword123!',
            'MySecure@Pass2024',
            'Complex#Password99',
            'Very$ecure1Pass'
        ]
        
        for password in strong_passwords:
            is_valid, errors = validate_password_strength(password)
            assert is_valid is True
            assert len(errors) == 0
    
    def test_validate_password_strength_weak(self):
        """Test rejection of weak passwords."""
        weak_passwords = [
            ('password', 'No uppercase, numbers, or special characters'),
            ('PASSWORD', 'No lowercase, numbers, or special characters'),
            ('123456789', 'No letters or special characters'),
            ('Pass1', 'Too short'),
            ('SimplePass', 'No numbers or special characters'),
            ('simple123', 'No uppercase or special characters'),
            ('Simple!', 'No numbers'),
            ('SIMPLE123!', 'No lowercase')
        ]
        
        for password, expected_issue in weak_passwords:
            is_valid, errors = validate_password_strength(password)
            assert is_valid is False
            assert len(errors) > 0
    
    def test_validate_password_strength_common(self):
        """Test rejection of common passwords."""
        common_passwords = [
            'password123',
            'admin123',
            'qwerty123',
            '123456789',
            'password1!'
        ]
        
        for password in common_passwords:
            is_valid, errors = validate_password_strength(password)
            # Should fail (though specific implementation may vary)
            assert is_valid is False or 'common' in str(errors).lower()


class TestRateLimiting:
    """Test rate limiting utilities."""
    
    def test_check_rate_limit_within_limit(self):
        """Test rate limiting within allowed limits."""
        client_id = 'test_client_123'
        
        # First few requests should be allowed
        for i in range(3):
            allowed, remaining = check_rate_limit(client_id, max_requests=5, window_minutes=1)
            assert allowed is True
            assert remaining >= 0
    
    def test_check_rate_limit_exceeded(self):
        """Test rate limiting when limit is exceeded."""
        client_id = 'test_client_456'
        max_requests = 2
        
        # Use up allowed requests
        for i in range(max_requests):
            allowed, remaining = check_rate_limit(client_id, max_requests=max_requests, window_minutes=1)
            assert allowed is True
        
        # Next request should be blocked
        allowed, remaining = check_rate_limit(client_id, max_requests=max_requests, window_minutes=1)
        assert allowed is False
        assert remaining == 0
    
    def test_check_rate_limit_window_reset(self):
        """Test rate limiting window reset."""
        client_id = 'test_client_789'
        
        with patch('time.time') as mock_time:
            # Start at time 0
            mock_time.return_value = 0
            
            # Use up requests
            for i in range(2):
                check_rate_limit(client_id, max_requests=2, window_minutes=1)
            
            # Should be blocked
            allowed, _ = check_rate_limit(client_id, max_requests=2, window_minutes=1)
            assert allowed is False
            
            # Move time forward past window
            mock_time.return_value = 70  # 70 seconds later
            
            # Should be allowed again
            allowed, _ = check_rate_limit(client_id, max_requests=2, window_minutes=1)
            assert allowed is True


class TestInputSanitization:
    """Test input sanitization utilities."""
    
    def test_sanitize_input_basic(self):
        """Test basic input sanitization."""
        dangerous_inputs = [
            ('<script>alert("xss")</script>', 'alert("xss")'),
            ('<img src="x" onerror="alert(1)">', ''),
            ('javascript:alert(1)', 'javascript:alert(1)'),  # May be left as-is with warning
            ('<div onclick="evil()">text</div>', 'text')
        ]
        
        for dangerous, expected_safe in dangerous_inputs:
            safe_input = sanitize_input(dangerous)
            assert '<script>' not in safe_input
            assert 'onerror=' not in safe_input
            assert 'onclick=' not in safe_input
    
    def test_sanitize_input_preserve_safe(self):
        """Test that safe input is preserved."""
        safe_inputs = [
            'Normal text input',
            'Text with numbers 123',
            'Text with symbols: !@#$%^&*()',
            'Unicode text: héllo wörld',
            'Email: user@example.com'
        ]
        
        for safe_input in safe_inputs:
            sanitized = sanitize_input(safe_input)
            assert sanitized == safe_input or len(sanitized) >= len(safe_input) * 0.9  # Allow minor cleaning
    
    def test_detect_sql_injection(self):
        """Test SQL injection detection."""
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM passwords --",
            "admin'--",
            "' OR 1=1 --",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ]
        
        for injection in sql_injection_attempts:
            is_suspicious = detect_sql_injection(injection)
            assert is_suspicious is True
    
    def test_detect_sql_injection_false_positives(self):
        """Test that normal inputs don't trigger SQL injection detection."""
        normal_inputs = [
            "John's car",
            "I can't believe it",
            "The price is $1 or $2",
            "Email me at john@example.com",
            "Product code: ABC-123",
            "Normal search term"
        ]
        
        for normal_input in normal_inputs:
            is_suspicious = detect_sql_injection(normal_input)
            assert is_suspicious is False


class TestEmailValidation:
    """Test email format validation."""
    
    def test_validate_email_format_valid(self):
        """Test validation of valid email formats."""
        valid_emails = [
            'user@example.com',
            'test.email@domain.org',
            'first.last+tag@company.co.uk',
            'user123@test-domain.net',
            'email_with_underscore@example.io'
        ]
        
        for email in valid_emails:
            is_valid, error = validate_email_format(email)
            assert is_valid is True
            assert error is None
    
    def test_validate_email_format_invalid(self):
        """Test rejection of invalid email formats."""
        invalid_emails = [
            'notanemail',
            '@example.com',
            'user@',
            'user..name@example.com',
            'user@domain',
            'user name@example.com',  # Space not allowed
            'user@domain..com'
        ]
        
        for email in invalid_emails:
            is_valid, error = validate_email_format(email)
            assert is_valid is False
            assert error is not None


class TestCSRFProtection:
    """Test CSRF token utilities."""
    
    def test_generate_csrf_token(self):
        """Test CSRF token generation."""
        token = generate_csrf_token()
        
        assert token is not None
        assert len(token) >= 32  # Should be sufficiently long
        assert token.replace('-', '').replace('_', '').isalnum()  # Should be alphanumeric with possible separators
    
    def test_validate_csrf_token_valid(self):
        """Test validation of valid CSRF token."""
        token = generate_csrf_token()
        
        # Mock session with token
        with patch('app.security.session', {'csrf_token': token}):
            is_valid = validate_csrf_token(token)
            assert is_valid is True
    
    def test_validate_csrf_token_invalid(self):
        """Test rejection of invalid CSRF token."""
        valid_token = generate_csrf_token()
        invalid_token = 'invalid_token_123'
        
        # Mock session with valid token
        with patch('app.security.session', {'csrf_token': valid_token}):
            is_valid = validate_csrf_token(invalid_token)
            assert is_valid is False
    
    def test_validate_csrf_token_missing_session(self):
        """Test CSRF validation when no session token exists."""
        token = 'some_token_123'
        
        # Mock empty session
        with patch('app.security.session', {}):
            is_valid = validate_csrf_token(token)
            assert is_valid is False


class TestSecureFilename:
    """Test secure filename generation."""
    
    def test_generate_secure_filename_basic(self):
        """Test basic secure filename generation."""
        dangerous_filenames = [
            '../../../etc/passwd',
            'file with spaces.txt',
            'file<script>.html',
            'CON.txt',  # Windows reserved name
            'file|pipe.txt'
        ]
        
        for filename in dangerous_filenames:
            secure = generate_secure_filename(filename)
            assert '..' not in secure
            assert '/' not in secure
            assert '\\' not in secure
            assert '<' not in secure
            assert '>' not in secure
            assert '|' not in secure
    
    def test_generate_secure_filename_preserve_extension(self):
        """Test that file extensions are preserved."""
        test_files = [
            ('document.pdf', 'pdf'),
            ('image.jpg', 'jpg'),
            ('archive.tar.gz', 'gz'),
            ('script.js', 'js')
        ]
        
        for filename, expected_ext in test_files:
            secure = generate_secure_filename(filename)
            assert secure.endswith(f'.{expected_ext}')
    
    def test_generate_secure_filename_unicode(self):
        """Test handling of unicode characters in filenames."""
        unicode_filenames = [
            'файл.txt',  # Cyrillic
            ' 文档.pdf',  # Chinese
            'dökument.doc',  # German umlaut
            'résumé.pdf'  # French accent
        ]
        
        for filename in unicode_filenames:
            secure = generate_secure_filename(filename)
            # Should not raise errors and should return something reasonable
            assert len(secure) > 0
            assert secure.replace('_', '').replace('-', '').replace('.', '').isalnum() or any(c.isascii() for c in secure)
