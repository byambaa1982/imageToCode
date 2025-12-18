# app/main/routes.py
"""Main routes."""

from flask import render_template, current_app, flash, redirect, url_for
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


@main.route('/faq')
def faq():
    """FAQ page."""
    return render_template('main/faq.html')


@main.route('/terms')
def terms():
    """Terms of Service page."""
    return render_template('main/terms.html')


@main.route('/privacy')
def privacy():
    """Privacy Policy page."""
    return render_template('main/privacy.html')


@main.route('/help')
def help_center():
    """Help Center page."""
    return render_template('main/help.html')


@main.route('/help/<article>')
def help_article(article):
    """Individual help articles"""
    # Define available articles
    articles = {
        'getting-started': 'Getting Started Guide',
        'first-conversion': 'Your First Conversion',
        'credit-system': 'Understanding Credits',
        'choosing-framework': 'Choosing the Right Framework',
        'optimizing-screenshots': 'Optimizing Screenshot Quality',
        'responsive-designs': 'Working with Responsive Designs',
        'conversion-history': 'Managing Your History',
        'purchasing-credits': 'Purchasing Credit Packages',
        'payment-security': 'Payment Security',
        'refunds': 'Refunds and Billing',
        'upload-problems': 'Upload Troubleshooting',
        'conversion-errors': 'Conversion Error Fixes',
        'browser-compatibility': 'Browser Compatibility',
        'performance': 'Performance Optimization',
        'profile-update': 'Updating Your Profile',
        'password-security': 'Password and Security',
        'notifications': 'Email Preferences',
        'account-deletion': 'Deleting Your Account'
    }
    
    if article not in articles:
        flash('Help article not found.', 'error')
        return redirect(url_for('main.help'))
    
    return render_template('main/help_article.html', 
                         article=article, 
                         title=articles[article])
