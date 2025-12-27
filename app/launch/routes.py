# app/launch/routes.py
"""Launch management routes."""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal

from flask import (
    render_template, request, jsonify, redirect, url_for, 
    flash, current_app, session
)
from flask_login import login_required, current_user

from app.launch import launch
from app.extensions import db
from app.models import PromoCode, PromoCodeRedemption, LaunchMetric, AnalyticsEvent, Account
from app.launch.utils import track_launch_event, get_launch_dashboard_data, create_launch_promo_codes

logger = logging.getLogger(__name__)


@launch.route('/dashboard')
@login_required
def dashboard():
    """Launch dashboard for monitoring metrics."""
    # Only admins can access
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    # Get launch dashboard data
    dashboard_data = get_launch_dashboard_data()
    
    return render_template('launch/dashboard.html', data=dashboard_data)


@launch.route('/promo/<code>')
def apply_promo(code):
    """Apply promo code and redirect to signup/purchase."""
    promo_code = PromoCode.query.filter_by(code=code.upper(), is_active=True).first()
    
    if not promo_code:
        flash('Invalid promo code.', 'error')
        return redirect(url_for('main.index'))
    
    # Check validity
    account_id = current_user.id if current_user.is_authenticated else None
    is_valid, error_msg = promo_code.is_valid(account_id)
    
    if not is_valid:
        flash(error_msg, 'error')
        return redirect(url_for('main.index'))
    
    # Store promo code in session
    session['promo_code'] = code.upper()
    session['promo_campaign'] = promo_code.campaign
    
    # Track the click
    track_launch_event('promo_code_click', {
        'code': code,
        'campaign': promo_code.campaign,
        'user_id': account_id
    })
    
    # Show success message based on discount type
    if promo_code.discount_type == 'credits':
        message = f'🎉 Promo code applied! You\'ll get {promo_code.discount_value} free credits when you sign up.'
    elif promo_code.discount_type == 'percentage':
        message = f'🎉 Promo code applied! You\'ll get {promo_code.discount_value}% off your first purchase.'
    else:
        message = f'🎉 Promo code applied! You\'ll get ${promo_code.discount_value} off your first purchase.'
    
    flash(message, 'success')
    
    # Redirect based on login status
    if current_user.is_authenticated:
        if promo_code.discount_type == 'credits':
            return redirect(url_for('launch.redeem_credits'))
        else:
            return redirect(url_for('payment.pricing'))
    else:
        return redirect(url_for('auth.register'))


@launch.route('/redeem-credits')
@login_required
def redeem_credits():
    """Redeem free credits from promo code."""
    promo_code_str = session.get('promo_code')
    if not promo_code_str:
        flash('No promo code found. Please use a valid promo link.', 'error')
        return redirect(url_for('main.index'))
    
    promo_code = PromoCode.query.filter_by(code=promo_code_str, is_active=True).first()
    if not promo_code:
        flash('Invalid or expired promo code.', 'error')
        return redirect(url_for('main.index'))
    
    # Check if credits type
    if promo_code.discount_type != 'credits':
        flash('This promo code is not for free credits.', 'error')
        return redirect(url_for('payment.pricing'))
    
    # Check validity
    is_valid, error_msg = promo_code.is_valid(current_user.id)
    if not is_valid:
        flash(error_msg, 'error')
        return redirect(url_for('main.index'))
    
    # Check if already redeemed
    existing_redemption = PromoCodeRedemption.query.filter_by(
        promo_code_id=promo_code.id,
        account_id=current_user.id
    ).first()
    
    if existing_redemption:
        flash('You have already redeemed this promo code.', 'warning')
        return redirect(url_for('account.dashboard'))
    
    try:
        # Add credits to user account
        current_user.add_credits(promo_code.discount_value, f'Promo code: {promo_code.code}')
        
        # Record redemption
        redemption = PromoCodeRedemption(
            promo_code_id=promo_code.id,
            account_id=current_user.id,
            original_amount=0,
            discount_amount=promo_code.discount_value,
            final_amount=0,
            context='signup',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(redemption)
        
        # Update promo code usage
        promo_code.uses_count += 1
        
        db.session.commit()
        
        # Track the redemption
        track_launch_event('promo_code_redeemed', {
            'code': promo_code.code,
            'campaign': promo_code.campaign,
            'credits': float(promo_code.discount_value),
            'user_id': current_user.id
        })
        
        # Clear session
        session.pop('promo_code', None)
        session.pop('promo_campaign', None)
        
        flash(f'🎉 Success! {promo_code.discount_value} credits have been added to your account.', 'success')
        return redirect(url_for('converter.upload'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error redeeming promo code: {str(e)}')
        flash('An error occurred while redeeming your promo code. Please try again.', 'error')
        return redirect(url_for('main.index'))


@launch.route('/api/metrics')
@login_required
def api_metrics():
    """API endpoint for real-time launch metrics."""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get today's metrics
    today = date.today()
    metrics = LaunchMetric.query.filter_by(date=today).first()
    
    if not metrics:
        metrics = LaunchMetric(date=today)
        db.session.add(metrics)
        db.session.commit()
    
    return jsonify({
        'date': today.isoformat(),
        'unique_visitors': metrics.unique_visitors,
        'signups': metrics.signups,
        'conversions_completed': metrics.conversions_completed,
        'revenue': float(metrics.revenue),
        'promo_code_uses': metrics.promo_code_uses,
        'error_count': metrics.error_count,
        'uptime_percentage': float(metrics.uptime_percentage)
    })


@launch.route('/api/track', methods=['POST'])
def api_track():
    """API endpoint for tracking launch events."""
    data = request.get_json()
    
    if not data or 'event_type' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    try:
        track_launch_event(data['event_type'], data.get('event_data', {}))
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f'Error tracking event: {str(e)}')
        return jsonify({'error': 'Tracking failed'}), 500


@launch.route('/setup')
@login_required
def setup():
    """Set up launch promo codes and initial metrics."""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Create launch promo codes
        promo_codes = create_launch_promo_codes()
        
        # Initialize today's metrics
        today = date.today()
        if not LaunchMetric.query.filter_by(date=today).first():
            metrics = LaunchMetric(date=today)
            db.session.add(metrics)
        
        db.session.commit()
        
        flash(f'Launch setup completed! Created {len(promo_codes)} promo codes.', 'success')
        return redirect(url_for('launch.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error setting up launch: {str(e)}')
        flash('Error setting up launch. Please try again.', 'error')
        return redirect(url_for('main.index'))


@launch.route('/special/product-hunt')
def product_hunt_landing():
    """Special landing page for Product Hunt visitors."""
    # Track Product Hunt visit
    track_launch_event('product_hunt_visit', {
        'referrer': request.referrer,
        'user_agent': request.headers.get('User-Agent')
    })
    
    # Apply Product Hunt promo code automatically
    session['promo_code'] = 'PRODUCTHUNT10'
    session['promo_campaign'] = 'product_hunt'
    
    return render_template('launch/product_hunt_landing.html')


@launch.route('/special/reddit')
def reddit_landing():
    """Special landing page for Reddit visitors."""
    # Track Reddit visit
    track_launch_event('reddit_visit', {
        'referrer': request.referrer,
        'user_agent': request.headers.get('User-Agent')
    })
    
    # Apply Reddit promo code automatically
    session['promo_code'] = 'REDDIT20'
    session['promo_campaign'] = 'reddit'
    
    return render_template('launch/reddit_landing.html')
