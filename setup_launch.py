#!/usr/bin/env python3
"""
Launch setup script for Phase 8 deployment.
Quick setup of promo codes and launch metrics.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.launch.utils import create_launch_promo_codes
from app.models import LaunchMetric
from datetime import date

def setup_launch():
    """Set up launch week infrastructure."""
    app = create_app()
    
    with app.app_context():
        print("🚀 Setting up Phase 8 Launch Infrastructure")
        print("=" * 50)
        
        try:
            # Create database tables if they don't exist
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Database tables ready")
            
            # Create launch promo codes
            print("\n🎟️  Creating launch promo codes...")
            promo_codes = create_launch_promo_codes()
            
            if promo_codes:
                print(f"✅ Created {len(promo_codes)} promo codes:")
                for promo in promo_codes:
                    print(f"   - {promo.code}: {promo.discount_value} {promo.discount_type} ({promo.campaign})")
            else:
                print("✅ Promo codes already exist")
            
            # Initialize today's metrics
            print("\n📈 Initializing launch metrics...")
            today = date.today()
            existing_metrics = LaunchMetric.query.filter_by(date=today).first()
            
            if not existing_metrics:
                metrics = LaunchMetric(date=today)
                db.session.add(metrics)
                print(f"✅ Created metrics tracking for {today}")
            else:
                print(f"✅ Metrics already initialized for {today}")
            
            db.session.commit()
            
            print("\n🎉 Launch setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Start your Flask application")
            print("2. Visit /launch/dashboard (admin required)")
            print("3. Share campaign URLs:")
            print("   - Product Hunt: /launch/special/product-hunt")
            print("   - Reddit: /launch/special/reddit")
            print("   - Direct promo: /launch/promo/PRODUCTHUNT10")
            print("\n🚀 Ready for launch!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during setup: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    setup_launch()
