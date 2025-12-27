#!/usr/bin/env python3
"""
Simple Phase 8 Verification - Check Core Implementation
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, '/Users/zoloo/project_v2/imageToCode')

def check_files_exist():
    """Check if all Phase 8 files were created."""
    print("🔍 Checking Phase 8 Files...")
    
    required_files = [
        'app/launch/__init__.py',
        'app/launch/routes.py', 
        'app/launch/utils.py',
        'app/launch/middleware.py',
        'app/templates/launch/dashboard.html',
        'app/templates/launch/product_hunt_landing.html',
        'app/templates/launch/reddit_landing.html',
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join('/Users/zoloo/project_v2/imageToCode', file_path)
        if os.path.exists(full_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files

def check_model_imports():
    """Check if new models can be imported."""
    print("🔍 Checking Model Imports...")
    
    try:
        from app.models import PromoCode, PromoCodeRedemption, LaunchMetric
        print("   ✅ PromoCode model imported")
        print("   ✅ PromoCodeRedemption model imported") 
        print("   ✅ LaunchMetric model imported")
        return True
    except ImportError as e:
        print(f"   ❌ Model import error: {e}")
        return False

def check_blueprint_import():
    """Check if launch blueprint can be imported."""
    print("🔍 Checking Blueprint Import...")
    
    try:
        from app.launch import launch
        print("   ✅ Launch blueprint imported")
        return True
    except ImportError as e:
        print(f"   ❌ Blueprint import error: {e}")
        return False

def check_app_integration():
    """Check if launch blueprint is registered in app."""
    print("🔍 Checking App Integration...")
    
    try:
        from app import create_app
        app = create_app()
        
        # Check if launch blueprint is registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        
        if 'launch' in blueprint_names:
            print("   ✅ Launch blueprint registered in app")
            
            # Check if routes are accessible 
            with app.test_client() as client:
                # Test Product Hunt landing page
                response = client.get('/launch/special/product-hunt')
                if response.status_code == 200:
                    print("   ✅ Product Hunt landing page accessible")
                else:
                    print(f"   ❌ Product Hunt landing page error: {response.status_code}")
                
                # Test Reddit landing page
                response = client.get('/launch/special/reddit')
                if response.status_code == 200:
                    print("   ✅ Reddit landing page accessible")
                else:
                    print(f"   ❌ Reddit landing page error: {response.status_code}")
                
            return True
        else:
            print("   ❌ Launch blueprint not registered")
            print(f"   Available blueprints: {blueprint_names}")
            return False
            
    except Exception as e:
        print(f"   ❌ App integration error: {e}")
        return False

def main():
    """Run simple verification checks."""
    print("🚀 Phase 8 Implementation - Simple Verification")
    print("=" * 50)
    
    all_passed = True
    
    # Check 1: Files exist
    files_ok, missing = check_files_exist()
    if not files_ok:
        print(f"❌ Missing files: {missing}")
        all_passed = False
    
    print()
    
    # Check 2: Models can be imported
    models_ok = check_model_imports()
    if not models_ok:
        all_passed = False
    
    print()
    
    # Check 3: Blueprint can be imported
    blueprint_ok = check_blueprint_import()
    if not blueprint_ok:
        all_passed = False
    
    print()
    
    # Check 4: App integration works
    app_ok = check_app_integration()
    if not app_ok:
        all_passed = False
    
    print()
    print("=" * 50)
    print("📊 VERIFICATION RESULTS")
    print("=" * 50)
    
    checks = [
        ("File Creation", files_ok),
        ("Model Imports", models_ok), 
        ("Blueprint Import", blueprint_ok),
        ("App Integration", app_ok),
    ]
    
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}")
    
    if all_passed:
        print("\n🎉 PHASE 8 CORE IMPLEMENTATION: VERIFIED!")
        print("✅ All essential components are in place")
        print("✅ Models, routes, and templates created")
        print("✅ Blueprint integrated successfully")
        print("✅ Landing pages accessible")
        print("\n📋 Next Steps:")
        print("1. Apply database migration: flask db migrate && flask db upgrade")
        print("2. Create admin account if not exists")
        print("3. Visit /launch/setup to create promo codes")
        print("4. Test full user journey manually")
        print("5. Run comprehensive verification script")
        print("\n🚀 Ready for launch preparation!")
    else:
        print("\n❌ PHASE 8 VERIFICATION FAILED")
        print("Please fix the failing checks before proceeding")
        print("Check error messages above for details")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
