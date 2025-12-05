# app/main/routes.py
"""Main routes."""

from flask import render_template, current_app
from flask_login import current_user
from app.main import main
from app.models import Package


@main.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@main.route('/about')
def about():
    """About page."""
    return render_template('main/about.html')


@main.route('/pricing')
def pricing():
    """Pricing page."""
    packages = Package.query.filter_by(is_active=True).order_by(Package.display_order).all()
    return render_template('main/pricing.html', packages=packages)


@main.route('/features')
def features():
    """Features page."""
    return render_template('main/features.html')


@main.route('/how-it-works')
def how_it_works():
    """How it works page."""
    return render_template('main/how_it_works.html')
