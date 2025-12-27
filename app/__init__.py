# app/__init__.py
"""Flask application factory."""

import logging
from flask import Flask
from app.extensions import db, login_manager, migrate, csrf, mail, bcrypt, moment
from config import config


def create_app(config_name='development'):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Optimize logging for performance
    if config_name == 'production' or not app.debug:
        # Reduce logging verbosity in production
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.WARNING)
        
        # Disable SQLAlchemy logging for performance
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
    else:
        # Keep INFO level for development
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.INFO)
        
        # Disable SQLAlchemy logging even in development
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    moment.init_app(app)
    
    # Initialize database monitoring after db is initialized (only in production)
    if not app.debug and config_name == 'production':
        with app.app_context():
            from app.database import init_db_monitoring, test_db_connection
            try:
                init_db_monitoring()
            except Exception as e:
                app.logger.error(f"Failed to initialize database monitoring: {e}")
    
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
    
    from app.launch import launch as launch_blueprint
    app.register_blueprint(launch_blueprint, url_prefix='/launch')
    
    # Initialize launch tracking middleware (optimized for performance)
    from app.launch.middleware_optimized import init_optimized_launch_tracking
    init_optimized_launch_tracking(app)
    
    # Register health check endpoints
    from app.health import register_health_blueprint
    register_health_blueprint(app)
    
    # Register custom Jinja filters
    register_jinja_filters(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_commands(app)
    
    return app


def register_jinja_filters(app):
    """Register custom Jinja filters."""
    @app.template_filter('number_format')
    def number_format(value):
        """Format numbers with thousands separator."""
        try:
            return "{:,}".format(int(value))
        except (ValueError, TypeError):
            return value


def register_error_handlers(app):
    """Register error handlers."""
    from flask import render_template, request, flash, redirect, url_for
    from sqlalchemy.exc import OperationalError, DisconnectionError
    from app.database import DatabaseConnectionError, recover_db_connection
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        try:
            db.session.rollback()
        except Exception as e:
            app.logger.error(f"Error during rollback: {e}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def rate_limit_error(error):
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(OperationalError)
    @app.errorhandler(DisconnectionError)
    @app.errorhandler(DatabaseConnectionError)
    def database_error(error):
        """Handle database connection errors."""
        error_msg = str(error)
        app.logger.error(f"Database error: {error_msg}")
        
        # Try to recover connection
        try:
            recover_db_connection()
            app.logger.info("Database connection recovered")
            flash('Connection restored. Please try again.', 'info')
        except Exception as e:
            app.logger.error(f"Failed to recover database connection: {e}")
            flash('We are experiencing technical difficulties. Please try again later.', 'error')
        
        # Redirect to home page or show error page
        if request.endpoint and 'api' in request.endpoint:
            return {'error': 'Database connection issue, please try again'}, 503
        else:
            return render_template('errors/503.html'), 503


def register_commands(app):
    """Register CLI commands."""
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        print('Database initialized.')
    
    @app.cli.command()
    def send_weekly_summaries():
        """Send weekly summaries to all active users."""
        from app.tasks.email_tasks import send_weekly_summary
        send_weekly_summary.delay()
        print('Weekly summary emails queued.')
    
    @app.cli.command()
    def cleanup_tokens():
        """Clean up expired tokens."""
        from app.tasks.email_tasks import cleanup_expired_tokens
        cleanup_expired_tokens.delay()
        print('Token cleanup queued.')
    
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
    def test_db():
        """Test database connection."""
        from app.database import test_db_connection, get_db_connection_info
        
        print('Testing database connection...')
        try:
            if test_db_connection():
                print('✓ Database connection successful')
                conn_info = get_db_connection_info()
                print(f'Connection pool info: {conn_info}')
            else:
                print('✗ Database connection failed')
        except Exception as e:
            print(f'✗ Database test error: {e}')
    
    @app.cli.command()
    def recover_db():
        """Recover database connection."""
        from app.database import recover_db_connection
        
        print('Attempting database connection recovery...')
        try:
            recover_db_connection()
            print('✓ Database connection recovered successfully')
        except Exception as e:
            print(f'✗ Database recovery failed: {e}')
    
    @app.cli.command()
    def db_status():
        """Show detailed database status."""
        from app.database import test_db_connection, get_db_connection_info
        from sqlalchemy import text
        
        print('Database Status Report')
        print('=' * 50)
        
        # Test connection
        try:
            connected = test_db_connection()
            print(f'Connection Status: {"✓ Connected" if connected else "✗ Disconnected"}')
        except Exception as e:
            print(f'Connection Status: ✗ Error - {e}')
            return
        
        # Get connection pool info
        try:
            conn_info = get_db_connection_info()
            print(f'Pool Size: {conn_info.get("pool_size", "unknown")}')
            print(f'Checked Out: {conn_info.get("checked_out", "unknown")}')
            print(f'Checked In: {conn_info.get("checked_in", "unknown")}')
            print(f'Overflow: {conn_info.get("overflow", "unknown")}')
            print(f'Invalid: {conn_info.get("invalid", "unknown")}')
        except Exception as e:
            print(f'Pool Info Error: {e}')
        
        # Test query performance
        try:
            import time
            start = time.time()
            with db.engine.connect() as conn:
                result = conn.execute(text('SELECT COUNT(*) FROM accounts'))
                count = result.scalar()
            end = time.time()
            print(f'Query Performance: {(end - start) * 1000:.2f}ms')
            print(f'Total Accounts: {count}')
        except Exception as e:
            print(f'Query Test Error: {e}')
    
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
    
    @app.cli.command()
    def send_weekly_summaries():
        """Send weekly summary emails to active users."""
        from app.tasks.email_tasks import send_weekly_summary
        
        print('Sending weekly summary emails...')
        try:
            send_weekly_summary.delay()
            print('✓ Weekly summary email task queued successfully.')
        except Exception as e:
            print(f'✗ Error queueing weekly summary task: {e}')
    
    @app.cli.command()
    def cleanup_tokens():
        """Clean up expired tokens."""
        from app.tasks.email_tasks import cleanup_expired_tokens
        
        print('Cleaning up expired tokens...')
        try:
            cleanup_expired_tokens.delay()
            print('✓ Token cleanup task queued successfully.')
        except Exception as e:
            print(f'✗ Error queueing cleanup task: {e}')
    
    @app.cli.command()
    def test_email():
        """Test email functionality."""
        from app.tasks.email_tasks import send_email_task
        
        email = input('Enter test email address: ').strip()
        if not email:
            print('Error: Email is required.')
            return
        
        print(f'Sending test email to {email}...')
        try:
            send_email_task.delay(
                to_email=email,
                subject="Test Email from Screenshot to Code",
                template_name='welcome',
                account={'username': 'Test User'},
                dashboard_url='http://localhost:5000/account/dashboard',
                upload_url='http://localhost:5000/converter/upload'
            )
            print('✓ Test email queued successfully.')
        except Exception as e:
            print(f'✗ Error sending test email: {e}')
