#!/usr/bin/env python3
"""
Setup script for Phase 8 database tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, PromoCode, PromoCodeRedemption, LaunchMetric
from sqlalchemy import inspect

def setup_database():
    """Setup Phase 8 database tables"""
    print("=== Phase 8 Database Setup ===")
    
    try:
        app = create_app()
        print("✓ App created successfully")
        
        with app.app_context():
            print("✓ App context established")
            
            # Test database connection
            try:
                result = db.session.execute(db.text('SELECT 1'))
                print("✓ Database connection successful")
            except Exception as e:
                print(f"✗ Database connection failed: {e}")
                return False
            
            # Create all tables
            try:
                print("Creating all database tables...")
                db.create_all()
                print("✓ Tables created successfully")
            except Exception as e:
                print(f"✗ Error creating tables: {e}")
                return False
            
            # Verify tables exist
            try:
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"✓ Total tables in database: {len(tables)}")
                
                # Check required Phase 8 tables
                required_tables = [
                    ('promo_codes', PromoCode),
                    ('promo_code_redemptions', PromoCodeRedemption), 
                    ('launch_metrics', LaunchMetric)
                ]
                
                all_exist = True
                for table_name, model_class in required_tables:
                    if table_name in tables:
                        print(f"✓ {table_name} table exists")
                        
                        # Test model access
                        try:
                            count = db.session.query(model_class).count()
                            print(f"  - {count} records in {table_name}")
                        except Exception as e:
                            print(f"  - Warning: Could not query {table_name}: {e}")
                    else:
                        print(f"✗ {table_name} table missing")
                        all_exist = False
                
                if all_exist:
                    print("\n✅ Phase 8 database setup complete!")
                    print("All required tables are present and accessible.")
                    return True
                else:
                    print("\n❌ Phase 8 database setup incomplete!")
                    print("Some required tables are missing.")
                    return False
                    
            except Exception as e:
                print(f"✗ Error verifying tables: {e}")
                return False
                
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
