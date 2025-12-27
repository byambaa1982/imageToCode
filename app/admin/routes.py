# app/admin/routes.py
"""Admin routes."""

from decimal import Decimal
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from sqlalchemy import or_, and_, desc, func
from app.admin import admin
from app.admin.decorators import admin_required
from app.admin.utils import (
    get_dashboard_stats,
    get_user_activity_log,
    get_system_health,
    get_revenue_report,
    get_user_acquisition_report
)
from app.extensions import db
from app.models import Account, Conversion, Order, CreditsTransaction, Package
import threading


@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with key metrics."""
    stats = get_dashboard_stats()
    health = get_system_health()
    
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        health=health
    )


@admin.route('/users')
@login_required
@admin_required
def users():
    """User management."""
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Search
    search = request.args.get('search', '').strip()
    
    # Filters
    verified_filter = request.args.get('verified', '')
    admin_filter = request.args.get('admin', '')
    
    # Build query
    query = Account.query.filter_by(deleted_at=None)
    
    if search:
        query = query.filter(
            or_(
                Account.email.ilike(f'%{search}%'),
                Account.username.ilike(f'%{search}%')
            )
        )
    
    if verified_filter == 'yes':
        query = query.filter_by(email_verified=True)
    elif verified_filter == 'no':
        query = query.filter_by(email_verified=False)
    
    if admin_filter == 'yes':
        query = query.filter_by(is_admin=True)
    elif admin_filter == 'no':
        query = query.filter_by(is_admin=False)
    
    # Order by newest first
    query = query.order_by(desc(Account.created_at))
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users_list = pagination.items
    
    return render_template(
        'admin/users.html',
        users=users_list,
        pagination=pagination,
        search=search,
        verified_filter=verified_filter,
        admin_filter=admin_filter
    )


@admin.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """User detail view."""
    user = Account.query.get_or_404(user_id)
    
    # Get user statistics
    total_conversions = Conversion.query.filter_by(
        account_id=user_id,
        deleted_at=None
    ).count()
    
    completed_conversions = Conversion.query.filter_by(
        account_id=user_id,
        status='completed',
        deleted_at=None
    ).count()
    
    total_spent = db.session.query(
        func.coalesce(func.sum(Order.amount), 0)
    ).filter_by(
        account_id=user_id,
        status='completed'
    ).scalar() or Decimal('0')
    
    # Get activity log
    activities = get_user_activity_log(user_id, limit=50)
    
    return render_template(
        'admin/user_detail.html',
        user=user,
        total_conversions=total_conversions,
        completed_conversions=completed_conversions,
        total_spent=float(total_spent),
        activities=activities
    )


@admin.route('/users/<int:user_id>/adjust-credits', methods=['POST'])
@login_required
@admin_required
def adjust_credits(user_id):
    """Adjust user credits (admin only)."""
    user = Account.query.get_or_404(user_id)
    
    amount = request.form.get('amount', type=float)
    reason = request.form.get('reason', '').strip()
    
    if not amount:
        flash('Please provide a valid amount.', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    if not reason:
        flash('Please provide a reason for the adjustment.', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    try:
        amount_decimal = Decimal(str(amount))
        user.credits_remaining += amount_decimal
        
        # Create transaction record
        transaction = CreditsTransaction(
            account_id=user_id,
            amount=amount_decimal,
            balance_after=user.credits_remaining,
            transaction_type='adjustment',
            description=f'Admin adjustment: {reason}'
        )
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Successfully adjusted credits by {amount}. New balance: {user.credits_remaining}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adjusting credits: {str(e)}', 'danger')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user."""
    user = Account.query.get_or_404(user_id)
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin access {status} for {user.email}', 'success')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_active(user_id):
    """Toggle active status for a user."""
    user = Account.query.get_or_404(user_id)
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'Account {status} for {user.email}', 'success')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin.route('/users/<int:user_id>/verify-email', methods=['POST'])
@login_required
@admin_required
def verify_email(user_id):
    """Manually verify user email."""
    user = Account.query.get_or_404(user_id)
    
    user.email_verified = True
    db.session.commit()
    
    flash(f'Email verified for {user.email}', 'success')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin.route('/conversions')
@login_required
@admin_required
def conversions():
    """Conversion management."""
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filters
    status_filter = request.args.get('status', '')
    framework_filter = request.args.get('framework', '')
    user_search = request.args.get('user', '').strip()
    
    # Build query
    query = Conversion.query.filter_by(deleted_at=None)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if framework_filter:
        query = query.filter_by(framework=framework_filter)
    
    if user_search:
        # Join with Account to search by email
        query = query.join(Account).filter(
            or_(
                Account.email.ilike(f'%{user_search}%'),
                Account.username.ilike(f'%{user_search}%')
            )
        )
    
    # Order by newest first
    query = query.order_by(desc(Conversion.created_at))
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    conversions_list = pagination.items
    
    # Get available frameworks for filter
    frameworks = db.session.query(
        Conversion.framework
    ).distinct().filter(
        Conversion.framework.isnot(None)
    ).all()
    frameworks = [f[0] for f in frameworks]
    
    return render_template(
        'admin/conversions.html',
        conversions=conversions_list,
        pagination=pagination,
        status_filter=status_filter,
        framework_filter=framework_filter,
        user_search=user_search,
        frameworks=frameworks
    )


