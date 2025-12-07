# app/auth/routes.py
"""Authentication routes."""

import json
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, current_user, login_required
from authlib.integrations.flask_client import OAuth
from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.auth.utils import send_password_reset_email, send_verification_email, verify_password_reset_token, verify_email_token, send_welcome_email
from app.models import Account
from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return Account.query.get(int(user_id))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = Account.query.filter_by(email=form.email.data.lower()).first()
        
        if user is None:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Check if account is locked
        if user.is_locked():
            flash('Account is temporarily locked due to multiple failed login attempts. Please try again later.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Check if account is active
        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Verify password
        if not user.check_password(form.password.data):
            user.increment_failed_login()
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Reset failed login attempts
        user.reset_failed_login()
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        # Log user in
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('account.dashboard')
        
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Create new user
        user = Account(
            username=form.username.data,
            email=form.email.data.lower(),
            credits_remaining=current_app.config['FREE_CREDITS_ON_SIGNUP']
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        if send_verification_email(user):
            flash('Account created successfully! Please check your email to verify your account.', 'success')
        else:
            flash('Account created successfully! However, we could not send a verification email. Please contact support.', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Request password reset."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    
    if form.validate_on_submit():
        user = Account.query.filter_by(email=form.email.data.lower()).first()
        
        if user:
            if send_password_reset_email(user):
                flash('Check your email for instructions to reset your password.', 'info')
            else:
                flash('Failed to send password reset email. Please try again later.', 'danger')
        else:
            # Don't reveal if email exists or not
            flash('Check your email for instructions to reset your password.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    reset_token = verify_password_reset_token(token)
    
    if not reset_token:
        flash('Invalid or expired password reset link.', 'danger')
        return redirect(url_for('auth.login'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user = Account.query.get(reset_token.account_id)
        user.set_password(form.password.data)
        
        # Mark token as used
        reset_token.used = True
        db.session.commit()
        
        flash('Your password has been reset successfully. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)


@auth.route('/verify-email/<token>')
def verify_email(token):
    """Verify email with token."""
    if current_user.is_authenticated and current_user.email_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('account.dashboard'))
    
    verification_token = verify_email_token(token)
    
    if not verification_token:
        flash('Invalid or expired verification link.', 'danger')
        return redirect(url_for('main.index'))
    
    user = Account.query.get(verification_token.account_id)
    
    if user.email_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('auth.login'))
    
    # Mark email as verified
    user.email_verified = True
    verification_token.verified = True
    db.session.commit()
    
    # Send welcome email
    send_welcome_email(user)
    
    flash('Your email has been verified successfully! You can now log in.', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/resend-verification')
@login_required
def resend_verification():
    """Resend verification email."""
    if current_user.email_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('account.dashboard'))
    
    if send_verification_email(current_user):
        flash('Verification email sent. Please check your inbox.', 'success')
    else:
        flash('Failed to send verification email. Please try again later.', 'danger')
    
    return redirect(url_for('account.dashboard'))


# Initialize OAuth
oauth = OAuth()

def init_oauth(app):
    """Initialize OAuth with the Flask app."""
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


@auth.route('/google/login')
def google_login():
    """Redirect to Google OAuth login."""
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback."""
    try:
        # Get the token from Google
        token = oauth.google.authorize_access_token()
        
        # Get user info from Google
        user_info = token.get('userinfo')
        
        if not user_info:
            flash('Failed to get user information from Google.', 'danger')
            return redirect(url_for('auth.login'))
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name', '')
        email_verified = user_info.get('email_verified', False)
        
        if not email:
            flash('Google account does not have an email address.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Check if user already exists with this Google ID
        user = Account.query.filter_by(oauth_provider='google', oauth_id=google_id).first()
        
        if user:
            # Existing OAuth user - just log them in
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=True)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('account.dashboard'))
        
        # Check if user exists with this email (traditional login)
        user = Account.query.filter_by(email=email.lower()).first()
        
        if user:
            # Link existing account with Google OAuth
            user.oauth_provider = 'google'
            user.oauth_id = google_id
            user.oauth_extra = json.dumps(user_info)
            if email_verified:
                user.email_verified = True
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=True)
            flash(f'Your account has been linked with Google. Welcome back, {user.username}!', 'success')
            return redirect(url_for('account.dashboard'))
        
        # Create new user
        username = email.split('@')[0]
        # Make username unique if needed
        base_username = username
        counter = 1
        while Account.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = Account(
            username=username,
            email=email.lower(),
            oauth_provider='google',
            oauth_id=google_id,
            oauth_extra=json.dumps(user_info),
            email_verified=email_verified,
            credits_remaining=current_app.config.get('FREE_CREDITS_ON_SIGNUP', 3.00)
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email
        if email_verified:
            send_welcome_email(user)
        
        # Log user in
        login_user(user, remember=True)
        flash(f'Account created successfully! Welcome, {user.username}!', 'success')
        return redirect(url_for('account.dashboard'))
        
    except Exception as e:
        current_app.logger.error(f"Google OAuth error: {str(e)}")
        flash('An error occurred during Google login. Please try again.', 'danger')
        return redirect(url_for('auth.login'))
