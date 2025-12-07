# celeryconfig.py
"""Celery configuration."""

import os

# Broker settings
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Task settings
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Task execution settings
task_acks_late = True
task_reject_on_worker_lost = True
task_track_started = True
task_time_limit = 300  # 5 minutes
task_soft_time_limit = 240  # 4 minutes

# Worker settings
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000

# Result backend settings
result_expires = 3600  # 1 hour

# Task routes
task_routes = {
    'app.tasks.conversion_tasks.*': {'queue': 'conversions'},
    'app.tasks.email_tasks.*': {'queue': 'emails'},
    'app.tasks.analytics_tasks.*': {'queue': 'analytics'},
}

# Include tasks
include = [
    'app.tasks.conversion_tasks',
    'app.tasks.email_tasks',
    'app.tasks.analytics_tasks',
]

# Beat schedule (for periodic tasks)
beat_schedule = {
    'cleanup-expired-conversions': {
        'task': 'app.tasks.conversion_tasks.cleanup_expired_conversions',
        'schedule': 3600.0,  # Every hour
    },
    'cleanup-expired-tokens': {
        'task': 'app.tasks.email_tasks.cleanup_expired_tokens',
        'schedule': 86400.0,  # Every day
    },
}
