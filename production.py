import pymysql
import urllib.parse
import os
import socket

# Only import SSH tunnel if needed (for local development against production DB)
try:
    from sshtunnel import SSHTunnelForwarder
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False


class ProductionConfig:
    DEBUG = False
    SECRET_KEY = 'prod-secret-key'

    SSH_HOST = 'ssh.pythonanywhere.com'
    SSH_USERNAME = 'byambaa1982'
    SSH_PASSWORD = 'Python@1982'
    DB_HOST = 'byambaa1982.mysql.pythonanywhere-services.com'
    DB_USER = 'byambaa1982'
    DB_PASSWORD = 'Mysql@1982'
    DB_NAME = 'byambaa1982$codemirror'

    server = None
    _is_on_pythonanywhere = None

    @classmethod
    def is_on_pythonanywhere(cls):
        """Check if we're running on PythonAnywhere."""
        if cls._is_on_pythonanywhere is None:
            # Check for PythonAnywhere-specific environment variables or hostname
            hostname = socket.gethostname()
            cls._is_on_pythonanywhere = (
                'pythonanywhere' in hostname.lower() or
                os.getenv('PYTHONANYWHERE_SITE') is not None or
                os.path.exists('/home/byambaa1982')  # PythonAnywhere home directory
            )
        return cls._is_on_pythonanywhere

    @classmethod
    def start_ssh_tunnel(cls):
        """Start SSH tunnel (only for local development)."""
        if not SSH_AVAILABLE:
            raise ImportError("sshtunnel package not available")
        
        if cls.server is None or not cls.server.is_active:
            cls.server = SSHTunnelForwarder(
                (cls.SSH_HOST, 22),
                ssh_username=cls.SSH_USERNAME,
                ssh_password=cls.SSH_PASSWORD,
                remote_bind_address=(cls.DB_HOST, 3306),
                local_bind_address=('127.0.0.1', 3307)
            )
            cls.server.start()
            print(f"SSH tunnel started on local port {cls.server.local_bind_port}")

    @classmethod
    def stop_ssh_tunnel(cls):
        """Stop SSH tunnel."""
        if cls.server:
            cls.server.stop()
            print("SSH tunnel stopped")

    @classmethod
    def get_mysql_uri(cls):
        """Get MySQL URI based on environment."""
        encoded_password = urllib.parse.quote(cls.DB_PASSWORD)
        
        if cls.is_on_pythonanywhere():
            # Direct connection on PythonAnywhere (no SSH tunnel needed)
            # Use mysqlclient (faster C-based driver) instead of pymysql
            print("Running on PythonAnywhere - using direct MySQL connection with mysqlclient")
            return (
                f"mysql+mysqldb://{cls.DB_USER}:{encoded_password}"
                f"@{cls.DB_HOST}/{cls.DB_NAME}"
                f"?charset=utf8mb4"
            )
        else:
            # Local development - use SSH tunnel with pymysql
            print("Running locally - using SSH tunnel to PythonAnywhere")
            if not cls.server or not cls.server.is_active:
                cls.start_ssh_tunnel()
            
            return (
                f"mysql+pymysql://{cls.DB_USER}:{encoded_password}"
                f"@127.0.0.1:{cls.server.local_bind_port}/{cls.DB_NAME}"
                f"?charset=utf8mb4"
            )

    @classmethod
    def init_app(cls):
        """Initialize app configuration."""
        cls.SQLALCHEMY_DATABASE_URI = cls.get_mysql_uri()
        cls.SQLALCHEMY_TRACK_MODIFICATIONS = False
        
        # Optimized database connection pooling for PythonAnywhere
        if cls.is_on_pythonanywhere():
            # PythonAnywhere has connection limits, so optimize accordingly
            cls.SQLALCHEMY_POOL_SIZE = 5  # Reduced from 10
            cls.SQLALCHEMY_MAX_OVERFLOW = 10  # Reduced from 20
            cls.SQLALCHEMY_POOL_RECYCLE = 280  # 280 seconds (< 300s MySQL timeout)
            cls.SQLALCHEMY_POOL_TIMEOUT = 20
            cls.SQLALCHEMY_POOL_PRE_PING = True  # Verify connections before using
            cls.SQLALCHEMY_ECHO = False  # Disable SQL logging in production
            
            # Additional engine options for better performance
            cls.SQLALCHEMY_ENGINE_OPTIONS = {
                'pool_pre_ping': True,
                'pool_recycle': 280,
                'connect_args': {
                    'connect_timeout': 10,
                    'read_timeout': 30,
                    'write_timeout': 30,
                }
            }
        else:
            # Local development settings
            cls.SQLALCHEMY_POOL_SIZE = 10
            cls.SQLALCHEMY_POOL_RECYCLE = 3600
            cls.SQLALCHEMY_POOL_TIMEOUT = 30
            cls.SQLALCHEMY_MAX_OVERFLOW = 20
            cls.SQLALCHEMY_POOL_PRE_PING = True
            cls.SQLALCHEMY_ECHO = False
        
        print(f"Production config initialized: {cls.SQLALCHEMY_DATABASE_URI.split('@')[1] if '@' in cls.SQLALCHEMY_DATABASE_URI else 'Unknown'}")