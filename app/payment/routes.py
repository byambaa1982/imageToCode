# app/payment/routes.py
"""Payment routes."""

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.payment import payment
from app.models import Package


@payment.route('/pricing')
def pricing():
    """Pricing page (public)."""
    packages = Package.query.filter_by(is_active=True).order_by(Package.display_order).all()
    return render_template('payment/pricing.html', packages=packages)


@payment.route('/checkout/<package_code>')
@login_required
def checkout(package_code):
    """Checkout page."""
    package = Package.query.filter_by(code=package_code, is_active=True).first_or_404()
    return render_template('payment/checkout.html', package=package)


@payment.route('/success')
@login_required
def success():
    """Payment success page."""
    return render_template('payment/success.html')


@payment.route('/cancel')
@login_required
def cancel():
    """Payment cancelled page."""
    return render_template('payment/cancel.html')
