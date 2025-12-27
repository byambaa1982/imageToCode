#!/usr/bin/env python3
"""
Quick Promo Code Checker for Phase 8
Run this to see all promo codes and their status
"""

import sys
import os
sys.path.insert(0, '/Users/zoloo/project_v2/imageToCode')

def check_promo_codes():
    try:
        from app import create_app
        from app.models import PromoCode, PromoCodeRedemption
        from app.extensions import db
        from datetime import datetime
        
        app = create_app()
        with app.app_context():
            print("🎫 PROMO CODE STATUS CHECK")
            print("=" * 60)
            
            # Check if any promo codes exist
            codes = PromoCode.query.all()
            
            if not codes:
                print("❌ NO PROMO CODES FOUND!")
                print("\n💡 To create promo codes:")
                print("   1. Login as admin")
                print("   2. Visit: http://localhost:5000/launch/setup")
                print("   3. Or run: create_launch_promo_codes()")
                return False
            
            print(f"📊 Found {len(codes)} promo codes:")
            print()
            
            all_valid = True
            
            for i, code in enumerate(codes, 1):
                print(f"{i}. 🎫 {code.code}")
                print(f"   📂 Campaign: {code.campaign}")
                print(f"   🎁 Type: {code.discount_type}")
                print(f"   💰 Value: {code.discount_value}")
                print(f"   📈 Usage: {code.uses_count}/{code.max_uses or '∞'}")
                
                # Check if active
                if code.is_active:
                    print(f"   🟢 Status: ACTIVE")
                else:
                    print(f"   🔴 Status: INACTIVE")
                    all_valid = False
                
                # Check expiry
                if code.expires_at:
                    now = datetime.utcnow()
                    if now > code.expires_at:
                        print(f"   ⏰ Expires: {code.expires_at} (EXPIRED)")
                        all_valid = False
                    else:
                        print(f"   ⏰ Expires: {code.expires_at} (Valid)")
                else:
                    print(f"   ⏰ Expires: Never")
                
                # Test validation
                is_valid, error_msg = code.is_valid()
                if is_valid:
                    print(f"   ✅ Validation: PASSED")
                else:
                    print(f"   ❌ Validation: FAILED - {error_msg}")
                    all_valid = False
                
                # Test discount calculation
                if code.discount_type == 'credits':
                    credits = code.apply_discount(0)
                    print(f"   🎁 Will give: {credits} free credits")
                elif code.discount_type == 'percentage':
                    test_amount = 100
                    discounted = code.apply_discount(test_amount)
                    savings = test_amount - discounted
                    print(f"   💸 Discount: {savings}% off (${test_amount} → ${discounted})")
                elif code.discount_type == 'fixed':
                    test_amount = 100
                    discounted = code.apply_discount(test_amount)
                    savings = test_amount - discounted
                    print(f"   💸 Discount: ${savings} off (${test_amount} → ${discounted})")
                
                print()
            
            # Check redemptions
            total_redemptions = PromoCodeRedemption.query.count()
            print(f"📊 Total Redemptions: {total_redemptions}")
            
            if total_redemptions > 0:
                recent_redemptions = PromoCodeRedemption.query.order_by(
                    PromoCodeRedemption.redeemed_at.desc()
                ).limit(5).all()
                
                print("\n🕐 Recent Redemptions:")
                for redemption in recent_redemptions:
                    print(f"   - {redemption.promo_code.code} by user {redemption.account_id} at {redemption.redeemed_at}")
            
            print("\n" + "=" * 60)
            
            if all_valid:
                print("🎉 ALL PROMO CODES ARE WORKING CORRECTLY!")
                print("✅ Ready for launch campaigns")
            else:
                print("⚠️  SOME PROMO CODES HAVE ISSUES")
                print("❌ Please fix issues before launch")
            
            # Show test URLs
            print("\n🔗 Test URLs:")
            for code in codes:
                print(f"   http://localhost:5000/launch/promo/{code.code}")
            
            return all_valid
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you're in the correct directory and Flask app is set up")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_promo_urls():
    """Test if promo URLs are accessible"""
    try:
        import requests
        
        print("\n🌐 Testing Promo URLs...")
        
        base_url = "http://localhost:5000"
        test_codes = ['PRODUCTHUNT10', 'REDDIT20', 'LAUNCH50', 'EARLY100']
        
        for code in test_codes:
            url = f"{base_url}/launch/promo/{code}"
            try:
                response = requests.get(url, allow_redirects=False, timeout=5)
                if response.status_code in [200, 302]:
                    print(f"   ✅ {code}: {response.status_code}")
                else:
                    print(f"   ❌ {code}: {response.status_code}")
            except requests.RequestException:
                print(f"   ⚠️  {code}: Server not running")
                
    except ImportError:
        print("   ℹ️  Install 'requests' to test URLs: pip install requests")

if __name__ == '__main__':
    print("🚀 Phase 8 Promo Code Checker")
    print("Checking promo codes in your Screenshot to Code app...\n")
    
    success = check_promo_codes()
    test_promo_urls()
    
    print("\n📋 Quick Actions:")
    print("- Create codes: Visit /launch/setup as admin")
    print("- View dashboard: Visit /launch/dashboard as admin") 
    print("- Test Product Hunt: Visit /launch/special/product-hunt")
    print("- Test Reddit: Visit /launch/special/reddit")
    
    if success:
        print("\n🎉 Promo codes are ready for launch! 🚀")
    else:
        print("\n⚠️  Please fix issues before launching")
    
    sys.exit(0 if success else 1)
