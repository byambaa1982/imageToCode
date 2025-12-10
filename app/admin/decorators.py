# app/admin/decorators.py
"""Admin decorators for access control."""

from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user


def admin_required(f):
    """
    Decorator to require admin access.
    
    Usage:
        @admin.route('/dashboard')
        @login_required
        @admin_required
        def dashboard():
            return render_template('admin/dashboard.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function
