# config.py
"""Application configuration."""

import os
import socket
import urllib.parse
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Only import SSH tunnel if needed (for local development against production DB)
try:
    from sshtunnel import SSHTunnelForwarder
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MySQL/PythonAnywhere configuration
    SSH_HOST = 'ssh.pythonanywhere.com'
    SSH_USERNAME = 'byambaa1982'
    SSH_PASSWORD = os.environ.get('SSH_PASSWORD') or 'Python@1982'
    DB_HOST = 'byambaa1982.mysql.pythonanywhere-services.com'
    DB_USER = 'byambaa1982'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'Mysql@1982'
    DB_NAME = 'byambaa1982$codemirror'
    
    # SSH tunnel (for local development)
    _ssh_tunnel = None
    _is_on_pythonanywhere = None
    
    # Database
    SQLALCHEMY_DATABASE_URI = None  # Will be set dynamically
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_POOL_RECYCLE = 280
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@screenshot-to-code.com'
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    
    # AI API
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    AI_MODEL = os.environ.get('AI_MODEL') or 'gpt-4-vision-preview'
    
    # Stripe
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    
    # Storage
    STORAGE_TYPE = os.environ.get('STORAGE_TYPE') or 'local'  # local or gcs
    GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME')
    GCS_PROJECT_ID = os.environ.get('GCS_PROJECT_ID')
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/1'
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Application
    APP_NAME = 'Screenshot to Code'
    APP_URL = os.environ.get('APP_URL') or 'http://localhost:5000'
    
    # Credits
    FREE_CREDITS_ON_SIGNUP = 3.0
    CREDITS_PER_CONVERSION = 1.0
    
    @classmethod
    def is_on_pythonanywhere(cls):
        """Check if we're running on PythonAnywhere."""
        if cls._is_on_pythonanywhere is None:
            hostname = socket.gethostname()
            cls._is_on_pythonanywhere = (
                'pythonanywhere' in hostname.lower() or
                os.getenv('PYTHONANYWHERE_SITE') is not None or
                os.path.exists('/home/byambaa1982')
            )
        return cls._is_on_pythonanywhere
    
    @classmethod
    def start_ssh_tunnel(cls):
        """Start SSH tunnel (only for local development)."""
        if not SSH_AVAILABLE:
            print("Warning: sshtunnel package not available. Install with: pip install sshtunnel")
            return None
        
        if cls._ssh_tunnel is None or not cls._ssh_tunnel.is_active:
            cls._ssh_tunnel = SSHTunnelForwarder(
                (cls.SSH_HOST, 22),
                ssh_username=cls.SSH_USERNAME,
                ssh_password=cls.SSH_PASSWORD,
                remote_bind_address=(cls.DB_HOST, 3306),
                local_bind_address=('127.0.0.1', 3307)
            )
            cls._ssh_tunnel.start()
            # print(f"SSH tunnel started on local port {cls._ssh_tunnel.local_bind_port}")
        return cls._ssh_tunnel
    
    @classmethod
    def stop_ssh_tunnel(cls):
        """Stop SSH tunnel."""
        if cls._ssh_tunnel:
            cls._ssh_tunnel.stop()
            # print("SSH tunnel stopped")
    
    @classmethod
    def get_mysql_uri(cls):
        """Get MySQL URI based on environment."""
        encoded_password = urllib.parse.quote(cls.DB_PASSWORD)
        
        if cls.is_on_pythonanywhere():
            # Direct connection on PythonAnywhere
            # print("Running on PythonAnywhere - using direct MySQL connection")
            return (
                f"mysql+pymysql://{cls.DB_USER}:{encoded_password}"
                f"@{cls.DB_HOST}/{cls.DB_NAME}"
                f"?charset=utf8mb4"
            )
        else:
            # Local development - use SSH tunnel
            # print("Running locally - using SSH tunnel to PythonAnywhere")
            tunnel = cls.start_ssh_tunnel()
            if tunnel and tunnel.is_active:
                return (
                    f"mysql+pymysql://{cls.DB_USER}:{encoded_password}"
                    f"@127.0.0.1:{tunnel.local_bind_port}/{cls.DB_NAME}"
                    f"?charset=utf8mb4"
                )
            else:
                # print("Warning: SSH tunnel not available, falling back to direct connection")
                return (
                    f"mysql+pymysql://{cls.DB_USER}:{encoded_password}"
                    f"@{cls.DB_HOST}/{cls.DB_NAME}"
                    f"?charset=utf8mb4"
                )
    
    @staticmethod
    def init_app(app):
        """Initialize application."""
        # Set the database URI dynamically
        if app.config.get('SQLALCHEMY_DATABASE_URI') is None:
            app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_mysql_uri()
        # print(f"Database URI configured: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'Unknown'}")


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = False  # Disabled to reduce log verbosity
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_MAX_OVERFLOW = 20
    SQLALCHEMY_POOL_TIMEOUT = 30
    
    @classmethod
    def init_app(cls, app):
        # Set database URI before calling parent init_app
        if app.config.get('SQLALCHEMY_DATABASE_URI') is None:
            app.config['SQLALCHEMY_DATABASE_URI'] = cls.get_mysql_uri()
        
        Config.init_app(app)
        
        # Create upload folder if it doesn't exist
        import os
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    # Optimized for PythonAnywhere
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_MAX_OVERFLOW = 10
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_POOL_TIMEOUT = 20
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
        'connect_args': {
            'connect_timeout': 10,
            'read_timeout': 30,
            'write_timeout': 30,
        }
    }
    
    @classmethod
    def init_app(cls, app):
        # Set database URI before calling parent init_app
        if app.config.get('SQLALCHEMY_DATABASE_URI') is None:
            app.config['SQLALCHEMY_DATABASE_URI'] = cls.get_mysql_uri()
        
        Config.init_app(app)
        
        # Log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
