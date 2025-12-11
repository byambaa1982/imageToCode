# app/auth/utils.py
"""Authentication utilities."""

import secrets
import hashlib
import re
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Tuple, Optional
from flask import url_for, current_app, request
from flask_mail import Message
from werkzeug.utils import secure_filename
from app.extensions import db, mail, bcrypt
from app.models import PasswordResetToken, EmailVerificationToken


def get_client_ip():
    """Get the client's IP address."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr or 'unknown'


def log_account_activity(account_id, activity_type, metadata=None):
    """Log account activity for security and auditing.
    
    Args:
        account_id: The account ID (can be None for failed logins)
        activity_type: Type of activity (login_success, login_failed, account_created, etc.)
        metadata: Additional data to store as JSON
    """
    try:
        from app.models import AnalyticsEvent
        
        event = AnalyticsEvent(
            account_id=account_id,
            event_type=activity_type,
            event_data=metadata or {},
            ip_address=get_client_ip(),
            user_agent=request.headers.get('User-Agent', 'unknown')[:500] if request else None
        )
        db.session.add(event)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f'Failed to log activity: {str(e)}')
        # Don't raise exception - logging failure shouldn't break the flow


def cleanup_expired_tokens():
    """Clean up expired password reset and email verification tokens."""
    try:
        now = datetime.utcnow()
        
        # Delete expired password reset tokens
        expired_reset = PasswordResetToken.query.filter(
            PasswordResetToken.expires_at < now
        ).delete()
        
        # Delete expired verification tokens
        expired_verify = EmailVerificationToken.query.filter(
            EmailVerificationToken.expires_at < now
        ).delete()
        
        db.session.commit()
        
        return expired_reset, expired_verify
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Failed to cleanup tokens: {str(e)}')
        return 0, 0


def generate_token():
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


def hash_token(token):
    """Hash a token using SHA-256."""
    return hashlib.sha256(token.encode()).hexdigest()


def create_password_reset_token(account):
    """Create a password reset token for an account."""
    token = generate_token()
    token_hash = hash_token(token)
    
    reset_token = PasswordResetToken(
        account_id=account.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.session.add(reset_token)
    db.session.commit()
    
    return token


def verify_password_reset_token(token):
    """Verify a password reset token and return the associated account."""
    token_hash = hash_token(token)
    
    reset_token = PasswordResetToken.query.filter_by(
        token_hash=token_hash,
        used=False
    ).first()
    
    if not reset_token or reset_token.is_expired():
        return None
    
    return reset_token


def create_email_verification_token(account):
    """Create an email verification token for an account."""
    token = generate_token()
    token_hash = hash_token(token)
    
    verification_token = EmailVerificationToken(
        account_id=account.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.session.add(verification_token)
    db.session.commit()
    
    return token


def verify_email_token(token):
    """Verify an email verification token and return the associated account."""
    token_hash = hash_token(token)
    
    verification_token = EmailVerificationToken.query.filter_by(
        token_hash=token_hash,
        verified=False
    ).first()
    
    if not verification_token or verification_token.is_expired():
        return None
    
    return verification_token


def send_password_reset_email(account):
    """Send password reset email to account."""
    token = create_password_reset_token(account)
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    msg = Message(
        'Password Reset Request',
        recipients=[account.email]
    )
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email and no changes will be made.

This link will expire in 1 hour.
'''
    msg.html = f'''
    <p>To reset your password, click the link below:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>If you did not make this request, simply ignore this email and no changes will be made.</p>
    <p><small>This link will expire in 1 hour.</small></p>
    '''
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send password reset email: {str(e)}')
        return False


def send_verification_email(account):
    """Send email verification to account."""
    token = create_email_verification_token(account)
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    
    msg = Message(
        'Verify Your Email Address',
        recipients=[account.email]
    )
    msg.body = f'''Welcome to {current_app.config['APP_NAME']}!

Please verify your email address by visiting the following link:
{verify_url}

This link will expire in 7 days.
'''
    msg.html = f'''
    <h2>Welcome to {current_app.config['APP_NAME']}!</h2>
    <p>Please verify your email address by clicking the link below:</p>
    <p><a href="{verify_url}">Verify Email Address</a></p>
    <p><small>This link will expire in 7 days.</small></p>
    '''
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send verification email: {str(e)}')
        return False


def send_welcome_email(account):
    """Send welcome email after verification."""
    msg = Message(
        f'Welcome to {current_app.config["APP_NAME"]}!',
        recipients=[account.email]
    )
    msg.body = f'''Hi {account.username},

Thank you for verifying your email! You now have {account.credits_remaining} free conversions to get started.

Visit {current_app.config['APP_URL']} to start converting your UI screenshots to code.

Best regards,
The {current_app.config['APP_NAME']} Team
'''
    msg.html = f'''
    <h2>Hi {account.username},</h2>
    <p>Thank you for verifying your email! You now have <strong>{account.credits_remaining} free conversions</strong> to get started.</p>
    <p><a href="{current_app.config['APP_URL']}">Start Converting Now</a></p>
    <p>Best regards,<br>The {current_app.config['APP_NAME']} Team</p>
    '''
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send welcome email: {str(e)}')
        return False


# Rate limiting storage (in production, use Redis)
_rate_limit_storage = {}


def generate_verification_token(user_id: int) -> str:
    """Generate email verification token."""
    token = secrets.token_hex(16)  # 32 character hex string
    
    # Hash the token for storage
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Store in database
    verification_token = EmailVerificationToken(
        account_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.session.add(verification_token)
    db.session.commit()
    
    return token


def verify_token(token: str, token_type: str) -> Tuple[bool, Optional[int]]:
    """Verify a token and return user_id if valid."""
    try:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        if token_type == 'email_verification':
            db_token = EmailVerificationToken.query.filter_by(
                token_hash=token_hash,
                verified=False
            ).first()
            
            if db_token and db_token.expires_at > datetime.utcnow():
                return True, db_token.account_id
                
        elif token_type == 'password_reset':
            db_token = PasswordResetToken.query.filter_by(
                token_hash=token_hash,
                used=False
            ).first()
            
            if db_token and db_token.expires_at > datetime.utcnow():
                return True, db_token.account_id
        
        return False, None
        
    except Exception as e:
        current_app.logger.error(f'Token verification error: {str(e)}')
        return False, None


def hash_password_reset_token(token: str) -> str:
    """Hash password reset token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_password_reset_token(token: str) -> Tuple[bool, Optional[int]]:
    """Verify password reset token."""
    return verify_token(token, 'password_reset')


