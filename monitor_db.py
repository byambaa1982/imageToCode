#!/usr/bin/env python3
"""
Database monitoring script for Screenshot to Code.
Checks database connection health and attempts recovery if needed.
"""

import sys
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_database_health():
    """Check database health and attempt recovery if needed."""
    try:
        # Import Flask app
        from app import create_app
        from app.database import test_db_connection, recover_db_connection, get_db_connection_info
        
        app = create_app()
        
        with app.app_context():
            logger.info("Starting database health check...")
            
            # Test connection
            if test_db_connection():
                logger.info("✓ Database connection is healthy")
                
                # Get connection info
                conn_info = get_db_connection_info()
                logger.info(f"Connection pool status: {conn_info}")
                
                return True
            else:
                logger.warning("✗ Database connection failed, attempting recovery...")
                
                # Attempt recovery
                try:
                    recover_db_connection()
                    
                    # Test again
                    if test_db_connection():
                        logger.info("✓ Database connection recovered successfully")
                        return True
                    else:
                        logger.error("✗ Database recovery failed")
                        return False
                        
                except Exception as e:
                    logger.error(f"✗ Database recovery error: {e}")
                    return False
                    
    except Exception as e:
        logger.error(f"✗ Health check error: {e}")
        return False


def continuous_monitoring(interval=30):
    """Run continuous database monitoring."""
    logger.info(f"Starting continuous monitoring (check every {interval}s)")
    logger.info("Press Ctrl+C to stop monitoring")
    
    consecutive_failures = 0
    max_failures = 3
    
    try:
        while True:
            try:
                if check_database_health():
                    consecutive_failures = 0
                    logger.info(f"Next check in {interval} seconds...")
                else:
                    consecutive_failures += 1
                    logger.warning(f"Consecutive failures: {consecutive_failures}/{max_failures}")
                    
                    if consecutive_failures >= max_failures:
                        logger.error("Max consecutive failures reached. Manual intervention required.")
                        sys.exit(1)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(5)  # Short delay before retrying
                
    except KeyboardInterrupt:
        logger.info("Monitoring stopped")
        sys.exit(0)


def main():
    """Main function."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'check':
            # Single health check
            success = check_database_health()
            sys.exit(0 if success else 1)
            
        elif command == 'monitor':
            # Continuous monitoring
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            continuous_monitoring(interval)
            
        elif command == 'help':
            print("Database Health Monitor")
            print("Usage:")
            print("  python monitor_db.py check          - Single health check")
            print("  python monitor_db.py monitor [N]    - Continuous monitoring (every N seconds, default 30)")
            print("  python monitor_db.py help           - Show this help")
            sys.exit(0)
        else:
            print(f"Unknown command: {command}")
            print("Use 'python monitor_db.py help' for usage information")
            sys.exit(1)
    else:
        # Default: single check
        success = check_database_health()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
