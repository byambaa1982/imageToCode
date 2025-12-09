#!/usr/bin/env python3
"""Debug SSH tunnel connection to PythonAnywhere."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from sshtunnel import SSHTunnelForwarder
    print("✓ sshtunnel package available")
except ImportError as e:
    print(f"✗ sshtunnel package not available: {e}")
    exit(1)

# SSH Configuration
SSH_HOST = 'ssh.pythonanywhere.com'
SSH_USERNAME = 'byambaa1982'
SSH_PASSWORD = os.environ.get('SSH_PASSWORD', 'Python@1982')
DB_HOST = 'byambaa1982.mysql.pythonanywhere-services.com'

print(f"SSH Host: {SSH_HOST}")
print(f"SSH Username: {SSH_USERNAME}")
print(f"SSH Password: {'*' * len(SSH_PASSWORD) if SSH_PASSWORD else 'NOT SET'}")
print(f"DB Host: {DB_HOST}")

try:
    print("\n🔄 Testing SSH connection...")
    
    # Create tunnel
    tunnel = SSHTunnelForwarder(
        (SSH_HOST, 22),
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSWORD,
        ssh_pkey=None,
        ssh_private_key_password=None,
        remote_bind_address=(DB_HOST, 3306),
        local_bind_address=('127.0.0.1', 0),  # Use any available port
        allow_agent=False,
        host_pkey_directories=[],
        set_keepalive=30.0
    )
    
    print("🔄 Starting tunnel...")
    tunnel.start()
    
    if tunnel.is_active:
        print(f"✓ SSH tunnel successful on port {tunnel.local_bind_port}")
        
        # Test MySQL connection through tunnel
        try:
            import pymysql
            print("🔄 Testing MySQL connection through tunnel...")
            
            conn = pymysql.connect(
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                user='byambaa1982',
                password=os.environ.get('DB_PASSWORD', 'Mysql@1982'),
                database='byambaa1982$codemirror',
                connect_timeout=10
            )
            print("✓ MySQL connection successful!")
            conn.close()
            
        except ImportError:
            print("⚠️  pymysql not available for connection test")
        except Exception as e:
            print(f"✗ MySQL connection failed: {e}")
            
        tunnel.stop()
        print("✓ Tunnel stopped")
        
    else:
        print("✗ SSH tunnel failed to become active")
        
except Exception as e:
    print(f"✗ SSH tunnel error: {e}")
    import traceback
    traceback.print_exc()
