# app/launch/utils.py
"""Launch management utilities."""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal

from flask import request, current_app
from app.extensions import db
from app.models import PromoCode, LaunchMetric, AnalyticsEvent

logger = logging.getLogger(__name__)


def track_launch_event(event_type, event_data=None):
    """Track launch-specific events."""
    try:
        # Create analytics event
        event = AnalyticsEvent(
            event_type=f'launch_{event_type}',
            event_data=event_data or {},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            session_id=request.cookies.get('session')
        )
        db.session.add(event)
        
        # Update daily metrics
        today = date.today()
        metrics = LaunchMetric.query.filter_by(date=today).first()
        
        if not metrics:
            metrics = LaunchMetric(date=today)
            db.session.add(metrics)
        
        # Update specific counters based on event type
        if event_type == 'page_view':
            metrics.page_views += 1
        elif event_type == 'unique_visitor':
            metrics.unique_visitors += 1
        elif event_type == 'signup':
            metrics.signups += 1
        elif event_type == 'conversion_started':
            metrics.conversions_started += 1
        elif event_type == 'conversion_completed':
            metrics.conversions_completed += 1
        elif event_type == 'download':
            metrics.downloads += 1
        elif event_type == 'order':
            metrics.orders += 1
            if event_data and 'amount' in event_data:
                metrics.revenue += Decimal(str(event_data['amount']))
        elif event_type == 'product_hunt_visit':
            metrics.product_hunt_clicks += 1
        elif event_type == 'reddit_visit':
            metrics.reddit_clicks += 1
        elif event_type == 'twitter_visit':
            metrics.twitter_clicks += 1
        elif event_type == 'promo_code_redeemed':
            metrics.promo_code_uses += 1
        elif event_type == 'error':
            metrics.error_count += 1
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error tracking launch event {event_type}: {str(e)}')


def get_launch_dashboard_data():
    """Get comprehensive launch dashboard data."""
    try:
        # Get metrics for the last 7 days
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        metrics = LaunchMetric.query.filter(
            LaunchMetric.date >= start_date,
            LaunchMetric.date <= end_date
        ).order_by(LaunchMetric.date.asc()).all()
        
        # Fill in missing dates with zero metrics
        date_range = [start_date + timedelta(days=i) for i in range(7)]
        metrics_dict = {m.date: m for m in metrics}
        
        daily_data = []
        for d in date_range:
            if d in metrics_dict:
                m = metrics_dict[d]
                daily_data.append({
                    'date': d.isoformat(),
                    'unique_visitors': m.unique_visitors,
                    'signups': m.signups,
                    'conversions': m.conversions_completed,
                    'revenue': float(m.revenue),
                    'errors': m.error_count
                })
            else:
                daily_data.append({
                    'date': d.isoformat(),
                    'unique_visitors': 0,
                    'signups': 0,
                    'conversions': 0,
                    'revenue': 0.0,
                    'errors': 0
                })
        
        # Get total metrics
        total_metrics = db.session.query(
            db.func.sum(LaunchMetric.unique_visitors).label('total_visitors'),
            db.func.sum(LaunchMetric.signups).label('total_signups'),
            db.func.sum(LaunchMetric.conversions_completed).label('total_conversions'),
            db.func.sum(LaunchMetric.revenue).label('total_revenue'),
            db.func.sum(LaunchMetric.promo_code_uses).label('total_promo_uses'),
            db.func.sum(LaunchMetric.error_count).label('total_errors')
        ).filter(
            LaunchMetric.date >= start_date
        ).first()
        
        # Get promo code performance
        promo_codes = PromoCode.query.filter(
            PromoCode.campaign.in_(['product_hunt', 'reddit', 'twitter']),
            PromoCode.is_active == True
        ).all()
        
        promo_data = []
        for promo in promo_codes:
            promo_data.append({
                'code': promo.code,
                'campaign': promo.campaign,
                'uses': promo.uses_count,
                'max_uses': promo.max_uses,
                'discount_type': promo.discount_type,
                'discount_value': float(promo.discount_value),
                'expires_at': promo.expires_at.isoformat() if promo.expires_at else None
            })
        
        # Get recent analytics events
        recent_events = AnalyticsEvent.query.filter(
            AnalyticsEvent.event_type.like('launch_%'),
            AnalyticsEvent.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).order_by(AnalyticsEvent.created_at.desc()).limit(50).all()
        
        events_data = []
        for event in recent_events:
            events_data.append({
                'type': event.event_type.replace('launch_', ''),
                'data': event.event_data,
                'time': event.created_at.isoformat(),
                'ip': event.ip_address
            })
        
        return {
            'daily_metrics': daily_data,
            'totals': {
                'visitors': total_metrics.total_visitors or 0,
                'signups': total_metrics.total_signups or 0,
                'conversions': total_metrics.total_conversions or 0,
                'revenue': float(total_metrics.total_revenue or 0),
                'promo_uses': total_metrics.total_promo_uses or 0,
                'errors': total_metrics.total_errors or 0
            },
            'promo_codes': promo_data,
            'recent_events': events_data,
            'conversion_rate': (total_metrics.total_conversions or 0) / max(total_metrics.total_visitors or 1, 1) * 100,
            'signup_rate': (total_metrics.total_signups or 0) / max(total_metrics.total_visitors or 1, 1) * 100
        }
        
    except Exception as e:
        logger.error(f'Error getting launch dashboard data: {str(e)}')
        return {
            'daily_metrics': [],
            'totals': {'visitors': 0, 'signups': 0, 'conversions': 0, 'revenue': 0, 'promo_uses': 0, 'errors': 0},
            'promo_codes': [],
            'recent_events': [],
            'conversion_rate': 0,
            'signup_rate': 0
        }


