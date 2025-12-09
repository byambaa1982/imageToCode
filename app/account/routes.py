# app/account/routes.py
"""Account routes."""

from flask import render_template, redirect, url_for, flash, current_app, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from app.account import account
from app.models import Account, Conversion, CreditsTransaction, ConversionFeedback
from app.extensions import db


@account.route('/dev/verify-email')
@login_required
def dev_verify_email():
    """Development route to quickly verify email."""
    if current_app.config.get('ENV') == 'production':
        flash('This feature is not available in production.', 'error')
        return redirect(url_for('account.dashboard'))
    
    if current_user.email_verified:
        flash('Your email is already verified!', 'info')
    else:
        current_user.email_verified = True
        db.session.commit()
        flash('✅ Email verified successfully for development!', 'success')
    
    return redirect(url_for('account.dashboard'))


@account.route('/dashboard')
@login_required
def dashboard():
    """Enhanced user dashboard with analytics."""
    try:
        # Get recent conversions for the dashboard
        recent_conversions = current_user.conversions.order_by(Conversion.created_at.desc()).limit(5).all()
        
        # Calculate analytics
        total_conversions = current_user.conversions.count()
        successful_conversions = current_user.conversions.filter_by(status='completed').count()
        success_rate = (successful_conversions / total_conversions * 100) if total_conversions > 0 else 0
        
        # Get conversions this month
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        conversions_this_month = current_user.conversions.filter(
            Conversion.created_at >= start_of_month
        ).count()
        
        # Framework usage statistics
        framework_stats_raw = db.session.query(
            Conversion.framework, 
            func.count(Conversion.id).label('count')
        ).filter(
            Conversion.account_id == current_user.id
        ).group_by(Conversion.framework).all()
        
        # Convert to serializable format
        framework_stats = [[row.framework, row.count] for row in framework_stats_raw]
        
        # Recent credit transactions
        recent_transactions = current_user.credit_transactions.order_by(
            CreditsTransaction.created_at.desc()
        ).limit(3).all()
        
        # Total credits purchased
        total_credits_purchased = db.session.query(
            func.sum(CreditsTransaction.amount)
        ).filter(
            and_(
                CreditsTransaction.account_id == current_user.id,
                CreditsTransaction.transaction_type == 'purchase'
            )
        ).scalar() or 0
        
        analytics = {
            'total_conversions': total_conversions,
            'successful_conversions': successful_conversions,
            'success_rate': round(success_rate, 1),
            'conversions_this_month': conversions_this_month,
            'framework_stats': framework_stats,
            'total_credits_purchased': float(total_credits_purchased)
        }
        
    except Exception as e:
        # If there's any error getting conversions, use defaults
        recent_conversions = []
        recent_transactions = []
        analytics = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'success_rate': 0,
            'conversions_this_month': 0,
            'framework_stats': [],
            'total_credits_purchased': 0
        }
        current_app.logger.error(f"Error fetching dashboard data for user {current_user.id}: {e}")
    
    return render_template('account/dashboard.html', 
                         recent_conversions=recent_conversions,
                         recent_transactions=recent_transactions,
                         analytics=analytics)


@account.route('/history')
@login_required
def history():
    """Enhanced conversion history with filtering and search."""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    framework_filter = request.args.get('framework', 'all')
    search_query = request.args.get('search', '').strip()
    
    # Start with base query
    query = current_user.conversions
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        query = query.filter(Conversion.status == status_filter)
    
    # Apply framework filter
    if framework_filter and framework_filter != 'all':
        query = query.filter(Conversion.framework == framework_filter)
    
    # Apply search filter
    if search_query:
        query = query.filter(Conversion.original_filename.contains(search_query))
    
    # Order by most recent and get results
    conversions = query.order_by(Conversion.created_at.desc()).all()
    
    # Get unique frameworks for filter dropdown
    frameworks = db.session.query(Conversion.framework).filter(
        Conversion.account_id == current_user.id
    ).distinct().all()
    frameworks = [f[0] for f in frameworks]
    
    return render_template('account/history.html', 
                         conversions=conversions,
                         frameworks=frameworks,
                         current_filters={
                             'status': status_filter,
                             'framework': framework_filter,
                             'search': search_query
                         })


@account.route('/settings')
@login_required
def settings():
    """Account settings."""
    return render_template('account/settings.html')