def is_safe_url(target: str) -> bool:
    """Check if URL is safe for redirects."""
    if not target:
        return False
        
    # Parse the URL
    try:
        parsed = urllib.parse.urlparse(target)
    except ValueError:
        return False
    
    # Reject dangerous schemes
    if parsed.scheme in ('javascript', 'data', 'vbscript'):
        return False
    
    # Allow relative URLs
    if not parsed.netloc:
        return True
    
    # Check if it's the same domain (if we have request context)
    if request:
        return parsed.netloc in (request.host, '127.0.0.1', 'localhost')
    
    return False


def validate_password_strength(password: str) -> Tuple[bool, list]:
    """Validate password strength."""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    # Check against common passwords
    common_passwords = {
        'password', 'password123', '123456789', 'qwerty123', 
        'admin123', 'password1', 'welcome123', 'passw0rd'
    }
    if password.lower() in common_passwords:
        errors.append("Password is too common")
    
    return len(errors) == 0, errors


def check_rate_limit(client_id: str, max_requests: int = 5, window_minutes: int = 1) -> Tuple[bool, int]:
    """Check if client is within rate limits."""
    current_time = time.time()
    window_seconds = window_minutes * 60
    
    # Clean old entries
    cutoff_time = current_time - window_seconds
    if client_id in _rate_limit_storage:
        _rate_limit_storage[client_id] = [
            timestamp for timestamp in _rate_limit_storage[client_id] 
            if timestamp > cutoff_time
        ]
    else:
        _rate_limit_storage[client_id] = []
    
    # Check current count
    current_count = len(_rate_limit_storage[client_id])
    
    if current_count < max_requests:
        _rate_limit_storage[client_id].append(current_time)
        return True, max_requests - current_count - 1
    else:
        return False, 0


def sanitize_input(input_text: str) -> str:
    """Sanitize input to prevent XSS."""
    if not input_text:
        return input_text
    
    # Remove dangerous HTML tags and attributes
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>',
        r'<link[^>]*>',
        r'<meta[^>]*>',
        r'on\w+\s*=\s*["\'][^"\']*["\']',  # onclick, onerror, etc.
        r'javascript:',
        r'vbscript:',
        r'data:text/html'
    ]
    
    sanitized = input_text
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    return sanitized


def detect_sql_injection(input_text: str) -> bool:
    """Detect potential SQL injection attempts."""
    if not input_text:
        return False
    
    # Common SQL injection patterns
    sql_patterns = [
        r"('|(\\'))+.*(or|and)\s*.*(=|like)",
        r"('|(\\'))+.*union\s+select",
        r"('|(\\'))+.*drop\s+table",
        r"('|(\\'))+.*insert\s+into",
        r"('|(\\'))+.*delete\s+from",
        r"('|(\\'))+.*update\s+.*set",
        r"('|(\\'))+.*create\s+table",
        r"--+.*",  # SQL comments
        r"/\*.*\*/",  # Multi-line comments
        r";\s*(drop|delete|insert|update|create|alter)",
    ]
    
    input_lower = input_text.lower()
    
    for pattern in sql_patterns:
        if re.search(pattern, input_lower, re.IGNORECASE):
            return True
    
    return False


def validate_email_format(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email format."""
    if not email:
        return False, "Email is required"
    
    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    # Additional checks
    if '..' in email:
        return False, "Email cannot contain consecutive dots"
    
    if email.startswith('.') or email.endswith('.'):
        return False, "Email cannot start or end with a dot"
    
    if '@' not in email or email.count('@') != 1:
        return False, "Email must contain exactly one @ symbol"
    
    local, domain = email.rsplit('@', 1)
    
    if len(local) > 64:
        return False, "Email local part too long"
    
    if len(domain) > 255:
        return False, "Email domain too long"
    
    return True, None


def generate_secure_filename(filename: str) -> str:
    """Generate secure filename."""
    if not filename:
        return 'file'
    
    # Use werkzeug's secure_filename as base
    safe_filename = secure_filename(filename)
    
    # Additional security measures
    # Remove any remaining dangerous characters
    safe_filename = re.sub(r'[<>:"|?*]', '', safe_filename)
    
    # Handle Windows reserved names
    windows_reserved = {
        'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 
        'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 
        'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    name_part = safe_filename.rsplit('.', 1)[0] if '.' in safe_filename else safe_filename
    if name_part.upper() in windows_reserved:
        safe_filename = f'file_{safe_filename}'
    
    # Ensure we have a filename
    if not safe_filename or safe_filename == '.':
        safe_filename = 'file'
    
    return safe_filename