def create_launch_promo_codes():
    """Create promo codes for launch campaigns."""
    launch_codes = [
        {
            'code': 'PRODUCTHUNT10',
            'discount_type': 'credits',
            'discount_value': Decimal('10.0'),
            'max_uses': 100,
            'max_uses_per_user': 1,
            'expires_at': datetime.utcnow() + timedelta(days=7),
            'campaign': 'product_hunt',
            'description': 'Product Hunt Launch Special - 10 Free Credits'
        },
        {
            'code': 'REDDIT20',
            'discount_type': 'credits',
            'discount_value': Decimal('20.0'),
            'max_uses': 50,
            'max_uses_per_user': 1,
            'expires_at': datetime.utcnow() + timedelta(days=3),
            'campaign': 'reddit',
            'description': 'Reddit Exclusive - 20 Free Credits'
        },
        {
            'code': 'LAUNCH50',
            'discount_type': 'percentage',
            'discount_value': Decimal('50.0'),
            'max_uses': 200,
            'max_uses_per_user': 1,
            'expires_at': datetime.utcnow() + timedelta(days=14),
            'campaign': 'twitter',
            'description': 'Launch Week Special - 50% Off First Purchase'
        },
        {
            'code': 'EARLY100',
            'discount_type': 'credits',
            'discount_value': Decimal('100.0'),
            'max_uses': 25,
            'max_uses_per_user': 1,
            'expires_at': datetime.utcnow() + timedelta(days=1),
            'campaign': 'early_supporters',
            'description': 'Early Supporters - 100 Free Credits'
        }
    ]
    
    created_codes = []
    
    for code_data in launch_codes:
        # Check if code already exists
        existing = PromoCode.query.filter_by(code=code_data['code']).first()
        
        if not existing:
            promo_code = PromoCode(**code_data)
            db.session.add(promo_code)
            created_codes.append(promo_code)
            logger.info(f'Created promo code: {code_data["code"]}')
        else:
            logger.info(f'Promo code already exists: {code_data["code"]}')
    
    return created_codes


def update_performance_metrics():
    """Update performance metrics for launch monitoring."""
    try:
        today = date.today()
        metrics = LaunchMetric.query.filter_by(date=today).first()
        
        if not metrics:
            metrics = LaunchMetric(date=today)
            db.session.add(metrics)
        
        # In a real implementation, you would:
        # - Query your monitoring service for response times
        # - Check error logs for error counts
        # - Calculate uptime percentage
        
        # For now, we'll set reasonable defaults
        if metrics.avg_response_time == 0:
            metrics.avg_response_time = Decimal('0.250')  # 250ms average
        
        if metrics.uptime_percentage == 100.00:
            metrics.uptime_percentage = Decimal('99.95')  # 99.95% uptime
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error updating performance metrics: {str(e)}')


def get_launch_status():
    """Get current launch status and key metrics."""
    try:
        today = date.today()
        metrics = LaunchMetric.query.filter_by(date=today).first()
        
        if not metrics:
            return {
                'status': 'pre_launch',
                'visitors': 0,
                'signups': 0,
                'conversions': 0,
                'revenue': 0.0
            }
        
        # Determine launch status based on activity
        if metrics.unique_visitors > 100:
            status = 'active_launch'
        elif metrics.unique_visitors > 10:
            status = 'soft_launch'
        else:
            status = 'pre_launch'
        
        return {
            'status': status,
            'visitors': metrics.unique_visitors,
            'signups': metrics.signups,
            'conversions': metrics.conversions_completed,
            'revenue': float(metrics.revenue)
        }
        
    except Exception as e:
        logger.error(f'Error getting launch status: {str(e)}')
        return {
            'status': 'error',
            'visitors': 0,
            'signups': 0,
            'conversions': 0,
            'revenue': 0.0
        }
