# app/account/routes.py
"""Account routes."""

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.account import account


@account.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    return render_template('account/dashboard.html')


@account.route('/history')
@login_required
def history():
    """Conversion history."""
    return render_template('account/history.html')


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
