# app/payment/routes.py
"""Payment routes."""

from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.payment import payment
from app.models import Package, Order, CreditsTransaction
from app.payment.stripe_utils import (
    create_checkout_session,
    handle_checkout_completed,
    handle_payment_failed,
    verify_webhook_signature,
    get_stripe_publishable_key
)
from app.extensions import db


@payment.route('/pricing')
def pricing():
    """Pricing page (public)."""
    packages = Package.query.filter_by(is_active=True).order_by(Package.display_order).all()
    
    # Calculate per-credit cost for each package
    for package in packages:
        if package.credits > 0:
            package.per_credit_cost = float(package.price) / float(package.credits)
        else:
            package.per_credit_cost = 0
    
    return render_template('main/pricing.html', packages=packages)


@payment.route('/checkout/<package_code>')
@login_required
def checkout(package_code):
    """Checkout page - redirects to Stripe."""
    package = Package.query.filter_by(code=package_code, is_active=True).first_or_404()
    
    try:
        current_app.logger.info(f"Creating checkout session for user {current_user.id}, package {package_code}")
        
        # Create Stripe checkout session
        session = create_checkout_session(package.code, current_user.id)
        
        current_app.logger.info(f"Checkout session created: {session.id}")
        
        # Redirect to Stripe checkout
        return redirect(session.url, code=303)
        
    except ValueError as e:
        # Configuration or validation error
        current_app.logger.error(f"Validation error creating checkout session: {str(e)}")
        flash(f'Configuration error: {str(e)}', 'error')
        return redirect(url_for('payment.pricing'))
        
    except Exception as e:
        # Unexpected error
        import traceback
        current_app.logger.error(f"Error creating checkout session: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        flash('Unable to process checkout. Please try again later.', 'error')
        return redirect(url_for('payment.pricing'))


@payment.route('/success')
@login_required
def success():
    """Payment success page."""
    session_id = request.args.get('session_id')
    order_id = request.args.get('order_id')
    
    order = None
    if order_id:
        order = Order.query.get(int(order_id))
    
    return render_template('payment/success.html', session_id=session_id, order=order)


@payment.route('/cancel')
@login_required
def cancel():
    """Payment cancelled page."""
    order_id = request.args.get('order_id')
    
    # Mark order as cancelled if it exists
    if order_id:
        order = Order.query.get(int(order_id))
        if order and order.status == 'pending':
            order.status = 'failed'
            order.extra_data = {'reason': 'cancelled_by_user'}
            db.session.commit()
    
    return render_template('payment/cancel.html')


@payment.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle Stripe webhooks.
    This endpoint processes payment events from Stripe.
    """
    payload = request.get_data()
    signature = request.headers.get('Stripe-Signature')
    
    if not signature:
        current_app.logger.error("Missing Stripe signature header")
        return jsonify({'error': 'Missing signature'}), 400
    
    try:
        # Verify webhook signature
        event = verify_webhook_signature(payload, signature)
        
    except ValueError as e:
        # Invalid payload
        current_app.logger.error(f"Invalid webhook payload: {str(e)}")
        return jsonify({'error': 'Invalid payload'}), 400
        
    except Exception as e:
        # Invalid signature
        current_app.logger.error(f"Invalid webhook signature: {str(e)}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Log all webhook events
    current_app.logger.info(f"Received webhook event: {event['type']} (ID: {event.get('id', 'unknown')})")
    
    # Handle the event
    try:
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            handle_checkout_completed(session)
            current_app.logger.info(f"✅ Processed checkout.session.completed: {session.id}")
            
        elif event['type'] == 'checkout.session.async_payment_succeeded':
            session = event['data']['object']
            handle_checkout_completed(session)
            current_app.logger.info(f"✅ Processed async payment succeeded: {session.id}")
            
        elif event['type'] == 'checkout.session.async_payment_failed':
            session = event['data']['object']
            handle_payment_failed(session)
            current_app.logger.info(f"✅ Processed async payment failed: {session.id}")
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            current_app.logger.warning(f"Payment failed: {payment_intent.get('id')}")
            
        elif event['type'] == 'charge.refunded':
            charge = event['data']['object']
            current_app.logger.info(f"Charge refunded: {charge.get('id')}")
            
        else:
            current_app.logger.debug(f"Unhandled webhook event: {event['type']}")
        
        return jsonify({'status': 'success', 'event': event['type']}), 200
        
    except Exception as e:
        current_app.logger.error(f"❌ Error processing webhook {event['type']}: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        # Return 200 to prevent Stripe from retrying
        return jsonify({'status': 'error', 'message': str(e)}), 200


@payment.route('/history')
@login_required
def history():
    """View purchase history."""
    orders = Order.query.filter_by(account_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('payment/history.html', orders=orders)
