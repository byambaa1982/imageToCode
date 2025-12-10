#!/usr/bin/env python
"""Test database connection script."""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test the database connection."""
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        return False
    
    print(f"\n📋 Database URL: {database_url.split('@')[0].split('://')[0]}://***:***@{database_url.split('@')[1] if '@' in database_url else 'N/A'}")
    
    try:
        # Create engine
        print("\n🔄 Creating database engine...")
        engine = create_engine(database_url, echo=False)
        
        # Test connection
        print("🔄 Testing connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            print("✅ Connection successful!")
            
            # Get database version
            result = connection.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            print(f"✅ MySQL Version: {version}")
            
            # Check if database exists and show tables
            result = connection.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            
            if tables:
                print(f"\n✅ Found {len(tables)} table(s) in database:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("\n⚠️  No tables found in database (run migrations to create tables)")
            
            # Check database info
            result = connection.execute(text("SELECT DATABASE()"))
            current_db = result.fetchone()[0]
            print(f"\n✅ Current database: {current_db}")
            
        print("\n" + "=" * 60)
        print("✅ DATABASE CONNECTION TEST PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Connection failed!")
        print(f"❌ Error details: {str(e)}")
        print("\n" + "=" * 60)
        print("❌ DATABASE CONNECTION TEST FAILED")
        print("=" * 60)
        return False


def test_flask_app_connection():
    """Test connection through Flask app."""
    print("\n\n" + "=" * 60)
    print("FLASK APP DATABASE TEST")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.extensions import db
        
        print("\n🔄 Creating Flask app...")
        app = create_app(os.getenv('FLASK_ENV', 'development'))
        
        with app.app_context():
            print("🔄 Testing database connection through Flask...")
            
            # Test connection
            db.session.execute(text("SELECT 1"))
            print("✅ Flask database connection successful!")
            
            # Get SQLAlchemy database URI (masked)
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            masked_uri = db_uri.split('@')[0].split('://')[0] + "://***:***@" + db_uri.split('@')[1] if '@' in db_uri else 'Not configured'
            print(f"✅ SQLAlchemy URI: {masked_uri}")
            
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"\n✅ Found {len(tables)} table(s):")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("\n⚠️  No tables found (run 'flask db upgrade' to create tables)")
            
        print("\n" + "=" * 60)
        print("✅ FLASK APP DATABASE TEST PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Flask app test failed!")
        print(f"❌ Error details: {str(e)}")
        print("\n" + "=" * 60)
        print("❌ FLASK APP DATABASE TEST FAILED")
        print("=" * 60)
        return False


if __name__ == '__main__':
    # Run direct connection test
    direct_test = test_database_connection()
    
    # Run Flask app test
    flask_test = test_flask_app_connection()
    
    # Summary
    print("\n\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Direct Connection Test: {'✅ PASSED' if direct_test else '❌ FAILED'}")
    print(f"Flask App Test:         {'✅ PASSED' if flask_test else '❌ FAILED'}")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if (direct_test and flask_test) else 1)
