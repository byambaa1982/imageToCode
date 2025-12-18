# app/health.py
"""Health check utilities for monitoring database and application status."""

import time
from flask import Blueprint, jsonify, current_app
from app.database import test_db_connection, get_db_connection_info
from app.extensions import db

health = Blueprint('health', __name__)


@health.route('/health')
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time()
    })


@health.route('/health/db')
def database_health():
    """Database health check endpoint."""
    start_time = time.time()
    
    try:
        # Test database connection
        is_connected = test_db_connection()
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        if is_connected:
            # Get connection pool information
            conn_info = get_db_connection_info()
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'response_time_ms': round(response_time, 2),
                'connection_pool': conn_info,
                'timestamp': time.time()
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'response_time_ms': round(response_time, 2),
                'timestamp': time.time()
            }), 503
            
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        current_app.logger.error(f"Database health check failed: {e}")
        
        return jsonify({
            'status': 'unhealthy',
            'database': 'error',
            'error': str(e),
            'response_time_ms': round(response_time, 2),
            'timestamp': time.time()
        }), 503


@health.route('/health/detailed')
def detailed_health():
    """Detailed health check including all services."""
    start_time = time.time()
    health_status = {
        'status': 'healthy',
        'checks': {},
        'timestamp': time.time()
    }
    
    overall_healthy = True
    
    # Database check
    try:
        db_start = time.time()
        db_connected = test_db_connection()
        db_time = (time.time() - db_start) * 1000
        
        if db_connected:
            conn_info = get_db_connection_info()
            health_status['checks']['database'] = {
                'status': 'healthy',
                'response_time_ms': round(db_time, 2),
                'connection_pool': conn_info
            }
        else:
            health_status['checks']['database'] = {
                'status': 'unhealthy',
                'response_time_ms': round(db_time, 2),
                'error': 'Connection failed'
            }
            overall_healthy = False
            
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_healthy = False
    
    # Redis/Celery check (if available)
    try:
        from app.celery_app import celery
        from celery import current_app as celery_app
        
        # Try to ping Redis through Celery
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            health_status['checks']['celery'] = {
                'status': 'healthy',
                'workers': len(stats) if stats else 0
            }
        else:
            health_status['checks']['celery'] = {
                'status': 'unhealthy',
                'error': 'No workers available'
            }
            overall_healthy = False
            
    except Exception as e:
        health_status['checks']['celery'] = {
            'status': 'unknown',
            'error': str(e)
        }
    
    # Application check
    try:
        health_status['checks']['application'] = {
            'status': 'healthy',
            'version': getattr(current_app.config, 'VERSION', 'unknown'),
            'environment': current_app.config.get('ENV', 'unknown')
        }
    except Exception as e:
        health_status['checks']['application'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_healthy = False
    
    # Set overall status
    health_status['status'] = 'healthy' if overall_healthy else 'unhealthy'
    health_status['response_time_ms'] = round((time.time() - start_time) * 1000, 2)
    
    status_code = 200 if overall_healthy else 503
    return jsonify(health_status), status_code


def register_health_blueprint(app):
    """Register health check blueprint with the Flask app."""
    app.register_blueprint(health, url_prefix='/api')
