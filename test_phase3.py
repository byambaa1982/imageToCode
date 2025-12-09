"""
Test script for Phase 3 - Credit System & Payment Integration
Run this to verify all Phase 3 components are working correctly.
"""

import sys
from app import create_app
from app.extensions import db
from app.models import Account, Package, Order, CreditsTransaction


def test_phase3():
    """Test Phase 3 implementation."""
    app = create_app()
    
    print("=" * 80)
    print("PHASE 3 IMPLEMENTATION TEST")
    print("=" * 80)
    print()
    
    with app.app_context():
        results = []
        
        # Test 1: Check packages table
        print("📦 Test 1: Packages Table")
        try:
            packages = Package.query.all()
            if len(packages) >= 3:
                print(f"   ✅ PASS: Found {len(packages)} packages")
                for pkg in packages:
                    print(f"      - {pkg.name}: ${pkg.price} for {int(pkg.credits)} credits")
                results.append(True)
            else:
                print(f"   ❌ FAIL: Only found {len(packages)} packages (expected 3+)")
                print("      Run: python seed_packages.py")
                results.append(False)
        except Exception as e:
            print(f"   ❌ FAIL: Error querying packages: {str(e)}")
            results.append(False)
        print()
        
        # Test 2: Check Account model has credit methods
        print("👤 Test 2: Account Credit Methods")
        try:
            test_account = Account.query.first()
            if test_account:
                has_credits_method = hasattr(test_account, 'has_credits')
                deduct_method = hasattr(test_account, 'deduct_credits')
                add_method = hasattr(test_account, 'add_credits')
                
                if has_credits_method and deduct_method and add_method:
                    print(f"   ✅ PASS: Account has all credit methods")
                    print(f"      - has_credits(): {has_credits_method}")
                    print(f"      - deduct_credits(): {deduct_method}")
                    print(f"      - add_credits(): {add_method}")
                    print(f"      Test account balance: {test_account.credits_remaining}")
                    results.append(True)
                else:
                    print(f"   ❌ FAIL: Missing credit methods")
                    results.append(False)
            else:
                print("   ⚠️  SKIP: No accounts in database to test")
                results.append(True)  # Not a failure
        except Exception as e:
            print(f"   ❌ FAIL: Error checking Account methods: {str(e)}")
            results.append(False)
        print()
        
        # Test 3: Check database tables exist
        print("🗄️  Test 3: Database Tables")
        try:
            tables_to_check = ['packages', 'orders', 'credits_transactions']
            all_exist = True
            
            for table in tables_to_check:
                # Try to query each table
                try:
                    if table == 'packages':
                        Package.query.first()
                    elif table == 'orders':
                        Order.query.first()
                    elif table == 'credits_transactions':
                        CreditsTransaction.query.first()
                    print(f"   ✅ Table '{table}' exists and is queryable")
                except Exception as e:
                    print(f"   ❌ Table '{table}' error: {str(e)}")
                    all_exist = False
            
            results.append(all_exist)
        except Exception as e:
            print(f"   ❌ FAIL: Error checking tables: {str(e)}")
            results.append(False)
        print()
        
        # Test 4: Check payment routes exist
        print("🌐 Test 4: Payment Routes")
        try:
            from app.payment import payment as payment_bp
            
            payment_routes = []
            for rule in app.url_map.iter_rules():
                if 'payment' in rule.endpoint:
                    payment_routes.append(str(rule))
            
            expected_routes = ['pricing', 'checkout', 'success', 'cancel', 'webhook', 'history']
            
            if len(payment_routes) >= 5:
                print(f"   ✅ PASS: Found {len(payment_routes)} payment routes")
                for route in payment_routes[:6]:  # Show first 6
                    print(f"      - {route}")
                results.append(True)
            else:
                print(f"   ❌ FAIL: Only found {len(payment_routes)} payment routes")
                results.append(False)
        except Exception as e:
            print(f"   ❌ FAIL: Error checking routes: {str(e)}")
            results.append(False)
        print()
        
        # Test 5: Check Stripe utils exist
        print("💳 Test 5: Stripe Integration")
        try:
            from app.payment.stripe_utils import (
                create_checkout_session,
                handle_checkout_completed,
                verify_webhook_signature,
                process_refund
            )
            print("   ✅ PASS: All Stripe utility functions exist")
            print("      - create_checkout_session()")
            print("      - handle_checkout_completed()")
            print("      - verify_webhook_signature()")
            print("      - process_refund()")
            results.append(True)
        except ImportError as e:
            print(f"   ❌ FAIL: Missing Stripe utilities: {str(e)}")
            results.append(False)
        print()
        
        # Test 6: Check configuration
        print("⚙️  Test 6: Configuration")
        try:
            stripe_public = app.config.get('STRIPE_PUBLIC_KEY')
            stripe_secret = app.config.get('STRIPE_SECRET_KEY')
            stripe_webhook = app.config.get('STRIPE_WEBHOOK_SECRET')
            
            config_ok = True
            if not stripe_public:
                print("   ⚠️  WARNING: STRIPE_PUBLIC_KEY not set in config")
                config_ok = False
            else:
                print(f"   ✅ STRIPE_PUBLIC_KEY configured")
                
            if not stripe_secret:
                print("   ⚠️  WARNING: STRIPE_SECRET_KEY not set in config")
                config_ok = False
            else:
                print(f"   ✅ STRIPE_SECRET_KEY configured")
                
            if not stripe_webhook:
                print("   ⚠️  WARNING: STRIPE_WEBHOOK_SECRET not set (optional for dev)")
            else:
                print(f"   ✅ STRIPE_WEBHOOK_SECRET configured")
            
            results.append(config_ok)
        except Exception as e:
            print(f"   ❌ FAIL: Error checking config: {str(e)}")
            results.append(False)
        print()
        
        # Test 7: Check templates exist
        print("📄 Test 7: Payment Templates")
        try:
            import os
            template_dir = os.path.join(app.root_path, 'templates', 'payment')
            
            if os.path.exists(template_dir):
                templates = os.listdir(template_dir)
                expected = ['success.html', 'cancel.html', 'history.html']
                
                all_exist = all(t in templates for t in expected)
                
                if all_exist:
                    print(f"   ✅ PASS: All payment templates exist")
                    for tmpl in templates:
                        print(f"      - {tmpl}")
                    results.append(True)
                else:
                    print(f"   ❌ FAIL: Missing templates")
                    print(f"      Found: {templates}")
                    print(f"      Expected: {expected}")
                    results.append(False)
            else:
                print(f"   ❌ FAIL: Payment template directory doesn't exist")
                results.append(False)
        except Exception as e:
            print(f"   ❌ FAIL: Error checking templates: {str(e)}")
            results.append(False)
        print()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        passed = sum(results)
        total = len(results)
        percentage = (passed / total) * 100 if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total} ({percentage:.1f}%)")
        print()
        
        if passed == total:
            print("🎉 SUCCESS! All Phase 3 tests passed!")
            print()
            print("Next Steps:")
            print("1. Set up Stripe API keys in .env file")
            print("2. Run: python seed_packages.py")
            print("3. Start the application and test payment flow")
            print("4. Use test card: 4242 4242 4242 4242")
            return 0
        else:
            print("⚠️  Some tests failed. Please review the errors above.")
            print()
            print("Common fixes:")
            print("- Run database migrations: flask db upgrade")
            print("- Seed packages: python seed_packages.py")
            print("- Install stripe: pip install stripe")
            print("- Check .env configuration")
            return 1


if __name__ == '__main__':
    try:
        exit_code = test_phase3()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Fatal error running tests: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
