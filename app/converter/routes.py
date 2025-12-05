# app/converter/routes.py
"""Converter routes."""

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.converter import converter


@converter.route('/upload')
@login_required
def upload():
    """Upload page."""
    if not current_user.email_verified:
        flash('Please verify your email address before converting screenshots.', 'warning')
        return redirect(url_for('account.dashboard'))
    
    if not current_user.has_credits():
        flash('You have no credits remaining. Please purchase more credits.', 'warning')
        return redirect(url_for('payment.pricing'))
    
    return render_template('converter/upload.html')


@converter.route('/processing/<conversion_uuid>')
@login_required
def processing(conversion_uuid):
    """Processing page."""
    return render_template('converter/processing.html', conversion_uuid=conversion_uuid)


@converter.route('/result/<conversion_uuid>')
@login_required
def result(conversion_uuid):
    """Result page."""
    return render_template('converter/result.html', conversion_uuid=conversion_uuid)
