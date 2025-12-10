# app/cache.py
"""Caching utilities for the application."""

import json
import logging
from functools import wraps
from typing import Any, Optional
from flask import current_app
from app.extensions import cache

logger = logging.getLogger(__name__)


def cache_key(*args, **kwargs):
    """Generate a cache key from arguments."""
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
    return ":".join(key_parts)


def cached(timeout=300, key_prefix="cache"):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds (default 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            cache_key_str = f"{key_prefix}:{f.__name__}:{cache_key(*args, **kwargs)}"
            
            try:
                # Try to get from cache
                cached_value = cache.get(cache_key_str)
                if cached_value is not None:
                    logger.debug(f"Cache hit for key: {cache_key_str}")
                    return json.loads(cached_value) if isinstance(cached_value, str) else cached_value
                
                # Execute function
                result = f(*args, **kwargs)
                
                # Cache result
                if result is not None:
                    cache.set(cache_key_str, json.dumps(result) if not isinstance(result, (str, int, float, bool)) else result, timeout=timeout)
                    logger.debug(f"Cached result for key: {cache_key_str}")
                
                return result
            except Exception as e:
                logger.error(f"Cache error for {cache_key_str}: {str(e)}")
                # Fall back to executing function without caching
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def invalidate_cache(key_pattern: str):
    """
    Invalidate cache entries matching a pattern.
    
    Args:
        key_pattern: Pattern to match cache keys (e.g., "user:*")
    """
    try:
        cache.delete_many(key_pattern)
        logger.info(f"Invalidated cache for pattern: {key_pattern}")
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {str(e)}")


def get_or_set_cache(key: str, factory_func, timeout=300) -> Any:
    """
    Get value from cache or set it using factory function.
    
    Args:
        key: Cache key
        factory_func: Function to call if cache miss
        timeout: Cache timeout in seconds
        
    Returns:
        Cached or freshly computed value
    """
    try:
        cached_value = cache.get(key)
        if cached_value is not None:
            logger.debug(f"Cache hit for key: {key}")
            return json.loads(cached_value) if isinstance(cached_value, str) else cached_value
        
        # Compute value
        value = factory_func()
        
        # Cache it
        if value is not None:
            cache.set(key, json.dumps(value) if not isinstance(value, (str, int, float, bool)) else value, timeout=timeout)
            logger.debug(f"Cached result for key: {key}")
        
        return value
    except Exception as e:
        logger.error(f"Cache error for {key}: {str(e)}")
        return factory_func()


class CacheManager:
    """Manager for common cache operations."""
    
    @staticmethod
    def get_user_stats(user_id: int, force_refresh=False):
        """Get cached user statistics."""
        key = f"user:stats:{user_id}"
        
        if force_refresh:
            cache.delete(key)
        
        def compute_stats():
            from app.models import Conversion, Order
            from app.extensions import db
            from sqlalchemy import func
            
            # Get conversion stats
            conversion_stats = db.session.query(
                func.count(Conversion.id).label('total'),
                func.sum(func.case((Conversion.status == 'completed', 1), else_=0)).label('completed'),
                func.sum(func.case((Conversion.status == 'failed', 1), else_=0)).label('failed')
            ).filter(
                Conversion.account_id == user_id,
                Conversion.deleted_at.is_(None)
            ).first()
            
            # Get order stats
            order_stats = db.session.query(
                func.count(Order.id).label('total'),
                func.coalesce(func.sum(Order.amount), 0).label('total_spent')
            ).filter(
                Order.account_id == user_id,
                Order.status == 'completed'
            ).first()
            
            return {
                'conversions': {
                    'total': conversion_stats.total or 0,
                    'completed': conversion_stats.completed or 0,
                    'failed': conversion_stats.failed or 0
                },
                'orders': {
                    'total': order_stats.total or 0,
                    'total_spent': float(order_stats.total_spent or 0)
                }
            }
        
        return get_or_set_cache(key, compute_stats, timeout=60)
    
    @staticmethod
    def get_packages(force_refresh=False):
        """Get cached active packages."""
        key = "packages:active"
        
        if force_refresh:
            cache.delete(key)
        
        def compute_packages():
            from app.models import Package
            
            packages = Package.query.filter_by(
                is_active=True
            ).order_by(Package.display_order).all()
            
            return [{
                'id': p.id,
                'code': p.code,
                'name': p.name,
                'description': p.description,
                'price': float(p.price),
                'credits': float(p.credits),
                'is_featured': p.is_featured,
                'badge': p.badge
            } for p in packages]
        
        return get_or_set_cache(key, compute_packages, timeout=600)
    
    @staticmethod
    def get_framework_list(force_refresh=False):
        """Get cached list of available frameworks."""
        key = "frameworks:list"
        
        if force_refresh:
            cache.delete(key)
        
        def compute_frameworks():
            return [
                {'value': 'react', 'label': 'React', 'description': 'Modern React with Hooks'},
                {'value': 'vue', 'label': 'Vue.js', 'description': 'Vue 3 Composition API'},
                {'value': 'html', 'label': 'HTML/CSS/JS', 'description': 'Plain HTML with JavaScript'},
                {'value': 'svelte', 'label': 'Svelte', 'description': 'Svelte 4'},
                {'value': 'angular', 'label': 'Angular', 'description': 'Angular 17+'}
            ]
        
        return get_or_set_cache(key, compute_frameworks, timeout=3600)
    
    @staticmethod
    def invalidate_user_cache(user_id: int):
        """Invalidate all cache entries for a user."""
        patterns = [
            f"user:stats:{user_id}",
            f"user:conversions:{user_id}:*",
            f"user:orders:{user_id}:*"
        ]
        for pattern in patterns:
            invalidate_cache(pattern)
