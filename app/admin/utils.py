# app/admin/utils.py
"""Admin utility functions."""

from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, and_, or_
from app.extensions import db
from app.models import Account, Conversion, Order, CreditsTransaction, Package


def get_dashboard_stats():
    """Get key performance indicators for admin dashboard."""
    
    # Time ranges
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    # User statistics
    total_users = Account.query.filter_by(deleted_at=None).count()
    users_today = Account.query.filter(
        Account.created_at >= today_start,
        Account.deleted_at.is_(None)
    ).count()
    users_this_week = Account.query.filter(
        Account.created_at >= week_start,
        Account.deleted_at.is_(None)
    ).count()
    users_this_month = Account.query.filter(
        Account.created_at >= month_start,
        Account.deleted_at.is_(None)
    ).count()
    verified_users = Account.query.filter_by(
        email_verified=True,
        deleted_at=None
    ).count()
    admin_users = Account.query.filter_by(
        is_admin=True,
        deleted_at=None
    ).count()
    
    # Conversion statistics
    total_conversions = Conversion.query.filter_by(deleted_at=None).count()
    conversions_today = Conversion.query.filter(
        Conversion.created_at >= today_start,
        Conversion.deleted_at.is_(None)
    ).count()
    conversions_this_week = Conversion.query.filter(
        Conversion.created_at >= week_start,
        Conversion.deleted_at.is_(None)
    ).count()
    conversions_this_month = Conversion.query.filter(
        Conversion.created_at >= month_start,
        Conversion.deleted_at.is_(None)
    ).count()
    
    # Conversion status breakdown
    completed_conversions = Conversion.query.filter_by(
        status='completed',
        deleted_at=None
    ).count()
    failed_conversions = Conversion.query.filter_by(
        status='failed',
        deleted_at=None
    ).count()
    processing_conversions = Conversion.query.filter_by(
        status='processing',
        deleted_at=None
    ).count()
    pending_conversions = Conversion.query.filter_by(
        status='pending',
        deleted_at=None
    ).count()
    
    # Calculate success rate
    if total_conversions > 0:
        success_rate = round((completed_conversions / total_conversions) * 100, 2)
    else:
        success_rate = 0
    
    # Revenue statistics
    total_revenue = db.session.query(
        func.coalesce(func.sum(Order.amount), 0)
    ).filter_by(status='completed').scalar() or Decimal('0')
    
    revenue_today = db.session.query(
        func.coalesce(func.sum(Order.amount), 0)
    ).filter(
        Order.status == 'completed',
        Order.created_at >= today_start
    ).scalar() or Decimal('0')
    
    revenue_this_week = db.session.query(
        func.coalesce(func.sum(Order.amount), 0)
    ).filter(
        Order.status == 'completed',
        Order.created_at >= week_start
    ).scalar() or Decimal('0')
    
    revenue_this_month = db.session.query(
        func.coalesce(func.sum(Order.amount), 0)
    ).filter(
        Order.status == 'completed',
        Order.created_at >= month_start
    ).scalar() or Decimal('0')
    
    # Order statistics
    total_orders = Order.query.filter_by(status='completed').count()
    orders_today = Order.query.filter(
        Order.status == 'completed',
        Order.created_at >= today_start
    ).count()
    orders_this_week = Order.query.filter(
        Order.status == 'completed',
        Order.created_at >= week_start
    ).count()
    orders_this_month = Order.query.filter(
        Order.status == 'completed',
        Order.created_at >= month_start
    ).count()
    
    # Average order value
    if total_orders > 0:
        avg_order_value = float(total_revenue) / total_orders
    else:
        avg_order_value = 0
    
    # Framework popularity
    framework_stats = db.session.query(
        Conversion.framework,
        func.count(Conversion.id).label('count')
    ).filter_by(deleted_at=None).group_by(Conversion.framework).all()
    
    # Average processing time
    avg_processing_time = db.session.query(
        func.avg(Conversion.processing_time)
    ).filter(
        Conversion.status == 'completed',
        Conversion.processing_time.isnot(None)
    ).scalar()
    
    if avg_processing_time:
        avg_processing_time = round(float(avg_processing_time), 2)
    else:
        avg_processing_time = 0
    
    # Total AI costs
    total_ai_cost = db.session.query(
        func.coalesce(func.sum(Conversion.cost), 0)
    ).filter(Conversion.cost.isnot(None)).scalar() or Decimal('0')
    
    return {
        'users': {
            'total': total_users,
            'today': users_today,
            'this_week': users_this_week,
            'this_month': users_this_month,
            'verified': verified_users,
            'admins': admin_users
        },
        'conversions': {
            'total': total_conversions,
            'today': conversions_today,
            'this_week': conversions_this_week,
            'this_month': conversions_this_month,
            'completed': completed_conversions,
            'failed': failed_conversions,
            'processing': processing_conversions,
            'pending': pending_conversions,
            'success_rate': success_rate,
            'avg_processing_time': avg_processing_time
        },
        'revenue': {
            'total': float(total_revenue),
            'today': float(revenue_today),
            'this_week': float(revenue_this_week),
            'this_month': float(revenue_this_month),
            'avg_order_value': round(avg_order_value, 2)
        },
        'orders': {
            'total': total_orders,
            'today': orders_today,
            'this_week': orders_this_week,
            'this_month': orders_this_month
        },
        'frameworks': [
            {'name': f.framework, 'count': f.count} for f in framework_stats
        ],
        'ai_costs': {
            'total': float(total_ai_cost)
        }
    }


