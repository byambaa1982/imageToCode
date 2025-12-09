# app/__init__.py
"""Flask application factory."""

import logging
from flask import Flask
from app.extensions import db, login_manager, migrate, csrf, mail, bcrypt
from config import config


def create_app(config_name='development'):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Reduce logging verbosity
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # Disable SQLAlchemy logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    # Initialize OAuth after registering auth blueprint
    from app.auth.routes import init_oauth
    init_oauth(app)
    
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.converter import converter as converter_blueprint
    app.register_blueprint(converter_blueprint, url_prefix='/converter')
    
    from app.account import account as account_blueprint
    app.register_blueprint(account_blueprint, url_prefix='/account')
    
    from app.payment import payment as payment_blueprint
    app.register_blueprint(payment_blueprint, url_prefix='/payment')
    
    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_commands(app)
    
    return app


def register_error_handlers(app):
    """Register error handlers."""
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def rate_limit_error(error):
        return render_template('errors/429.html'), 429


def register_commands(app):
    """Register CLI commands."""
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        print('Database initialized.')
    
    @app.cli.command()
    def seed_packages():
        """Seed the packages table with default data."""
        from app.models import Package
        
        packages = [
            Package(
                name='Starter Pack',
                code='starter_pack',
                description='2 additional conversions',
                price=1.99,
                credits=2.00,
                is_featured=False,
                badge=None,
                display_order=1
            ),
            Package(
                name='Pro Pack',
                code='pro_pack',
                description='3 conversions - Best Value!',
                price=2.49,
                credits=3.00,
                is_featured=True,
                badge='Most Popular',
                display_order=2
            ),
            Package(
                name='Bulk Pack',
                code='bulk_pack',
                description='10 conversions for power users',
                price=7.99,
                credits=10.00,
                is_featured=False,
                badge='Best Value',
                display_order=3
            )
        ]
        
        for package in packages:
            existing = Package.query.filter_by(code=package.code).first()
            if not existing:
                db.session.add(package)
        
        db.session.commit()
        print('Packages seeded successfully.')
    
    @app.cli.command()
    def create_admin():
        """Create an admin user."""
        from app.models import Account
        import getpass
        
        print('Create Admin User')
        print('-' * 50)
        
        email = input('Email: ').strip()
        if not email:
            print('Error: Email is required.')
            return
        
        # Check if user already exists
        existing = Account.query.filter_by(email=email).first()
        if existing:
            # Update existing user to admin
            existing.is_admin = True
            db.session.commit()
            print(f'✓ User {email} is now an admin.')
            return
        
        username = input('Username (optional): ').strip() or None
        password = getpass.getpass('Password: ')
        password_confirm = getpass.getpass('Confirm Password: ')
        
        if password != password_confirm:
            print('Error: Passwords do not match.')
            return
        
        if len(password) < 8:
            print('Error: Password must be at least 8 characters.')
            return
        
        # Create admin account
        admin = Account(
            email=email,
            username=username,
            email_verified=True,
            is_active=True,
            is_admin=True,
            credits_remaining=100.00  # Give admin some credits
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f'✓ Admin user created successfully!')
        print(f'  Email: {email}')
        print(f'  Username: {username or "N/A"}')
        print(f'  Credits: 100.00')
