# app/tasks/email_tasks.py
"""Email background tasks."""

from datetime import datetime, timedelta
from app.extensions import db
from app.models import PasswordResetToken, EmailVerificationToken


def cleanup_expired_tokens():
    """Clean up expired tokens (placeholder)."""
    # This will be implemented in Phase 2
    pass
