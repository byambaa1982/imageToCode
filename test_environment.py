#!/usr/bin/env python3
"""Simple test runner to validate our test environment."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from app.extensions import db
    from app.models import Account
    print("✅ App imports successful")
    
    # Test app creation
    app = create_app('testing')
    print("✅ Test app creation successful")
    
    with app.app_context():
        db.create_all()
        print("✅ Database creation successful")
    
    # Test converter imports
    from app.converter.ai_service import AIService
    from app.converter.utils import validate_image_file
    print("✅ Converter imports successful")
    
    print("\n🎉 All imports and basic setup are working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
