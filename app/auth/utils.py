# app/auth/utils.py
"""Authentication utilities."""

import secrets
import hashlib
from datetime import datetime, timedelta
from flask import url_for, current_app, request
from flask_mail import Message
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
