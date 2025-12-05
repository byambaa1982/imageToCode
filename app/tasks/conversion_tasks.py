# app/tasks/conversion_tasks.py
"""Conversion background tasks."""

from datetime import datetime, timedelta
from app.celery_app import make_celery
from app.extensions import db
from app.models import Conversion


# Celery will be initialized from app.py
celery = None


def cleanup_expired_conversions():
    """Clean up expired conversions (placeholder)."""
    # This will be implemented in Phase 2
    pass