@admin.route('/conversions/<int:conversion_id>')
@login_required
@admin_required
def conversion_detail(conversion_id):
    """Conversion detail view with debug information."""
    conversion = Conversion.query.get_or_404(conversion_id)
    
    return render_template(
        'admin/conversion_detail.html',
        conversion=conversion
    )


@admin.route('/conversions/<int:conversion_id>/retry', methods=['POST'])
@login_required
@admin_required
def retry_conversion(conversion_id):
    """Manually retry a failed conversion."""
    conversion = Conversion.query.get_or_404(conversion_id)
    
    if conversion.status not in ['failed', 'pending']:
        flash('Only failed or pending conversions can be retried.', 'warning')
        return redirect(url_for('admin.conversion_detail', conversion_id=conversion_id))
    
    try:
        # Reset status
        conversion.status = 'pending'
        conversion.error_message = None
        conversion.retry_count += 1
        db.session.commit()
        
        # Queue for processing using threading (same as converter routes)
        from app.tasks.conversion_tasks import process_screenshot_conversion
        thread = threading.Thread(target=process_screenshot_conversion, args=[conversion.uuid])
        thread.daemon = True
        thread.start()
        
        flash('Conversion queued for retry.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error retrying conversion: {str(e)}', 'danger')
    
    return redirect(url_for('admin.conversion_detail', conversion_id=conversion_id))


@admin.route('/conversions/<int:conversion_id>/refund', methods=['POST'])
@login_required
@admin_required
def refund_conversion(conversion_id):
    """Refund credits for a conversion."""
    conversion = Conversion.query.get_or_404(conversion_id)
    
    # Check if already refunded
    existing_refund = CreditsTransaction.query.filter_by(
        account_id=conversion.account_id,
        transaction_type='refund',
        description=f'Refund for conversion {conversion.uuid}'
    ).first()
    
    if existing_refund:
        flash('This conversion has already been refunded.', 'warning')
        return redirect(url_for('admin.conversion_detail', conversion_id=conversion_id))
    
    try:
        # Add 1 credit back
        conversion.account.add_credits(
            1.0,
            description=f'Refund for conversion {conversion.uuid}',
            order_id=None
        )
        
        # Update transaction type to refund
        transaction = CreditsTransaction.query.filter_by(
            account_id=conversion.account_id
        ).order_by(desc(CreditsTransaction.created_at)).first()
        
        if transaction:
            transaction.transaction_type = 'refund'
            db.session.commit()
        
        flash(f'1 credit refunded to {conversion.account.email}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error refunding credits: {str(e)}', 'danger')
    
    return redirect(url_for('admin.conversion_detail', conversion_id=conversion_id))


@admin.route('/analytics')
@login_required
@admin_required
def analytics():
    """Analytics dashboard."""
    # Get reports
    days = request.args.get('days', 30, type=int)
    
    revenue_report = get_revenue_report(days=days)
    user_report = get_user_acquisition_report(days=days)
    
    return render_template(
        'admin/analytics.html',
        revenue_report=revenue_report,
        user_report=user_report,
        days=days
    )


@admin.route('/health')
@login_required
@admin_required
def health():
    """System health monitoring."""
    health_data = get_system_health()
    
    # Get recent errors
    recent_errors = Conversion.query.filter_by(
        status='failed',
        deleted_at=None
    ).order_by(desc(Conversion.created_at)).limit(20).all()
    
    # Get stuck conversions
    stuck = Conversion.query.filter(
        or_(
            Conversion.status == 'processing',
            Conversion.status == 'pending'
        ),
        Conversion.created_at < datetime.utcnow() - timedelta(minutes=10),
        Conversion.deleted_at.is_(None)
    ).all()
    
    return render_template(
        'admin/health.html',
        health=health_data,
        recent_errors=recent_errors,
        stuck_conversions=stuck
    )


@admin.route('/packages')
@login_required
@admin_required
def packages():
    """Package management."""
    packages_list = Package.query.order_by(Package.display_order).all()
    
    return render_template(
        'admin/packages.html',
        packages=packages_list
    )


@admin.route('/packages/<int:package_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_package(package_id):
    """Edit package details."""
    package = Package.query.get_or_404(package_id)
    
    if request.method == 'POST':
        try:
            package.name = request.form.get('name', package.name)
            package.description = request.form.get('description', package.description)
            package.price = Decimal(request.form.get('price', package.price))
            package.credits = Decimal(request.form.get('credits', package.credits))
            package.is_active = request.form.get('is_active') == 'on'
            package.is_featured = request.form.get('is_featured') == 'on'
            package.badge = request.form.get('badge', '').strip() or None
            package.display_order = int(request.form.get('display_order', package.display_order))
            
            db.session.commit()
            flash('Package updated successfully.', 'success')
            return redirect(url_for('admin.packages'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating package: {str(e)}', 'danger')
    
    return render_template(
        'admin/edit_package.html',
        package=package
    )


@admin.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API endpoint for dashboard stats (for AJAX updates)."""
    stats = get_dashboard_stats()
    return jsonify(stats)


@admin.route('/api/health')
@login_required
@admin_required
def api_health():
    """API endpoint for system health (for AJAX updates)."""
    health = get_system_health()
    # Convert datetime to string for JSON serialization
    health['timestamp'] = health['timestamp'].isoformat()
    return jsonify(health)



