import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.production import ProductionConfig
from app import create_app
from app.extensions import db
from app.models import PromoCode, PromoCodeRedemption, LaunchMetric
from datetime import datetime, timedelta

def create_phase8_tables_and_data():
    """Create Phase 8 tables and initial data using production config."""
    
    print("🚀 Starting Phase 8 setup using production configuration...")
    
    # Initialize production config
    ProductionConfig.init_app()
    
    # Create app with production config
    app = create_app()
    app.config.from_object(ProductionConfig)
    
    # Add the additional config attributes
    for attr in dir(ProductionConfig):
        if attr.startswith('SQLALCHEMY_') and not attr.startswith('_'):
            setattr(app.config, attr, getattr(ProductionConfig, attr))
    
    print(f"🔌 Database: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1].split('/')[0] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'Unknown'}")
    
    with app.app_context():
        try:
            # Test database connection first
            result = db.engine.execute('SELECT 1').fetchone()
            print("✅ Database connection successful")
            
            # Create all tables (including Phase 8 tables)
            print("🔧 Creating database tables...")
            db.create_all()
            print("✅ All tables created/verified")
            
            # Create promo codes
            promo_codes_data = [
                {
                    'code': 'PRODUCTHUNT10',
                    'discount_type': 'credits',
                    'discount_value': 10,
                    'campaign': 'product_hunt',
                    'description': '10 free credits for Product Hunt users',
                    'expires_at': datetime.now() + timedelta(days=30)
                },
                {
                    'code': 'REDDIT20',
                    'discount_type': 'credits',
                    'discount_value': 20,
                    'campaign': 'reddit',
                    'description': '20 free credits for Reddit community',
                    'expires_at': datetime.now() + timedelta(days=30)
                },
                {
                    'code': 'LAUNCH50',
                    'discount_type': 'percentage',
                    'discount_value': 50,
                    'campaign': 'twitter',
                    'description': '50% off first purchase for early supporters',
                    'expires_at': datetime.now() + timedelta(days=7)
                },
                {
                    'code': 'EARLY100',
                    'discount_type': 'credits',
                    'discount_value': 100,
                    'campaign': 'early_supporters',
                    'description': '100 free credits for first 48 hours',
                    'expires_at': datetime.now() + timedelta(days=2)
                }
            ]
            
            print("🎫 Creating promo codes...")
            created_count = 0
            existing_count = 0
            
            for code_data in promo_codes_data:
                existing = PromoCode.query.filter_by(code=code_data['code']).first()
                if not existing:
                    promo_code = PromoCode(**code_data)
                    db.session.add(promo_code)
                    created_count += 1
                    print(f"   ✅ Created: {code_data['code']} ({code_data['campaign']})")
                else:
                    existing_count += 1
                    print(f"   ⚠️  Exists: {code_data['code']} ({existing.campaign})")
            
            # Create today's launch metrics
            today = datetime.now().date()
            existing_metric = LaunchMetric.query.filter_by(date=today).first()
            if not existing_metric:
                metric = LaunchMetric(date=today)
                db.session.add(metric)
                print(f"✅ Created launch metrics for {today}")
            else:
                print(f"⚠️  Launch metrics already exist for {today}")
            
            # Commit all changes
            db.session.commit()
            print("💾 All changes committed to database")
            
            # Verify and display results
            print("\n" + "="*60)
            print("🎉 PHASE 8 SETUP COMPLETE!")
            print("="*60)
            
            total_codes = PromoCode.query.count()
            active_codes = PromoCode.query.filter_by(is_active=True).count()
            total_metrics = LaunchMetric.query.count()
            
            print(f"📊 Database Statistics:")
            print(f"   • Total promo codes: {total_codes}")
            print(f"   • Active promo codes: {active_codes}")
            print(f"   • Launch metrics records: {total_metrics}")
            print(f"   • Created this session: {created_count}")
            print(f"   • Already existed: {existing_count}")
            
            print(f"\n🎫 Active Promo Codes:")
            for code in PromoCode.query.filter_by(is_active=True).all():
                status_icon = "🟢" if code.expires_at and code.expires_at > datetime.now() else "🔴"
                expiry = code.expires_at.strftime('%Y-%m-%d %H:%M') if code.expires_at else "Never"
                print(f"   {status_icon} {code.code:<15} | {code.discount_value:>3} {code.discount_type:<10} | {code.campaign:<15} | Until: {expiry}")
            
            print(f"\n🚀 Next Steps:")
            print(f"   1. Test promo checker: python check_promo_codes.py")
            print(f"   2. Start Flask server: python app.py")
            print(f"   3. Test promo URLs: /launch/promo/PRODUCTHUNT10")
            print(f"   4. Visit dashboard: /launch/dashboard")
            print(f"   5. Test registration: /launch/special/product-hunt")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Clean up SSH tunnel if running locally
            if not ProductionConfig.is_on_pythonanywhere() and ProductionConfig.server:
                print("🔌 Closing SSH tunnel...")
                ProductionConfig.stop_ssh_tunnel()

if __name__ == '__main__':
    success = create_phase8_tables_and_data()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("Phase 8 is now ready for launch! 🚀")
    else:
        print("\n❌ Setup failed. Please check the errors above.")