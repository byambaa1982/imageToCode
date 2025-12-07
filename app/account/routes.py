# app/account/routes.py
"""Account routes."""

from flask import render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.account import account
from app.models import Conversion


@account.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    try:
        # Get recent conversions for the dashboard
        recent_conversions = current_user.conversions.order_by(Conversion.created_at.desc()).limit(5).all()
    except Exception as e:
        # If there's any error getting conversions, use empty list
        recent_conversions = []
        current_app.logger.error(f"Error fetching recent conversions for user {current_user.id}: {e}")
    
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
