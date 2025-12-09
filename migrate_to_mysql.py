"""Migrate database schema and data from SQLite to MySQL."""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from sqlalchemy import create_engine, text, inspect
from config import DevelopmentConfig

def migrate_to_mysql():
    """Migrate tables from SQLite to MySQL."""
    print("=" * 60)
    print("Database Migration: SQLite to MySQL")
    print("=" * 60)
    
    # Create MySQL connection
    print("\n[1/5] Connecting to MySQL...")
    mysql_uri = DevelopmentConfig.get_mysql_uri()
    mysql_engine = create_engine(mysql_uri, echo=False)
    
    try:
        with mysql_engine.connect() as conn:
            result = conn.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0]
            print(f"✓ Connected to MySQL database: {db_name}")
    except Exception as e:
        print(f"✗ Failed to connect to MySQL: {e}")
        return False
    
    # Create Flask app with MySQL config
    print("\n[2/5] Creating Flask app with MySQL configuration...")
    app = create_app('development')
    
    with app.app_context():
        # Get inspector to check existing tables
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print(f"\n[3/5] Checking existing tables in MySQL...")
        if existing_tables:
            print(f"Found {len(existing_tables)} existing tables: {', '.join(existing_tables[:5])}")
            print("\nOptions:")
            print("  1. Drop all tables and recreate (WARNING: This will delete all data!)")
            print("  2. Create only missing tables (safe)")
            print("  3. Cancel")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                print("\n⚠️  WARNING: This will DROP ALL TABLES!")
                confirm = input("Type 'YES' to confirm: ").strip()
                if confirm != 'YES':
                    print("Migration cancelled.")
                    return False
                
                print("\nDropping all tables...")
                db.drop_all()
                print("✓ All tables dropped")
            elif choice == '2':
                print("\nWill create only missing tables...")
            else:
                print("Migration cancelled.")
                return False
        else:
            print("No existing tables found. Will create all tables.")
        
        # Create all tables
        print("\n[4/5] Creating tables in MySQL...")
        try:
            db.create_all()
            
            # Verify tables were created
            inspector = inspect(db.engine)
            new_tables = inspector.get_table_names()
            print(f"✓ Successfully created {len(new_tables)} tables:")
            for table in sorted(new_tables):
                print(f"  - {table}")
            
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
            return False
        
        # Optionally migrate data from SQLite
        print("\n[5/5] Data Migration")
        sqlite_path = os.path.join(app.instance_path, 'screenshot_to_code.db')
        
        if os.path.exists(sqlite_path):
            print(f"\nFound SQLite database at: {sqlite_path}")
            migrate_data = input("Do you want to migrate data from SQLite? (y/n): ").strip().lower()
            
            if migrate_data == 'y':
                print("\nMigrating data from SQLite...")
                try:
                    sqlite_uri = f'sqlite:///{sqlite_path}'
                    sqlite_engine = create_engine(sqlite_uri, echo=False)
                    
                    # Get all tables from SQLite
                    sqlite_inspector = inspect(sqlite_engine)
                    sqlite_tables = sqlite_inspector.get_table_names()
                    
                    migrated_count = 0
                    for table_name in sqlite_tables:
                        if table_name in new_tables:
                            try:
                                # Read from SQLite
                                with sqlite_engine.connect() as sqlite_conn:
                                    result = sqlite_conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                                    count = result.fetchone()[0]
                                    
                                    if count > 0:
                                        print(f"\n  Migrating {table_name} ({count} rows)...")
                                        
                                        # Read all data
                                        result = sqlite_conn.execute(text(f"SELECT * FROM {table_name}"))
                                        rows = result.fetchall()
                                        columns = result.keys()
                                        
                                        # Insert into MySQL
                                        with mysql_engine.connect() as mysql_conn:
                                            # Build insert statement
                                            cols = ', '.join([f'`{col}`' for col in columns])
                                            placeholders = ', '.join([f':{col}' for col in columns])
                                            insert_sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
                                            
                                            # Insert rows
                                            for row in rows:
                                                row_dict = dict(zip(columns, row))
                                                mysql_conn.execute(text(insert_sql), row_dict)
                                            
                                            mysql_conn.commit()
                                        
                                        print(f"  ✓ Migrated {count} rows from {table_name}")
                                        migrated_count += 1
                                    else:
                                        print(f"  - {table_name} is empty, skipping")
                            except Exception as e:
                                print(f"  ✗ Error migrating {table_name}: {e}")
                    
                    print(f"\n✓ Data migration completed: {migrated_count} tables migrated")
                    
                except Exception as e:
                    print(f"✗ Error during data migration: {e}")
        else:
            print(f"No SQLite database found at: {sqlite_path}")
    
    print("\n" + "=" * 60)
    print("✓ Migration completed successfully!")
    print("=" * 60)
    print("\nYou can now run your Flask app with:")
    print("  python app.py")
    
    # Cleanup
    DevelopmentConfig.stop_ssh_tunnel()
    
    return True

if __name__ == "__main__":
    try:
        success = migrate_to_mysql()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user.")
        DevelopmentConfig.stop_ssh_tunnel()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        DevelopmentConfig.stop_ssh_tunnel()
        sys.exit(1)
