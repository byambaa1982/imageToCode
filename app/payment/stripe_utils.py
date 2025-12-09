# app/payment/stripe_utils.py
"""Stripe payment utilities."""
# Last updated: 2025-12-09 06:56 - Import all available Stripe submodules

import stripe
# Import all Stripe sub-modules to prevent lazy loading issues
import stripe.apps
import stripe.billing_portal
import stripe.checkout
import stripe.climate
import stripe.data
import stripe.financial_connections
import stripe.identity
import stripe.issuing
import stripe.radar
import stripe.reporting
import stripe.sigma
import stripe.tax
import stripe.terminal
import stripe.test_helpers
import stripe.treasury

from flask import current_app, url_for
from app.models import Order, Package, Account
from app.extensions import db


def init_stripe():
    """Initialize Stripe with API key."""
    api_key = current_app.config.get('STRIPE_SECRET_KEY')
    if not api_key:
        raise ValueError("STRIPE_SECRET_KEY is not configured")
    
    stripe.api_key = api_key
    current_app.logger.debug(f"Stripe initialized with key: {stripe.api_key[:7]}...")


def create_checkout_session(package_code, account_id):
    """
    Create a Stripe checkout session for package purchase.
    
    Args:
        package_code: Code of the package to purchase
        account_id: ID of the account making the purchase
    
    Returns:
        Stripe checkout session object
    """
    # Initialize Stripe API key
    init_stripe()
    
    # Get package details
    package = Package.query.filter_by(code=package_code, is_active=True).first()
    if not package:
        raise ValueError(f"Package {package_code} not found or inactive")
    
    # Get account
    account = Account.query.get(account_id)
    if not account:
        raise ValueError(f"Account {account_id} not found")
    
    # Create pending order
    order = Order(
        account_id=account_id,
        amount=float(package.price),
        currency='USD',
        package_type=package.code,
        credits_purchased=float(package.credits),
        status='pending'
    )
    db.session.add(order)
    db.session.commit()
    
    try:
        # Create Stripe checkout session with idempotency key
        idempotency_key = f"order_{order.id}_{order.created_at.timestamp()}"
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': package.name,
                        'description': package.description,
                    },
                    'unit_amount': int(float(package.price) * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payment.success', _external=True) + f'?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}',
            cancel_url=url_for('payment.cancel', _external=True) + f'?order_id={order.id}',
            client_reference_id=str(order.id),
            customer_email=account.email,
            metadata={
                'order_id': str(order.id),
                'account_id': str(account_id),
                'package_code': package_code,
                'credits': str(package.credits)
            },
            idempotency_key=idempotency_key
        )
        
        # Update order with session ID
        order.stripe_session_id = session.id
        db.session.commit()
        
        return session
        
    except stripe.error.CardError as e:
        # Card declined or invalid
        order.status = 'failed'
        order.extra_data = {'error': str(e), 'type': 'card_error'}
        db.session.commit()
        current_app.logger.error(f"Card error for order {order.id}: {str(e)}")
        raise
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters
        order.status = 'failed'
        order.extra_data = {'error': str(e), 'type': 'invalid_request'}
        db.session.commit()
        current_app.logger.error(f"Invalid request for order {order.id}: {str(e)}")
        raise
    except stripe.error.AuthenticationError as e:
        # Authentication failed
        order.status = 'failed'
        order.extra_data = {'error': str(e), 'type': 'auth_error'}
        db.session.commit()
        current_app.logger.error(f"Stripe authentication error: {str(e)}")
        raise
    except Exception as e:
        # Other errors
        order.status = 'failed'
        order.extra_data = {'error': str(e), 'type': 'unknown'}
        db.session.commit()
        current_app.logger.error(f"Unexpected error creating session for order {order.id}: {str(e)}")
        raise


def handle_checkout_completed(session):
    """
    Handle completed checkout session.
    
    Args:
        session: Stripe checkout session object
    """
    init_stripe()
    
    # Get order ID from metadata
    order_id = session.metadata.get('order_id')
    if not order_id:
        current_app.logger.error(f"No order_id in session metadata: {session.id}")
        return
    
    order = Order.query.get(int(order_id))
    if not order:
        current_app.logger.error(f"Order {order_id} not found")
        return
    
    # Check if already processed
    if order.status == 'completed':
        current_app.logger.info(f"Order {order_id} already completed")
        return
    
    try:
        # Update order status
        order.status = 'completed'
        order.stripe_payment_id = session.payment_intent
        order.payment_method_type = 'card'
        order.extra_data = {
            'session_id': session.id,
            'payment_status': session.payment_status,
            'amount_total': session.amount_total,
            'currency': session.currency
        }
        
        # Add credits to account
        account = Account.query.get(order.account_id)
        if account:
            account.add_credits(
                amount=float(order.credits_purchased),
                description=f"Purchase: {order.package_type}",
                order_id=order.id
            )
            current_app.logger.info(
                f"Added {order.credits_purchased} credits to account {account.email} "
                f"(Order: {order.id}, New balance: {account.credits_remaining})"
            )
        
        db.session.commit()
        
    except Exception as e:
        current_app.logger.error(f"Error processing order {order_id}: {str(e)}")
        db.session.rollback()
        raise


