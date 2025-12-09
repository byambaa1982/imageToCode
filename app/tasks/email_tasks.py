# app/tasks/email_tasks.py
"""Email background tasks and notifications."""

import logging
from datetime import datetime, timedelta
from flask import current_app, render_template_string
from flask_mail import Message
from app.extensions import db, mail, celery
from app.models import Account, Conversion, PasswordResetToken, EmailVerificationToken, CreditsTransaction

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3)
def send_email_task(self, to_email, subject, template_name, **template_vars):
    """Send email asynchronously."""
    try:
        # Create message
        msg = Message(
            subject=subject,
            recipients=[to_email],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        
        # Get template content
        template_content = get_email_template(template_name)
        if template_content:
            msg.html = render_template_string(template_content, **template_vars)
            msg.body = f"Subject: {subject}\n\nThis is an HTML email. Please view it in a client that supports HTML."
        else:
            msg.body = f"Subject: {subject}\n\nEmail notification from Screenshot to Code"
        
        # Send email
        mail.send(msg)
        logger.info(f"Email sent successfully to {to_email}")
        
    except Exception as exc:
        logger.error(f"Email sending failed: {exc}")
        if self.request.retries < self.max_retries:
            # Retry in 5 minutes
            raise self.retry(countdown=300, exc=exc)
        raise exc


@celery.task
def send_conversion_complete_email(account_id, conversion_id):
    """Send email when conversion is completed."""
    try:
        account = Account.query.get(account_id)
        conversion = Conversion.query.get(conversion_id)
        
        if not account or not conversion:
            logger.error(f"Account or conversion not found: {account_id}, {conversion_id}")
            return
        
        if not account.email_verified:
            logger.info(f"Skipping email to unverified account: {account.email}")
            return
        
        # Send email
        send_email_task.delay(
            to_email=account.email,
            subject="Your conversion is ready! 🎉",
            template_name='conversion_complete',
            account=account,
            conversion=conversion,
            result_url=current_app.config.get('BASE_URL', '') + f"/converter/result/{conversion.uuid}"
        )
        
    except Exception as e:
        logger.error(f"Error sending conversion complete email: {e}")


@celery.task
def send_low_credit_warning(account_id):
    """Send email when user has low credits."""
    try:
        account = Account.query.get(account_id)
        
        if not account or not account.email_verified:
            return
        
        # Only send if credits are exactly 1 (to avoid spam)
        if float(account.credits_remaining) != 1.0:
            return
        
        send_email_task.delay(
            to_email=account.email,
            subject="Running low on credits ⚡",
            template_name='low_credit_warning',
            account=account,
            pricing_url=current_app.config.get('BASE_URL', '') + "/payment/pricing"
        )
        
    except Exception as e:
        logger.error(f"Error sending low credit warning: {e}")


@celery.task
def send_welcome_email(account_id):
    """Send welcome email to new users."""
    try:
        account = Account.query.get(account_id)
        
        if not account:
            return
        
        send_email_task.delay(
            to_email=account.email,
            subject="Welcome to Screenshot to Code! 🚀",
            template_name='welcome',
            account=account,
            dashboard_url=current_app.config.get('BASE_URL', '') + "/account/dashboard",
            upload_url=current_app.config.get('BASE_URL', '') + "/converter/upload"
        )
        
    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")


@celery.task
def send_weekly_summary():
    """Send weekly usage summary to active users."""
    try:
        # Get the date range for last week
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Find accounts that had activity in the last week
        active_accounts = db.session.query(Account).join(Conversion).filter(
            Conversion.created_at >= start_date,
            Account.email_verified == True
        ).distinct().all()
        
        for account in active_accounts:
            # Calculate weekly stats
            weekly_conversions = account.conversions.filter(
                Conversion.created_at >= start_date
            ).count()
            
            weekly_successful = account.conversions.filter(
                Conversion.created_at >= start_date,
                Conversion.status == 'completed'
            ).count()
            
            success_rate = (weekly_successful / weekly_conversions * 100) if weekly_conversions > 0 else 0
            
            send_email_task.delay(
                to_email=account.email,
                subject="Your weekly conversion summary 📊",
                template_name='weekly_summary',
                account=account,
                weekly_conversions=weekly_conversions,
                weekly_successful=weekly_successful,
                success_rate=round(success_rate, 1),
                dashboard_url=current_app.config.get('BASE_URL', '') + "/account/dashboard"
            )
            
    except Exception as e:
        logger.error(f"Error sending weekly summaries: {e}")


@celery.task
def send_purchase_receipt(account_id, order_id):
    """Send receipt email after successful purchase."""
    try:
        from app.models import Order
        
        account = Account.query.get(account_id)
        order = Order.query.get(order_id)
        
        if not account or not order or not account.email_verified:
            return
        
        send_email_task.delay(
            to_email=account.email,
            subject=f"Purchase receipt - ${order.amount}",
            template_name='purchase_receipt',
            account=account,
            order=order,
            billing_url=current_app.config.get('BASE_URL', '') + "/account/billing"
        )
        
    except Exception as e:
        logger.error(f"Error sending purchase receipt: {e}")


@celery.task
def cleanup_expired_tokens():
    """Clean up expired tokens."""
    try:
        now = datetime.utcnow()
        
        # Clean up expired password reset tokens
        expired_password_tokens = PasswordResetToken.query.filter(
            PasswordResetToken.expires_at < now
        ).all()
        
        for token in expired_password_tokens:
            db.session.delete(token)
        
        # Clean up expired email verification tokens
        expired_verification_tokens = EmailVerificationToken.query.filter(
            EmailVerificationToken.expires_at < now
        ).all()
        
        for token in expired_verification_tokens:
            db.session.delete(token)
        
        db.session.commit()
        
        logger.info(f"Cleaned up {len(expired_password_tokens)} password tokens and {len(expired_verification_tokens)} verification tokens")
        
    except Exception as e:
        logger.error(f"Error cleaning up tokens: {e}")
        db.session.rollback()


def get_email_template(template_name):
    """Get email template content."""
    templates = {
        'conversion_complete': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Conversion Complete</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #8B5CF6, #06B6D4); color: white; padding: 30px 20px; text-align: center; border-radius: 8px; }
                .content { background: #f9f9f9; padding: 30px 20px; border-radius: 8px; margin: 20px 0; }
                .button { display: inline-block; background: #8B5CF6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }
                .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Your Conversion is Ready!</h1>
                </div>
                <div class="content">
                    <p>Hi {{ account.username }},</p>
                    <p>Great news! Your screenshot conversion has been completed successfully.</p>
                    <p><strong>File:</strong> {{ conversion.original_filename }}<br>
                       <strong>Framework:</strong> {{ conversion.framework|title }}<br>
                       <strong>Completed:</strong> {{ conversion.updated_at.strftime('%B %d, %Y at %I:%M %p') }}</p>
                    <p><a href="{{ result_url }}" class="button">View Your Code</a></p>
                    <p>You can view, edit, and download your converted code from your dashboard.</p>
                </div>
                <div class="footer">
                    <p>Happy coding!<br>The Screenshot to Code Team</p>
                </div>
            </div>
        </body>
        </html>
        ''',
        
        'low_credit_warning': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Low Credits Warning</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #F59E0B, #EF4444); color: white; padding: 30px 20px; text-align: center; border-radius: 8px; }
                .content { background: #fff8f1; padding: 30px 20px; border-radius: 8px; margin: 20px 0; border: 2px solid #F59E0B; }
                .button { display: inline-block; background: #F59E0B; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }
                .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚡ Running Low on Credits</h1>
                </div>
                <div class="content">
                    <p>Hi {{ account.username }},</p>
                    <p>You currently have <strong>{{ account.credits_remaining|int }} credit</strong> remaining.</p>
                    <p>Don't let your creative flow stop! Get more credits to continue converting your screenshots into beautiful code.</p>
                    <p><a href="{{ pricing_url }}" class="button">Buy More Credits</a></p>
                    <p>Our credit packages start at just $1.99 for 2 conversions.</p>
                </div>
                <div class="footer">
                    <p>Keep creating!<br>The Screenshot to Code Team</p>
                </div>
            </div>
        </body>
        </html>
        ''',
        
        'welcome': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Screenshot to Code</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #8B5CF6, #06B6D4); color: white; padding: 30px 20px; text-align: center; border-radius: 8px; }
                .content { background: #f9f9f9; padding: 30px 20px; border-radius: 8px; margin: 20px 0; }
                .button { display: inline-block; background: #8B5CF6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 5px; }
                .feature { background: white; padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #8B5CF6; }
                .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Welcome to Screenshot to Code!</h1>
                </div>
                <div class="content">
                    <p>Hi {{ account.username }},</p>
                    <p>Welcome to the most powerful AI-powered screenshot-to-code converter! We're excited to have you on board.</p>
                    
                    <div class="feature">
                        <h3>🎁 You have 3 FREE conversions</h3>
                        <p>Start exploring right away with your complimentary credits!</p>
                    </div>
                    
                    <div class="feature">
                        <h3>⚡ Supported Frameworks</h3>
                        <p>React, Vue.js, HTML/CSS/JS, Svelte, and Angular</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🎨 CSS Frameworks</h3>
                        <p>Tailwind CSS, Bootstrap, or plain CSS</p>
                    </div>
                    
                    <p><a href="{{ upload_url }}" class="button">Start Converting</a>
                       <a href="{{ dashboard_url }}" class="button">Visit Dashboard</a></p>
                </div>
                <div class="footer">
                    <p>Happy coding!<br>The Screenshot to Code Team</p>
                </div>
            </div>
        </body>
        </html>
        ''',
        
        'weekly_summary': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Weekly Summary</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #8B5CF6, #06B6D4); color: white; padding: 30px 20px; text-align: center; border-radius: 8px; }
                .content { background: #f9f9f9; padding: 30px 20px; border-radius: 8px; margin: 20px 0; }
                .stat { background: white; padding: 20px; margin: 10px 0; border-radius: 6px; text-align: center; }
                .stat h3 { margin: 0; color: #8B5CF6; font-size: 2em; }
                .button { display: inline-block; background: #8B5CF6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }
                .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Your Weekly Summary</h1>
                </div>
                <div class="content">
                    <p>Hi {{ account.username }},</p>
                    <p>Here's a summary of your activity this week:</p>
                    
                    <div class="stat">
                        <h3>{{ weekly_conversions }}</h3>
                        <p>Total Conversions</p>
                    </div>
                    
                    <div class="stat">
                        <h3>{{ success_rate }}%</h3>
                        <p>Success Rate</p>
                    </div>
                    
                    <div class="stat">
                        <h3>{{ account.credits_remaining|int }}</h3>
                        <p>Credits Remaining</p>
                    </div>
                    
                    <p><a href="{{ dashboard_url }}" class="button">View Dashboard</a></p>
                </div>
                <div class="footer">
                    <p>Keep up the great work!<br>The Screenshot to Code Team</p>
                </div>
            </div>
        </body>
        </html>
        ''',
        
        'purchase_receipt': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Purchase Receipt</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #10B981, #059669); color: white; padding: 30px 20px; text-align: center; border-radius: 8px; }
                .content { background: #f0fdf4; padding: 30px 20px; border-radius: 8px; margin: 20px 0; border: 2px solid #10B981; }
                .receipt { background: white; padding: 20px; border-radius: 6px; margin: 20px 0; }
                .button { display: inline-block; background: #10B981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }
                .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💳 Purchase Receipt</h1>
                </div>
                <div class="content">
                    <p>Hi {{ account.username }},</p>
                    <p>Thank you for your purchase! Your credits have been added to your account.</p>
                    
                    <div class="receipt">
                        <h3>Order Details</h3>
                        <p><strong>Package:</strong> {{ order.package_type|replace('_', ' ')|title }}</p>
                        <p><strong>Credits:</strong> {{ order.credits_purchased }} credits</p>
                        <p><strong>Amount:</strong> ${{ order.amount }}</p>
                        <p><strong>Date:</strong> {{ order.created_at.strftime('%B %d, %Y at %I:%M %p') }}</p>
                        <p><strong>Order ID:</strong> {{ order.id }}</p>
                    </div>
                    
                    <p><a href="{{ billing_url }}" class="button">View Billing History</a></p>
                    <p>Your credits are now available and ready to use!</p>
                </div>
                <div class="footer">
                    <p>Happy converting!<br>The Screenshot to Code Team</p>
                </div>
            </div>
        </body>
        </html>
        '''
    }
    
    return templates.get(template_name)