@account.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    """Update profile information."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        
        if not username:
            flash('Username is required.', 'error')
            return redirect(url_for('account.settings'))
        
        # Check if username is taken (excluding current user)
        existing_user = db.session.query(Account).filter(
            and_(Account.username == username, Account.id != current_user.id)
        ).first()
        
        if existing_user:
            flash('Username is already taken.', 'error')
            return redirect(url_for('account.settings'))
        
        # Update username
        current_user.username = username
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
    return redirect(url_for('account.settings'))


@account.route('/settings/password', methods=['POST'])
@login_required
def change_password():
    """Change user password."""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validate inputs
    if not all([current_password, new_password, confirm_password]):
        flash('All password fields are required.', 'error')
        return redirect(url_for('account.settings'))
    
    # Check current password (only for non-OAuth users)
    if current_user.password_hash and not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('account.settings'))
    
    # Check password confirmation
    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('account.settings'))
    
    # Validate password strength
    if len(new_password) < 8:
        flash('Password must be at least 8 characters long.', 'error')
        return redirect(url_for('account.settings'))
    
    # Update password
    current_user.set_password(new_password)
    db.session.commit()
    flash('Password changed successfully!', 'success')
    
    return redirect(url_for('account.settings'))


@account.route('/conversion/<conversion_uuid>/delete', methods=['POST'])
@login_required
def delete_conversion(conversion_uuid):
    """Delete a conversion."""
    conversion = Conversion.query.filter_by(
        uuid=conversion_uuid,
        account_id=current_user.id
    ).first_or_404()
    
    try:
        db.session.delete(conversion)
        db.session.commit()
        flash('Conversion deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting conversion {conversion_uuid}: {e}")
        flash('Error deleting conversion. Please try again.', 'error')
    
    return redirect(url_for('account.history'))


@account.route('/conversion/<conversion_uuid>/retry', methods=['POST'])
@login_required
def retry_conversion(conversion_uuid):
    """Retry a failed conversion."""
    conversion = Conversion.query.filter_by(
        uuid=conversion_uuid,
        account_id=current_user.id,
        status='failed'
    ).first_or_404()
    
    try:
        # Reset conversion status
        conversion.status = 'pending'
        conversion.error_message = None
        conversion.retry_count += 1
        db.session.commit()
        
        # Queue for processing
        from app.tasks.conversion_tasks import process_conversion
        process_conversion.delay(conversion.uuid)
        
        flash('Conversion queued for retry.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error retrying conversion {conversion_uuid}: {e}")
        flash('Error retrying conversion.', 'error')
    
    return redirect(url_for('account.history'))


@account.route('/conversion/<conversion_uuid>/feedback', methods=['POST'])
@login_required
def add_feedback(conversion_uuid):
    """Add feedback for a conversion."""
    conversion = Conversion.query.filter_by(
        uuid=conversion_uuid,
        account_id=current_user.id
    ).first_or_404()
    
    rating = request.form.get('rating', type=int)
    feedback_text = request.form.get('feedback', '').strip()
    
    if not rating or rating < 1 or rating > 5:
        flash('Please provide a valid rating (1-5 stars).', 'error')
        return redirect(request.referrer or url_for('account.history'))
    
    # Check if feedback already exists
    existing_feedback = ConversionFeedback.query.filter_by(
        conversion_id=conversion.id,
        account_id=current_user.id
    ).first()
    
    try:
        if existing_feedback:
            # Update existing feedback
            existing_feedback.rating = rating
            existing_feedback.feedback_text = feedback_text
        else:
            # Create new feedback
            feedback = ConversionFeedback(
                conversion_id=conversion.id,
                account_id=current_user.id,
                rating=rating,
                feedback_text=feedback_text
            )
            db.session.add(feedback)
        
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving feedback for conversion {conversion_uuid}: {e}")
        flash('Error saving feedback. Please try again.', 'error')
    
    return redirect(request.referrer or url_for('account.history'))


@account.route('/analytics/data')
@login_required
def analytics_data():
    """Get analytics data for charts (AJAX endpoint)."""
    # Get conversions over the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Daily conversion counts
    daily_conversions = db.session.query(
        func.date(Conversion.created_at).label('date'),
        func.count(Conversion.id).label('count')
    ).filter(
        and_(
            Conversion.account_id == current_user.id,
            Conversion.created_at >= start_date
        )
    ).group_by(func.date(Conversion.created_at)).all()
    
    # Framework distribution
    framework_distribution = db.session.query(
        Conversion.framework,
        func.count(Conversion.id).label('count')
    ).filter(
        Conversion.account_id == current_user.id
    ).group_by(Conversion.framework).all()
    
    # Status distribution
    status_distribution = db.session.query(
        Conversion.status,
        func.count(Conversion.id).label('count')
    ).filter(
        Conversion.account_id == current_user.id
    ).group_by(Conversion.status).all()
    
    return jsonify({
        'daily_conversions': [
            {'date': str(item.date), 'count': item.count} 
            for item in daily_conversions
        ],
        'framework_distribution': [
            {'framework': item.framework, 'count': item.count} 
            for item in framework_distribution
        ],
        'status_distribution': [
            {'status': item.status, 'count': item.count} 
            for item in status_distribution
        ]
    })


@account.route('/billing')
@login_required
def billing():
    """Billing and transaction history."""
    from app.models import CreditsTransaction
    
    # Get all transactions for the user, ordered by most recent
    transactions = CreditsTransaction.query.filter_by(
        account_id=current_user.id
    ).order_by(CreditsTransaction.created_at.desc()).all()
    
    return render_template('account/billing.html', transactions=transactions)
