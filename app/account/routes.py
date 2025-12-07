# app/account/routes.py
"""Account routes."""

from flask import render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.account import account
from app.models import Conversion
<<<<<<< HEAD
=======
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
>>>>>>> 2bf1b7da8016d815cd152db5a4ae2d975ae344b4


@account.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
<<<<<<< HEAD
    # Get recent conversions
    recent_conversions = Conversion.query.filter_by(account_id=current_user.id)\
        .order_by(Conversion.created_at.desc())\
        .limit(5)\
        .all()
=======
    try:
        # Get recent conversions for the dashboard
        recent_conversions = current_user.conversions.order_by(Conversion.created_at.desc()).limit(5).all()
    except Exception as e:
        # If there's any error getting conversions, use empty list
        recent_conversions = []
        current_app.logger.error(f"Error fetching recent conversions for user {current_user.id}: {e}")
>>>>>>> 2bf1b7da8016d815cd152db5a4ae2d975ae344b4
    
    return render_template('account/dashboard.html', recent_conversions=recent_conversions)


@account.route('/history')
@login_required
def history():
    """Conversion history."""
    # Get all conversions for the user, ordered by most recent
    conversions = current_user.conversions.order_by(Conversion.created_at.desc()).all()
    
    return render_template('account/history.html', conversions=conversions)


@account.route('/settings')
@login_required
def settings():
    """Account settings."""
    return render_template('account/settings.html')


@account.route('/billing')
@login_required
def billing():
    """Billing and transaction history."""
    return render_template('account/billing.html')
