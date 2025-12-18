# app/database.py
"""Database connection utilities and error handling."""

import logging
from functools import wraps
from sqlalchemy.exc import OperationalError, DisconnectionError
from sqlalchemy import text
from flask import current_app
from app.extensions import db

logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Custom exception for database connection issues."""
    pass


def handle_db_connection_error(func):
    """Decorator to handle database connection errors with retry logic."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                return func(*args, **kwargs)
            except (OperationalError, DisconnectionError) as e:
                retry_count += 1
                error_msg = str(e)
                
                # Check if it's a connection issue
                if any(phrase in error_msg.lower() for phrase in [
                    'mysql server has gone away',
                    'lost connection',
                    'broken pipe',
                    'connection reset',
                    'bad handshake'
                ]):
                    logger.warning(f"Database connection error (attempt {retry_count}/{max_retries}): {error_msg}")
                    
                    if retry_count < max_retries:
                        # Try to recover the connection
                        try:
                            recover_db_connection()
                            logger.info("Database connection recovered, retrying...")
                            continue
                        except Exception as recovery_error:
                            logger.error(f"Failed to recover database connection: {recovery_error}")
                    
                    if retry_count >= max_retries:
                        logger.error(f"Max retries exceeded for database operation: {error_msg}")
                        raise DatabaseConnectionError(f"Database connection failed after {max_retries} attempts")
                else:
                    # Not a connection error, re-raise
                    raise
            except Exception as e:
                # Non-connection related error, re-raise immediately
                raise
                
        return None
    
    return wrapper


def recover_db_connection():
    """Attempt to recover database connection."""
    try:
        # Dispose of the current connection pool
        db.engine.dispose()
        
        # Create new connection and test it
        with db.engine.connect() as connection:
            result = connection.execute(text('SELECT 1'))
            result.fetchone()
            
        logger.info("Database connection successfully recovered")
        return True
        
    except Exception as e:
        logger.error(f"Failed to recover database connection: {e}")
        raise


def test_db_connection():
    """Test the database connection."""
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text('SELECT 1 as test'))
            return result.fetchone() is not None
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def get_db_connection_info():
    """Get database connection information for debugging."""
    try:
        pool = db.engine.pool
        return {
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'invalid': pool.invalid(),
            'total_connections': pool.size() + pool.overflow()
        }
    except Exception as e:
        logger.error(f"Failed to get connection info: {e}")
        return {}


def safe_db_query(query_func, *args, **kwargs):
    """Safely execute a database query with automatic retry on connection failure."""
    @handle_db_connection_error
    def _execute_query():
        return query_func(*args, **kwargs)
    
    return _execute_query()


# Context manager for safe database operations
class SafeDBSession:
    """Context manager for safe database operations."""
    
    def __enter__(self):
        self.session = db.session
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            # Check if it's a connection error
            if isinstance(exc_val, (OperationalError, DisconnectionError)):
                error_msg = str(exc_val)
                if any(phrase in error_msg.lower() for phrase in [
                    'mysql server has gone away',
                    'lost connection',
                    'broken pipe'
                ]):
                    logger.warning(f"Database connection error in session: {error_msg}")
                    try:
                        self.session.rollback()
                        recover_db_connection()
                    except Exception as e:
                        logger.error(f"Failed to recover in session context: {e}")
            else:
                try:
                    self.session.rollback()
                except Exception as e:
                    logger.error(f"Failed to rollback session: {e}")
        else:
            try:
                self.session.commit()
            except (OperationalError, DisconnectionError) as e:
                logger.warning(f"Connection error during commit: {e}")
                try:
                    self.session.rollback()
                    recover_db_connection()
                    # Retry commit once
                    self.session.commit()
                except Exception as retry_error:
                    logger.error(f"Failed to commit after recovery: {retry_error}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error during commit: {e}")
                self.session.rollback()
                raise


# Utility functions for common database operations
@handle_db_connection_error
def safe_get_user_by_id(user_id):
    """Safely get user by ID with connection error handling."""
    from app.models import Account  # Import here to avoid circular imports
    return Account.query.get(user_id)


@handle_db_connection_error
def safe_get_user_by_email(email):
    """Safely get user by email with connection error handling."""
    from app.models import Account
    return Account.query.filter_by(email=email).first()


@handle_db_connection_error
def safe_create_user(**kwargs):
    """Safely create a new user with connection error handling."""
    from app.models import Account
    
    with SafeDBSession() as session:
        user = Account(**kwargs)
        session.add(user)
        session.flush()  # Get the ID without committing
        return user


def init_db_monitoring():
    """Initialize database connection monitoring."""
    logger.info("Database connection monitoring initialized")
    
    # Test initial connection
    if test_db_connection():
        logger.info("Initial database connection test successful")
    else:
        logger.error("Initial database connection test failed")
        
    # Log connection pool info
    conn_info = get_db_connection_info()
    logger.info(f"Database connection pool info: {conn_info}")
