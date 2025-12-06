# app/models.py
"""Database models."""

import uuid
from datetime import datetime, timedelta
from flask_login import UserMixin
from app.extensions import db, bcrypt


class Account(UserMixin, db.Model):
    """User account model."""
    
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), unique=True)
    
    # Status flags
    email_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Credits
    credits_remaining = db.Column(db.Numeric(10, 2), default=3.00)
    
    # Security
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    conversions = db.relationship('Conversion', backref='account', lazy='dynamic', cascade='all, delete-orphan')
    credit_transactions = db.relationship('CreditsTransaction', backref='account', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='account', lazy='dynamic', cascade='all, delete-orphan')
    sessions = db.relationship('AccountSession', backref='account', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Account {self.email}>'
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches hash."""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        """Check if account is locked."""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock if needed."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
    
    def reset_failed_login(self):
        """Reset failed login attempts."""
        self.failed_login_attempts = 0
        self.locked_until = None
        db.session.commit()
    
    def has_credits(self, amount=1.0):
        """Check if account has enough credits."""
        return float(self.credits_remaining) >= amount
    
    def deduct_credits(self, amount, description='Conversion'):
        """Deduct credits from account."""
        if not self.has_credits(amount):
            raise ValueError('Insufficient credits')
        
        self.credits_remaining -= amount
        
        # Create transaction record
        transaction = CreditsTransaction(
            account_id=self.id,
            amount=-amount,
            balance_after=self.credits_remaining,
            transaction_type='usage',
            description=description
        )
        db.session.add(transaction)
        db.session.commit()
    
    def add_credits(self, amount, description='Credit purchase', order_id=None):
        """Add credits to account."""
        self.credits_remaining += amount
        
        # Create transaction record
        transaction = CreditsTransaction(
            account_id=self.id,
            order_id=order_id,
            amount=amount,
            balance_after=self.credits_remaining,
            transaction_type='purchase',
            description=description
        )
        db.session.add(transaction)
        db.session.commit()


class Conversion(db.Model):
    """Conversion model."""
    
    __tablename__ = 'conversions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    
    # Input data
    original_image_url = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    
    # Conversion settings
    framework = db.Column(db.String(50), nullable=False, index=True)
    css_framework = db.Column(db.String(50))
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    
    # Generated code
    generated_html = db.Column(db.Text)
    generated_css = db.Column(db.Text)
    generated_js = db.Column(db.Text)
    
    # URLs
    preview_url = db.Column(db.String(500))
    download_url = db.Column(db.String(500))
    expires_at = db.Column(db.DateTime)
    
    # Metrics
    processing_time = db.Column(db.Numeric(8, 2))
    tokens_used = db.Column(db.Integer)
    cost = db.Column(db.Numeric(8, 4))
    
    # Audit
    ip_address = db.Column(db.String(45))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    feedback = db.relationship('ConversionFeedback', backref='conversion', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Conversion {self.uuid}>'


class CreditsTransaction(db.Model):
    """Credits transaction model."""
    
    __tablename__ = 'credits_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    
    # Transaction details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    balance_after = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False, index=True)
    
    # Description
    description = db.Column(db.String(500))
    extra_data = db.Column(db.JSON)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<CreditsTransaction {self.id} {self.amount}>'


class Order(db.Model):
    """Order model."""
    
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    
    # Pricing
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    tax_amount = db.Column(db.Numeric(10, 2), default=0.00)
    discount_amount = db.Column(db.Numeric(10, 2), default=0.00)
    coupon_code = db.Column(db.String(50))
    
    # Package purchased
    package_type = db.Column(db.String(50), nullable=False, index=True)
    credits_purchased = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Payment
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    stripe_payment_id = db.Column(db.String(255), unique=True, index=True)
    stripe_session_id = db.Column(db.String(255))
    payment_method_type = db.Column(db.String(50))
    
    # Extra data for storing additional payment information
    extra_data = db.Column(db.JSON)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    credit_transactions = db.relationship('CreditsTransaction', backref='order', lazy='dynamic')
    
    def __repr__(self):
        return f'<Order {self.id} {self.status}>'


class Package(db.Model):
    """Package model."""
    
    __tablename__ = 'packages'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Package details
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Pricing
    price = db.Column(db.Numeric(10, 2), nullable=False)
    credits = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Display
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_featured = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0, index=True)
    
    # Popular indicator
    badge = db.Column(db.String(50))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Package {self.name}>'


class PasswordResetToken(db.Model):
    """Password reset token model."""
    
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    token_hash = db.Column(db.String(255), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PasswordResetToken {self.id}>'
    
    def is_expired(self):
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at


class EmailVerificationToken(db.Model):
    """Email verification token model."""
    
    __tablename__ = 'email_verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    token_hash = db.Column(db.String(255), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailVerificationToken {self.id}>'
    
    def is_expired(self):
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at


class AccountSession(db.Model):
    """Account session model."""
    
    __tablename__ = 'account_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    session_token_hash = db.Column(db.String(255), nullable=False, index=True)
    
    # Session info
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    # Timestamps
    last_active_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AccountSession {self.id}>'


class ConversionFeedback(db.Model):
    """Conversion feedback model."""
    
    __tablename__ = 'conversion_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    conversion_id = db.Column(db.Integer, db.ForeignKey('conversions.id'), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    
    # Feedback
    rating = db.Column(db.Integer, nullable=False, index=True)
    feedback_text = db.Column(db.Text)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Ensure one feedback per conversion per account
    __table_args__ = (
        db.UniqueConstraint('conversion_id', 'account_id', name='unique_conversion_feedback'),
    )
    
    def __repr__(self):
        return f'<ConversionFeedback {self.id}>'


class APIKey(db.Model):
    """API key model (future)."""
    
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    
    # Key details
    key_hash = db.Column(db.String(255), nullable=False, index=True)
    name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Rate limiting
    rate_limit = db.Column(db.Integer, default=100)
    rate_limit_period = db.Column(db.String(20), default='hour')
    
    # Security
    scopes = db.Column(db.JSON)
    allowed_ips = db.Column(db.Text)
    
    # Usage tracking
    last_used_at = db.Column(db.DateTime, nullable=True)
    usage_count = db.Column(db.Integer, default=0)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<APIKey {self.id}>'


class AnalyticsEvent(db.Model):
    """Analytics event model."""
    
    __tablename__ = 'analytics_events'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True, index=True)
    
    # Event details
    event_type = db.Column(db.String(100), nullable=False, index=True)
    event_data = db.Column(db.JSON)
    
    # Session tracking
    session_id = db.Column(db.String(100), index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        db.Index('idx_account_event_type', 'account_id', 'event_type'),
    )
    
    def __repr__(self):
        return f'<AnalyticsEvent {self.event_type}>'
