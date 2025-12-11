# app/security.py
"""Security utilities and middleware."""

import re
import logging
from functools import wraps
from flask import request, abort, current_app, session, session
from werkzeug.exceptions import TooManyRequests
import secrets

logger = logging.getLogger(__name__)


# Security headers middleware
def add_security_headers(response):
    """Add security headers to response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://js.stripe.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https:; "
        "font-src 'self' data: https://cdn.jsdelivr.net; "
        "connect-src 'self' https://api.openai.com https://api.anthropic.com https://api.stripe.com; "
        "frame-src https://js.stripe.com;"
    )
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response


def sanitize_filename(filename):
    """
    Sanitize filename to prevent path traversal attacks.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = filename.replace('\\', '/').split('/')[-1]
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\s\-\.]', '', filename)
    
    # Remove multiple dots
    filename = re.sub(r'\.{2,}', '.', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename or 'unnamed'


def validate_file_type(filename, allowed_extensions=None):
    """
    Validate file extension.
    
    Args:
        filename: Filename to validate
        allowed_extensions: Set of allowed extensions
        
    Returns:
        True if valid, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_image_content(file_stream):
    """
    Validate image file content to prevent malicious uploads.
    
    Args:
        file_stream: File stream to validate
        
    Returns:
        True if valid image, False otherwise
    """
    try:
        from PIL import Image
        import io
        
        # Read file
        file_bytes = file_stream.read()
        file_stream.seek(0)  # Reset stream
        
        # Try to open as image
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()
        
        return True
    except Exception as e:
        logger.warning(f"Invalid image content: {str(e)}")
        return False


def check_sql_injection(text):
    """
    Basic SQL injection pattern detection.
    
    Args:
        text: Text to check
        
    Returns:
        True if suspicious patterns found
    """
    if not text:
        return False
    
    dangerous_patterns = [
        r'(\bSELECT\b.*\bFROM\b)',
        r'(\bINSERT\b.*\bINTO\b)',
        r'(\bUPDATE\b.*\bSET\b)',
        r'(\bDELETE\b.*\bFROM\b)',
        r'(\bDROP\b.*\bTABLE\b)',
        r'(;\s*DROP\b)',
        r'(\bEXEC\b|\bEXECUTE\b)',
        r'(--|\#|\/\*)',
        r'(\bUNION\b.*\bSELECT\b)',
    ]
    
    text_upper = text.upper()
    for pattern in dangerous_patterns:
        if re.search(pattern, text_upper, re.IGNORECASE):
            return True
    
    return False


def check_xss(text):
    """
    Basic XSS pattern detection.
    
    Args:
        text: Text to check
        
    Returns:
        True if suspicious patterns found
    """
    if not text:
        return False
    
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def validate_input(text, max_length=1000, check_injections=True):
    """
    Validate user input for security issues.
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
        check_injections: Whether to check for injection attacks
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        return True, None
    
    # Check length
    if len(text) > max_length:
        return False, f"Input too long (max {max_length} characters)"
    
    # Check for injection attempts
    if check_injections:
        if check_sql_injection(text):
            logger.warning(f"Potential SQL injection attempt: {text[:100]}")
            return False, "Invalid input detected"
        
        if check_xss(text):
            logger.warning(f"Potential XSS attempt: {text[:100]}")
            return False, "Invalid input detected"
    
    return True, None


def require_admin(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        
        if not current_user.is_authenticated:
            abort(401)
        
        if not current_user.is_admin:
            logger.warning(f"Non-admin user {current_user.id} attempted to access admin route")
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_verified_email(f):
    """Decorator to require verified email."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        from flask import flash, redirect, url_for
        
        if not current_user.is_authenticated:
            abort(401)
        
        if not current_user.email_verified:
            flash('Please verify your email address to access this feature.', 'warning')
            return redirect(url_for('account.dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_credits(amount=1.0):
    """Decorator to require minimum credits."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_login import current_user
            from flask import flash, redirect, url_for
            
            if not current_user.is_authenticated:
                abort(401)
            
            if not current_user.has_credits(amount):
                flash(f'Insufficient credits. You need at least {amount} credits.', 'error')
                return redirect(url_for('payment.pricing'))
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


class IPWhitelist:
    """IP whitelist middleware."""
    
    def __init__(self, whitelist=None):
        """Initialize with whitelist."""
        self.whitelist = whitelist or []
    
    def is_allowed(self, ip):
        """Check if IP is allowed."""
        if not self.whitelist:
            return True
        return ip in self.whitelist
    
    def __call__(self, f):
        """Decorator."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_allowed(request.remote_addr):
                logger.warning(f"Blocked access from {request.remote_addr}")
                abort(403)
            return f(*args, **kwargs)
        return decorated_function


def generate_csrf_token():
    """Generate a CSRF token."""
    token = secrets.token_urlsafe(32)
    session['csrf_token'] = token
    return token


def validate_csrf_token(token):
    """Validate CSRF token."""
    session_token = session.get('csrf_token')
    if not session_token:
        return False
    
    return session_token == token


def get_csrf_token():
    """Get current CSRF token or generate new one."""
    token = session.get('csrf_token')
    if not token:
        token = generate_csrf_token()
    return token


def csrf_protect():
    """Decorator to protect routes with CSRF token validation."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == 'POST':
                token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
                if not token or not validate_csrf_token(token):
                    current_app.logger.warning(f'CSRF token validation failed for {request.endpoint}')
                    return 'CSRF token validation failed', 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def init_security(app):
    """Initialize security features."""
    
    # Add security headers to all responses
    @app.after_request
    def after_request(response):
        return add_security_headers(response)
    
    # Log suspicious activity
    @app.before_request
    def before_request():
        # Check for suspicious patterns in query parameters
        for key, value in request.args.items():
            if check_sql_injection(value) or check_xss(value):
                logger.warning(
                    f"Suspicious request from {request.remote_addr}: "
                    f"{request.method} {request.path} - {key}={value[:100]}"
                )
                abort(400)
    
    logger.info("Security middleware initialized")
