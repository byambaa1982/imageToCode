# app/launch/middleware.py
"""Launch tracking middleware."""

import logging
from datetime import datetime
from flask import request, g, session
from app.models import AnalyticsEvent
from app.extensions import db
from app.launch.utils import track_launch_event

logger = logging.getLogger(__name__)


class LaunchTrackingMiddleware:
    """Middleware to track launch metrics automatically."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Track page views and unique visitors."""
        # Skip tracking for static files and API endpoints
        if (request.endpoint and 
            (request.endpoint.startswith('static') or 
             request.endpoint.startswith('api.') or
             request.path.startswith('/static/'))):
            return
        
        # Track page view
        try:
            track_launch_event('page_view', {
                'path': request.path,
                'method': request.method,
                'referrer': request.referrer,
                'user_agent': request.headers.get('User-Agent')
            })
            
            # Check if unique visitor (simple session-based tracking)
            if 'visitor_tracked' not in session:
                track_launch_event('unique_visitor', {
                    'path': request.path,
                    'referrer': request.referrer
                })
                session['visitor_tracked'] = True
                session.permanent = True
        
        except Exception as e:
            logger.error(f'Error tracking launch metrics: {str(e)}')
    
    def after_request(self, response):
        """Track response metrics."""
        # Skip tracking for static files
        if (request.endpoint and 
            (request.endpoint.startswith('static') or 
             request.path.startswith('/static/'))):
            return response
        
        try:
            # Track errors
            if response.status_code >= 400:
                track_launch_event('error', {
                    'status_code': response.status_code,
                    'path': request.path,
                    'method': request.method
                })
        
        except Exception as e:
            logger.error(f'Error tracking response metrics: {str(e)}')
        
        return response


def init_launch_tracking(app):
    """Initialize launch tracking middleware."""
    middleware = LaunchTrackingMiddleware(app)
    app.logger.info('Launch tracking middleware initialized')
