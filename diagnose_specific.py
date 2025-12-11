#!/usr/bin/env python3
"""
Diagnose specific conversion UUID and fix preview issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def diagnose_specific_conversion():
    """Diagnose the specific conversion UUID provided by the user."""
    conversion_uuid = "0c715064-ae41-4c41-a3c9-b5a0aab6af27"
    
    try:
        from app import create_app
        from app.models import Conversion, Account
        from app.extensions import db
        from datetime import datetime, timedelta
        
        # Try to use the current app configuration
        app = create_app()
        
        with app.app_context():
            print(f"🔍 Diagnosing Conversion: {conversion_uuid}")
            print("=" * 60)
            
            # Find the conversion
            conversion = Conversion.query.filter_by(uuid=conversion_uuid).first()
            
            if not conversion:
                print(f"❌ Conversion {conversion_uuid} not found in database")
                return False
            
            # Display conversion details
            print(f"✅ Conversion found!")
            print(f"   ID: {conversion.id}")
            print(f"   Account ID: {conversion.account_id}")
            print(f"   Status: {conversion.status}")
            print(f"   Framework: {conversion.framework}")
            print(f"   Original Filename: {conversion.original_filename}")
            print(f"   Created: {conversion.created_at}")
            print(f"   Updated: {conversion.updated_at}")
            print()
            
            # Check account details
            account = Account.query.get(conversion.account_id)
            if account:
                print(f"👤 Account Details:")
                print(f"   Email: {account.email}")
                print(f"   Name: {account.first_name} {account.last_name}")
                print(f"   Credits: {account.credits_remaining}")
                print()
            
            # Check generated content
            print("📄 Generated Content Analysis:")
            html_len = len(conversion.generated_html or "")
            css_len = len(conversion.generated_css or "")
            js_len = len(conversion.generated_js or "")
            
            print(f"   HTML: {'✅' if html_len > 0 else '❌'} ({html_len:,} characters)")
            print(f"   CSS:  {'✅' if css_len > 0 else '❌'} ({css_len:,} characters)")  
            print(f"   JS:   {'✅' if js_len > 0 else '❌'} ({js_len:,} characters)")
            
            if html_len > 0:
                print(f"   HTML Preview: {conversion.generated_html[:100]}...")
            if css_len > 0:
                print(f"   CSS Preview: {conversion.generated_css[:100]}...")
                
            print()
            
            # Check URLs and files
            print("🔗 URLs and File Status:")
            print(f"   Original Image: {conversion.original_image_url}")
            print(f"   Preview URL: {conversion.preview_url or 'None'}")
            print(f"   Download URL: {conversion.download_url or 'None'}")
            
            if conversion.preview_url:
                if os.path.exists(conversion.preview_url):
                    print(f"   ✅ Preview file exists")
                    file_size = os.path.getsize(conversion.preview_url)
                    print(f"   📊 File size: {file_size:,} bytes")
                else:
                    print(f"   ❌ Preview file missing: {conversion.preview_url}")
            
            if conversion.download_url:
                if os.path.exists(conversion.download_url):
                    print(f"   ✅ Download file exists")
                else:
                    print(f"   ❌ Download file missing: {conversion.download_url}")
                    
            print()
            
            # Check for errors
            if conversion.error_message:
                print(f"❌ Error Message: {conversion.error_message}")
                print()
            
            # Processing information
            if conversion.processing_time:
                print(f"⏱️  Processing Time: {conversion.processing_time} seconds")
            if conversion.tokens_used:
                print(f"🔢 Tokens Used: {conversion.tokens_used:,}")
            if conversion.cost:
                print(f"💰 Cost: ${conversion.cost}")
            
            print()
            
            # Diagnosis and recommendations
            print("🔧 DIAGNOSIS:")
            
            if conversion.status != 'completed':
                print(f"   ⚠️  Status is '{conversion.status}', not 'completed'")
                if conversion.status == 'failed':
                    print("   💡 Recommendation: Retry the conversion")
                elif conversion.status in ['pending', 'processing']:
                    print("   💡 Recommendation: Wait for processing to complete")
            
            elif html_len == 0:
                print("   ❌ CRITICAL ISSUE: Status is 'completed' but no generated HTML")
                print("   💡 This suggests the AI service completed but failed to save results")
                print("   💡 Recommendation: Retry the conversion or check logs")
            
            elif conversion.preview_url and not os.path.exists(conversion.preview_url):
                print("   ⚠️  Generated content exists but preview file is missing")
                print("   💡 Recommendation: Preview will be generated on-the-fly")
            
            else:
                print("   ✅ Conversion appears to be healthy!")
                print(f"   💡 Preview should work at: /converter/preview/{conversion_uuid}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_conversion_if_needed():
    """Fix the conversion by regenerating preview if needed."""
    conversion_uuid = "0c715064-ae41-4c41-a3c9-b5a0aab6af27"
    
    try:
        from app import create_app
        from app.models import Conversion
        from app.extensions import db
        from app.converter.utils import generate_preview_html
        import os
        
        app = create_app()
        
        with app.app_context():
            conversion = Conversion.query.filter_by(uuid=conversion_uuid).first()
            
            if not conversion:
                print("❌ Conversion not found")
                return False
            
            if conversion.status == 'completed' and conversion.generated_html:
                print("🔧 Attempting to fix preview...")
                
                # Generate preview HTML
                try:
                    preview_html = generate_preview_html(
                        conversion.generated_html or '',
                        conversion.generated_css or '',
                        conversion.generated_js or ''
                    )
                    
                    # Create preview file path
                    upload_dir = os.path.dirname(app.config.get('UPLOAD_FOLDER', 'uploads'))
                    preview_filename = f"{conversion_uuid}_preview.html"
                    preview_path = os.path.join(upload_dir, 'previews', preview_filename)
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(preview_path), exist_ok=True)
                    
                    # Write preview file
                    with open(preview_path, 'w', encoding='utf-8') as f:
                        f.write(preview_html)
                    
                    # Update conversion
                    conversion.preview_url = preview_path
                    db.session.commit()
                    
                    print(f"✅ Preview file created: {preview_path}")
                    print(f"🌐 Preview URL updated in database")
                    print(f"🎯 Test preview at: /converter/preview/{conversion_uuid}")
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ Failed to create preview: {e}")
                    return False
            
            else:
                print("❌ Cannot fix: Conversion not completed or missing generated content")
                return False
                
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Conversion Diagnostic Tool")
    print("=" * 60)
    
    success = diagnose_specific_conversion()
    
    if success:
        print("\n" + "=" * 60)
        fix_response = input("Would you like to attempt to fix the preview? (y/N): ")
        
        if fix_response.lower() in ['y', 'yes']:
            print("\n🔧 Attempting to fix...")
            fix_conversion_if_needed()
    
    print("\n✅ Diagnostic complete!")
