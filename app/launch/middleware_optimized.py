# app/launch/middleware_optimized.py
"""Optimized launch tracking middleware with reduced database overhead."""

import logging
from datetime import datetime, date
from collections import defaultdict
from threading import Lock, Timer
from flask import request, session

logger = logging.getLogger(__name__)


class OptimizedLaunchTrackingMiddleware:
    """Optimized middleware to track launch metrics with minimal DB overhead."""
    
    def __init__(self, app=None):
        self.app = app
        self.batch_data = defaultdict(int)
        self.batch_lock = Lock()
        self.batch_timer = None
        self.batch_interval = 30  # Batch every 30 seconds
        self.skip_paths = {'/static/', '/favicon', '/health', '/ping'}
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app."""
        app.before_request(self.before_request)
    
    def should_skip_tracking(self):
        """Check if we should skip tracking for this request."""
        if not request.endpoint:
            return True
        
        # Skip static files, API health checks, etc.
        if (request.endpoint.startswith('static') or 
            request.endpoint.startswith('api.health') or
            any(skip_path in request.path for skip_path in self.skip_paths)):
            return True
        
        return False
    
    def before_request(self):
        """Track page views with minimal overhead."""
        if self.should_skip_tracking():
            return
        
        try:
            with self.batch_lock:
                # Batch page views instead of individual DB writes
                self.batch_data['page_views'] += 1
                
                # Check if unique visitor (simple session-based tracking)
                if 'visitor_tracked' not in session:
                    self.batch_data['unique_visitors'] += 1
                    session['visitor_tracked'] = True
                    session.permanent = True
                
                # Start batch timer if not already running
                if not self.batch_timer:
                    self._start_batch_timer()
        
        except Exception as e:
            logger.error(f'Error tracking launch metrics: {str(e)}', exc_info=False)
    
    def _start_batch_timer(self):
        """Start the batch processing timer (called with lock held)."""
        self.batch_timer = Timer(self.batch_interval, self._process_batch)
        self.batch_timer.daemon = True
        self.batch_timer.start()
    
    def _process_batch(self):
        """Process batched metrics in background."""
        if not self.batch_data:
            with self.batch_lock:
                self.batch_timer = None
            return
        
        try:
            # Get current batch data and clear it
            with self.batch_lock:
                batch_copy = dict(self.batch_data)
                self.batch_data.clear()
                self.batch_timer = None
            
            if not batch_copy:
                return
            
            # Process in app context
            if self.app:
                with self.app.app_context():
                    self._update_database_metrics(batch_copy)
        
        except Exception as e:
            logger.error(f'Error processing batch metrics: {str(e)}', exc_info=False)
    
    def _update_database_metrics(self, batch_data):
        """Update database with batched metrics."""
        try:
            from app.models import LaunchMetric
            from app.extensions import db
            
            today = date.today()
            metrics = LaunchMetric.query.filter_by(date=today).first()
            
            if not metrics:
                metrics = LaunchMetric(date=today)
                db.session.add(metrics)
            
            # Apply batched data
            metrics.page_views += batch_data.get('page_views', 0)
            metrics.unique_visitors += batch_data.get('unique_visitors', 0)
            
            db.session.commit()
            logger.debug(f"Processed batch metrics: {batch_data}")
        
        except Exception as e:
            logger.error(f'Error updating database metrics: {str(e)}')
            try:
                db.session.rollback()
            except:
                pass


def init_optimized_launch_tracking(app):
    """Initialize optimized launch tracking middleware."""
    # Only enable in production or when explicitly requested
    if app.config.get('ENABLE_LAUNCH_TRACKING', app.config.get('ENV') == 'production'):
        middleware = OptimizedLaunchTrackingMiddleware(app)
        app.logger.info('Optimized launch tracking middleware initialized')
    else:
        app.logger.info('Launch tracking disabled in development mode')