def get_user_activity_log(account_id, limit=20):
    """Get recent activity for a specific user."""
    
    activities = []
    
    # Get conversions
    conversions = Conversion.query.filter_by(
        account_id=account_id,
        deleted_at=None
    ).order_by(Conversion.created_at.desc()).limit(limit).all()
    
    for conv in conversions:
        activities.append({
            'type': 'conversion',
            'status': conv.status,
            'framework': conv.framework,
            'timestamp': conv.created_at,
            'details': f"Converted {conv.original_filename}"
        })
    
    # Get orders
    orders = Order.query.filter_by(
        account_id=account_id
    ).order_by(Order.created_at.desc()).limit(limit).all()
    
    for order in orders:
        activities.append({
            'type': 'order',
            'status': order.status,
            'amount': float(order.amount),
            'timestamp': order.created_at,
            'details': f"Purchased {order.package_type}"
        })
    
    # Get credit transactions
    transactions = CreditsTransaction.query.filter_by(
        account_id=account_id
    ).order_by(CreditsTransaction.created_at.desc()).limit(limit).all()
    
    for trans in transactions:
        activities.append({
            'type': 'credit_transaction',
            'transaction_type': trans.transaction_type,
            'amount': float(trans.amount),
            'timestamp': trans.created_at,
            'details': trans.description
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return activities[:limit]


def get_system_health():
    """Get system health metrics."""
    
    now = datetime.utcnow()
    last_hour = now - timedelta(hours=1)
    
    # Check for stuck conversions
    stuck_conversions = Conversion.query.filter(
        or_(
            Conversion.status == 'processing',
            Conversion.status == 'pending'
        ),
        Conversion.created_at < now - timedelta(minutes=10),
        Conversion.deleted_at.is_(None)
    ).count()
    
    # Recent error rate
    recent_conversions = Conversion.query.filter(
        Conversion.created_at >= last_hour,
        Conversion.deleted_at.is_(None)
    ).count()
    
    recent_errors = Conversion.query.filter(
        Conversion.status == 'failed',
        Conversion.created_at >= last_hour,
        Conversion.deleted_at.is_(None)
    ).count()
    
    if recent_conversions > 0:
        error_rate = round((recent_errors / recent_conversions) * 100, 2)
    else:
        error_rate = 0
    
    # Database connection check
    try:
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    # Check for locked accounts
    locked_accounts = Account.query.filter(
        Account.locked_until.isnot(None),
        Account.locked_until > now
    ).count()
    
    return {
        'database': db_status,
        'stuck_conversions': stuck_conversions,
        'error_rate': error_rate,
        'recent_conversions': recent_conversions,
        'recent_errors': recent_errors,
        'locked_accounts': locked_accounts,
        'timestamp': now
    }


def get_revenue_report(days=30):
    """Generate revenue report for specified days."""
    
    now = datetime.utcnow()
    start_date = now - timedelta(days=days)
    
    # Daily revenue
    daily_revenue = db.session.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.amount).label('revenue'),
        func.count(Order.id).label('orders')
    ).filter(
        Order.status == 'completed',
        Order.created_at >= start_date
    ).group_by(func.date(Order.created_at)).order_by(func.date(Order.created_at)).all()
    
    # Package breakdown
    package_revenue = db.session.query(
        Order.package_type,
        func.sum(Order.amount).label('revenue'),
        func.count(Order.id).label('orders')
    ).filter(
        Order.status == 'completed',
        Order.created_at >= start_date
    ).group_by(Order.package_type).all()
    
    return {
        'daily': [
            {
                'date': str(row.date),
                'revenue': float(row.revenue),
                'orders': row.orders
            } for row in daily_revenue
        ],
        'by_package': [
            {
                'package': row.package_type,
                'revenue': float(row.revenue),
                'orders': row.orders
            } for row in package_revenue
        ]
    }


def get_user_acquisition_report(days=30):
    """Generate user acquisition report."""
    
    now = datetime.utcnow()
    start_date = now - timedelta(days=days)
    
    # Daily signups
    daily_signups = db.session.query(
        func.date(Account.created_at).label('date'),
        func.count(Account.id).label('signups')
    ).filter(
        Account.created_at >= start_date,
        Account.deleted_at.is_(None)
    ).group_by(func.date(Account.created_at)).order_by(func.date(Account.created_at)).all()
    
    # Conversion to paid users
    total_users = Account.query.filter(
        Account.created_at >= start_date,
        Account.deleted_at.is_(None)
    ).count()
    
    paid_users = db.session.query(func.count(func.distinct(Order.account_id))).filter(
        Order.status == 'completed',
        Order.created_at >= start_date
    ).scalar()
    
    if total_users > 0:
        conversion_rate = round((paid_users / total_users) * 100, 2)
    else:
        conversion_rate = 0
    
    return {
        'daily': [
            {
                'date': str(row.date),
                'signups': row.signups
            } for row in daily_signups
        ],
        'total_users': total_users,
        'paid_users': paid_users,
        'conversion_rate': conversion_rate
    }
