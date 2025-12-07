#!/usr/bin/env python3
"""
Quick script to verify email for development/testing
Usage: python verify_email.py your-email@example.com
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app
from app.extensions import db
from app.models import Account

def verify_email(email):
    """Verify email for a user account."""
    app = create_app()
    
    with app.app_context():
        user = Account.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ No user found with email: {email}")
            return False
        
        if user.email_verified:
            print(f"✅ Email already verified for: {email}")
            return True
        
        user.email_verified = True
        db.session.commit()
        
        print(f"✅ Email verified successfully for: {email}")
        print(f"   User ID: {user.id}")
        print(f"   Credits: {user.credits_remaining}")
        return True

def list_users():
    """List all users in the database."""
    app = create_app()
    
    with app.app_context():
        users = Account.query.all()
        
        if not users:
            print("❌ No users found in database")
            return
        
        print("📋 Users in database:")
        print("-" * 60)
        for user in users:
            verified_status = "✅" if user.email_verified else "❌"
            print(f"{verified_status} {user.email} (ID: {user.id}, Credits: {user.credits_remaining})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python verify_email.py your-email@example.com  # Verify specific email")
        print("  python verify_email.py --list                  # List all users")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        list_users()
    else:
        email = sys.argv[1]
        verify_email(email)
