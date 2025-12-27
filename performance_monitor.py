#!/usr/bin/env python3
# performance_monitor.py
"""Performance monitoring script for Screenshot to Code."""

import time
import psutil
import os
import requests
from datetime import datetime


def check_app_performance():
    """Check application performance metrics."""
    print("🚀 Screenshot to Code Performance Monitor")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # Check system resources
    print("💻 System Resources:")
    print(f"  CPU Usage: {psutil.cpu_percent(interval=1):.1f}%")
    print(f"  Memory Usage: {psutil.virtual_memory().percent:.1f}%")
    print(f"  Disk Usage: {psutil.disk_usage('/').percent:.1f}%")
    print()
    
    # Check if Flask app is running
    flask_running = False
    flask_port = 5000
    
    try:
        # Check if port 5000 is in use
        connections = psutil.net_connections()
        for conn in connections:
            if conn.laddr.port == flask_port:
                flask_running = True
                break
    except:
        pass
    
    print("🌐 Application Status:")
    print(f"  Flask Server: {'✓ Running' if flask_running else '✗ Not running'}")
    
    if flask_running:
        # Test response time
        try:
            start_time = time.time()
            response = requests.get(f'http://localhost:{flask_port}/', timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            print(f"  Response Time: {response_time:.1f}ms")
            print(f"  Status Code: {response.status_code}")
            
            if response_time < 500:
                print("  Performance: ✓ Good (< 500ms)")
            elif response_time < 1000:
                print("  Performance: ⚠ Acceptable (500-1000ms)")
            else:
                print("  Performance: ✗ Slow (> 1000ms)")
                
        except requests.exceptions.RequestException as e:
            print(f"  Connection Error: {e}")
    
    print()
    
    # Check database file if SQLite
    db_path = "instance/screenshot_to_code.db"
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
        print("💾 Database:")
        print(f"  Size: {db_size:.2f} MB")
        print(f"  Path: {db_path}")
    
    # Performance recommendations
    print()
    print("💡 Performance Tips:")
    if flask_running:
        print("  ✓ Application is running")
    else:
        print("  • Start the application: python app.py")
    
    print("  • Use production config: export FLASK_ENV=production")
    print("  • Enable Redis caching if available")
    print("  • Monitor database connection pool")
    print("  • Use async processing for heavy tasks")


def benchmark_database():
    """Benchmark database operations."""
    print("\n📊 Database Performance Test")
    print("-" * 30)
    
    try:
        import sys
        sys.path.insert(0, '.')
        
        from app import create_app
        from app.extensions import db
        from app.models import Account
        
        app = create_app('development')
        
        with app.app_context():
            # Test simple query
            start_time = time.time()
            count = Account.query.count()
            query_time = (time.time() - start_time) * 1000
            
            print(f"Simple query time: {query_time:.1f}ms")
            print(f"Total accounts: {count}")
            
            # Test connection pool
            pool_info = db.engine.pool.status()
            print(f"Connection pool status: {pool_info}")
            
    except Exception as e:
        print(f"Database test failed: {e}")


if __name__ == '__main__':
    check_app_performance()
    benchmark_database()