def handle_payment_failed(session):
    """
    Handle failed payment.
    
    Args:
        session: Stripe checkout session object
    """
    order_id = session.metadata.get('order_id')
    if not order_id:
        return
    
    order = Order.query.get(int(order_id))
    if not order:
        return
    
    order.status = 'failed'
    order.extra_data = {
        'session_id': session.id,
        'payment_status': session.payment_status,
        'error': 'Payment failed'
    }
    db.session.commit()


def process_refund(order_id, reason='requested_by_customer'):
    """
    Process a refund for an order.
    
    Args:
        order_id: ID of the order to refund
        reason: Reason for refund
    
    Returns:
        Stripe refund object
    """
    init_stripe()
    
    order = Order.query.get(order_id)
    if not order:
        raise ValueError(f"Order {order_id} not found")
    
    if order.status != 'completed':
        raise ValueError(f"Order {order_id} is not completed (status: {order.status})")
    
    if not order.stripe_payment_id:
        raise ValueError(f"Order {order_id} has no payment ID")
    
    try:
        # Create refund in Stripe
        refund = stripe.Refund.create(
            payment_intent=order.stripe_payment_id,
            reason=reason,
            metadata={
                'order_id': str(order_id)
            }
        )
        
        # Update order status
        order.status = 'refunded'
        order.extra_data = order.extra_data or {}
        order.extra_data['refund_id'] = refund.id
        order.extra_data['refund_reason'] = reason
        order.extra_data['refund_created'] = refund.created
        
        # Deduct credits from account (refund removes credits)
        account = Account.query.get(order.account_id)
        if account:
            # Deduct the credits that were added during purchase
            current_credits = float(account.credits_remaining)
            refund_amount = float(order.credits_purchased)
            
            # Only deduct if account has enough credits
            if current_credits >= refund_amount:
                account.credits_remaining = current_credits - refund_amount
                
                # Create negative transaction record
                from app.models import CreditsTransaction
                transaction = CreditsTransaction(
                    account_id=account.id,
                    amount=-refund_amount,
                    description=f"Refund: {order.package_type}",
                    order_id=order.id
                )
                db.session.add(transaction)
                
                current_app.logger.info(
                    f"Refunded {refund_amount} credits from account {account.email} "
                    f"(Order: {order.id}, New balance: {account.credits_remaining})"
                )
            else:
                current_app.logger.warning(
                    f"Account {account.email} has insufficient credits for refund. "
                    f"Current: {current_credits}, Refund: {refund_amount}"
                )
        
        db.session.commit()
        
        current_app.logger.info(
            f"Refunded order {order_id} (Refund ID: {refund.id})"
        )
        
        return refund
        
    except Exception as e:
        current_app.logger.error(f"Error refunding order {order_id}: {str(e)}")
        raise


def get_stripe_publishable_key():
    """Get Stripe publishable key."""
    return current_app.config.get('STRIPE_PUBLIC_KEY')


def verify_webhook_signature(payload, signature):
    """
    Verify Stripe webhook signature.
    
    Args:
        payload: Raw request payload
        signature: Stripe signature header
    
    Returns:
        Verified event object
    """
    init_stripe()
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
        return event
    except ValueError as e:
        # Invalid payload
        current_app.logger.error(f"Invalid webhook payload: {str(e)}")
        raise
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        current_app.logger.error(f"Invalid webhook signature: {str(e)}")
        raise


def get_customer_portal_url(account_id):
    """
    Create a Stripe customer portal session.
    
    Args:
        account_id: ID of the account
    
    Returns:
        URL to customer portal
    """
    init_stripe()
    
    # Get account
    account = Account.query.get(account_id)
    if not account:
        raise ValueError(f"Account {account_id} not found")
    
    # For now, redirect to billing page
    # In future, we could create a proper Stripe customer portal
    return url_for('account.billing', _external=True)
