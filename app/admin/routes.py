# app/admin/routes.py
"""Admin routes."""

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.admin import admin


def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard."""
    return render_template('admin/dashboard.html')


@admin.route('/users')
@login_required
@admin_required
def users():
    """User management."""
    return render_template('admin/users.html')


@admin.route('/conversions')
@login_required
@admin_required
def conversions():
    """Conversion management."""
    return render_template('admin/conversions.html')


@admin.route('/analytics')
@login_required
@admin_required
def analytics():
    """Analytics dashboard."""
    return render_template('admin/analytics.html')
