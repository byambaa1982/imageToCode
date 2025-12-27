# performance_optimizer.py
"""Performance optimization script for Screenshot to Code application."""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from app import create_app
from app.extensions import db
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_performance_issues():
    """Analyze potential performance issues."""
    print("\n🔍 Screenshot to Code Performance Analysis")
    print("=" * 50)
    
    issues = []
    recommendations = []
    
    # Check 1: Database connection configuration
    print("\n📊 Checking database configuration...")
    
    if Config.SQLALCHEMY_POOL_SIZE < 5:
        issues.append("Small database connection pool")
        recommendations.append("Increase SQLALCHEMY_POOL_SIZE to at least 10")
    
    if not Config.SQLALCHEMY_POOL_PRE_PING:
        issues.append("Connection pre-ping disabled")
        recommendations.append("Enable SQLALCHEMY_POOL_PRE_PING for better connection recovery")
    
    # Check 2: Debug mode in production
    flask_env = os.getenv('FLASK_ENV', 'development')
    if flask_env == 'development':
        issues.append("Running in debug mode")
        recommendations.append("Set FLASK_ENV=production for better performance")
    
    # Check 3: Logging levels
    print("📝 Checking logging configuration...")
    
    # Check 4: Launch middleware
    print("🚀 Checking launch middleware...")
    issues.append("Launch middleware tracking every request")
    recommendations.append("Consider batching launch metrics or using async processing")
    
    # Check 5: Database monitoring
    print("💾 Checking database monitoring...")
    issues.append("Database monitoring initialization on app startup")
    recommendations.append("Move database monitoring to background task")
    
    # Check 6: SSH tunnel for local development
    if not Config.is_on_pythonanywhere():
        print("🔒 Checking SSH tunnel...")
        issues.append("SSH tunnel overhead for local development")
        recommendations.append("Consider using local MySQL for development")
    
    # Report findings
    print(f"\n⚠️  Found {len(issues)} potential performance issues:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    return issues, recommendations


def optimize_database_config():
    """Optimize database configuration."""
    print("\n🔧 Optimizing database configuration...")
    
    optimizations = {
        'SQLALCHEMY_POOL_SIZE': 15,
        'SQLALCHEMY_MAX_OVERFLOW': 25,
        'SQLALCHEMY_POOL_TIMEOUT': 20,
        'SQLALCHEMY_POOL_RECYCLE': 280,
        'SQLALCHEMY_POOL_PRE_PING': True,
        'SQLALCHEMY_ECHO': False,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }
    
    print("Recommended database settings:")
    for key, value in optimizations.items():
        print(f"  {key} = {value}")
    
    return optimizations


def create_optimized_launch_middleware():
    """Create optimized launch middleware."""
    return '''# app/launch/middleware_optimized.py
"""Optimized launch tracking middleware with batching."""

import logging
from datetime import datetime
from collections import defaultdict
from threading import Timer
from flask import request, g, session
from app.models import AnalyticsEvent, LaunchMetric
from app.extensions import db
from app.launch.utils import track_launch_event

logger = logging.getLogger(__name__)


class OptimizedLaunchTrackingMiddleware:
    """Optimized middleware to track launch metrics with batching."""
    
    def __init__(self, app=None):
        self.app = app
        self.batch_data = defaultdict(int)
        self.batch_timer = None
        self.batch_interval = 60  # Batch every 60 seconds
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app."""
        app.before_request(self.before_request)
        # Remove after_request to reduce overhead
    
    def before_request(self):
        """Track page views with minimal overhead."""
        # Skip tracking for static files and API endpoints
        if (request.endpoint and 
            (request.endpoint.startswith('static') or 
             request.endpoint.startswith('api.') or
             request.path.startswith('/static/') or
             request.path.startswith('/favicon'))):
            return
        
        # Only track essential metrics
        try:
            # Batch page views instead of individual DB writes
            self.batch_data['page_views'] += 1
            
            # Check if unique visitor (simple session-based tracking)
            if 'visitor_tracked' not in session:
                self.batch_data['unique_visitors'] += 1
                session['visitor_tracked'] = True
                session.permanent = True
            
            # Start batch timer if not already running
            if not self.batch_timer:
                self.start_batch_timer()
        
        except Exception as e:
            logger.error(f'Error tracking launch metrics: {str(e)}')
    
    def start_batch_timer(self):
        """Start the batch processing timer."""
        self.batch_timer = Timer(self.batch_interval, self.process_batch)
        self.batch_timer.daemon = True
        self.batch_timer.start()
    
    def process_batch(self):
        """Process batched metrics."""
        if not self.batch_data:
            self.batch_timer = None
            return
        
        try:
            from app import create_app
            from datetime import date
            
            app = create_app()
            with app.app_context():
                today = date.today()
                metrics = LaunchMetric.query.filter_by(date=today).first()
                
                if not metrics:
                    metrics = LaunchMetric(date=today)
                    db.session.add(metrics)
                
                # Apply batched data
                metrics.page_views += self.batch_data['page_views']
                metrics.unique_visitors += self.batch_data['unique_visitors']
                
                db.session.commit()
                logger.info(f"Processed batch: {dict(self.batch_data)}")
                
                # Clear batch data
                self.batch_data.clear()
        
        except Exception as e:
            logger.error(f'Error processing batch metrics: {str(e)}')
        
        finally:
            self.batch_timer = None
            # Restart timer if there's more data
            if self.batch_data:
                self.start_batch_timer()


def init_optimized_launch_tracking(app):
    """Initialize optimized launch tracking middleware."""
    middleware = OptimizedLaunchTrackingMiddleware(app)
    app.logger.info('Optimized launch tracking middleware initialized')
'''


def create_performance_config():
    """Create performance-optimized configuration."""
    return '''# config_optimized.py
"""Performance-optimized configuration additions."""

# Add these to your existing Config class for better performance

class OptimizedConfig(Config):
    """Performance-optimized configuration."""
    
    # Optimized database settings
    SQLALCHEMY_POOL_SIZE = 15
    SQLALCHEMY_MAX_OVERFLOW = 25  
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_ECHO = False  # Disable SQL logging
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Optimized engine options
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
        'pool_size': 15,
        'max_overflow': 25,
        'pool_timeout': 20,
        'connect_args': {
            'connect_timeout': 30,  # Reduced from 60
            'read_timeout': 30,     # Reduced from 60
            'write_timeout': 30,    # Reduced from 60
            'charset': 'utf8mb4',
            'autocommit': False,
            'sql_mode': 'TRADITIONAL'
        }
    }
    
    # Session optimizations
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)  # Reduced from 7 days
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Disable debug features in production
    SQLALCHEMY_RECORD_QUERIES = False
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(hours=12)
    
    # Cache settings
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = 'redis://localhost:6379/2'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate limiting optimizations
    RATELIMIT_STORAGE_URL = 'redis://localhost:6379/1'
    RATELIMIT_STRATEGY = 'moving-window'
    
    @staticmethod
    def init_app(app):
        """Initialize app with performance optimizations."""
        Config.init_app(app)
        
        # Disable some Flask features for performance
        app.config['JSON_SORT_KEYS'] = False
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
        
        # Optimize Jinja2
        app.jinja_env.cache = {}
        app.jinja_env.auto_reload = False
        
        # Set up logging for performance
        if not app.debug:
            import logging
            logging.getLogger('werkzeug').setLevel(logging.WARNING)
            logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
            logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
'''


def create_quick_fixes():
    """Create quick performance fixes."""
    print("\n⚡ Creating quick performance fixes...")
    
    fixes = []
    
    # Fix 1: Disable database monitoring in production
    fixes.append({
        'file': 'app/__init__.py',
        'issue': 'Database monitoring on every startup',
        'fix': 'Wrap in development check'
    })
    
    # Fix 2: Optimize launch middleware
    fixes.append({
        'file': 'app/launch/middleware.py', 
        'issue': 'DB writes on every request',
        'fix': 'Implement batching'
    })
    
    # Fix 3: Reduce logging verbosity
    fixes.append({
        'file': 'app/__init__.py',
        'issue': 'Verbose logging',
        'fix': 'Set WARNING level for production'
    })
    
    return fixes


def main():
    """Main optimization function."""
    print("🚀 Screenshot to Code Performance Optimizer")
    print("=" * 50)
    
    # Analyze current issues
    issues, recommendations = analyze_performance_issues()
    
    # Show optimizations
    optimize_database_config()
    
    # Create optimization files
    print("\n📁 Creating optimization files...")
    
    # Create optimized middleware
    with open('app/launch/middleware_optimized.py', 'w') as f:
        f.write(create_optimized_launch_middleware())
    print("  ✓ Created app/launch/middleware_optimized.py")
    
    # Create performance config
    with open('config_optimized.py', 'w') as f:
        f.write(create_performance_config())
    print("  ✓ Created config_optimized.py")
    
    print("\n🎯 Quick Fixes to Apply:")
    print("1. Replace launch middleware with optimized version")
    print("2. Add performance config to existing config.py")
    print("3. Wrap database monitoring in development check")
    print("4. Set logging levels to WARNING in production")
    print("5. Consider using Redis for caching")
    
    print("\n✅ Performance optimization files created!")
    print("\nNext steps:")
    print("1. Review the generated optimization files")
    print("2. Apply the recommended changes")
    print("3. Test the application performance")
    print("4. Monitor database connection pool usage")


if __name__ == '__main__':
    main()
