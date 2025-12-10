"""Test MySQL connection using updated config.py"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DevelopmentConfig

def test_connection():
    print("=" * 60)
    print("Testing MySQL Connection to PythonAnywhere")
    print("=" * 60)
    
    # Check if we're on PythonAnywhere
    is_pythonanywhere = DevelopmentConfig.is_on_pythonanywhere()
    print(f"\nRunning on PythonAnywhere: {is_pythonanywhere}")
    
    # Get MySQL URI
    print("\nGenerating MySQL URI...")
    try:
        mysql_uri = DevelopmentConfig.get_mysql_uri()
        # Mask the password in the output
        masked_uri = mysql_uri.split('@')[0].split(':')[0] + ':****@' + mysql_uri.split('@')[1]
        print(f"MySQL URI: {masked_uri}")
    except Exception as e:
        print(f"Error generating MySQL URI: {e}")
        return False
    
    # Try to connect using SQLAlchemy
    print("\nTesting database connection with SQLAlchemy...")
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(
            mysql_uri,
            pool_pre_ping=True,
            pool_recycle=280,
            echo=False
        )
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE() as db, VERSION() as version, NOW() as now"))
            row = result.fetchone()
            print(f"✓ Connection successful!")
            print(f"  Database: {row[0]}")
            print(f"  MySQL Version: {row[1]}")
            print(f"  Server Time: {row[2]}")
            
            # List tables
            result = connection.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            print(f"\n✓ Found {len(tables)} tables:")
            for table in tables[:10]:  # Show first 10 tables
                print(f"  - {table[0]}")
            if len(tables) > 10:
                print(f"  ... and {len(tables) - 10} more")
        
        engine.dispose()
        print("\n" + "=" * 60)
        print("✓ MySQL connection test PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        print("\n" + "=" * 60)
        print("✗ MySQL connection test FAILED")
        print("=" * 60)
        return False
    finally:
        # Stop SSH tunnel if it was started
        if not is_pythonanywhere:
            print("\nStopping SSH tunnel...")
            DevelopmentConfig.stop_ssh_tunnel()

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
