#!/usr/bin/env python3
"""
Diagnostic tool to check conversion data and fix preview issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Conversion
from app.extensions import db

def diagnose_conversion(conversion_uuid):
    """Diagnose a specific conversion."""
    app = create_app('development')  # Use local SQLite for now
    
    with app.app_context():
        conversion = Conversion.query.filter_by(uuid=conversion_uuid).first()
        
        if not conversion:
            print(f"❌ Conversion {conversion_uuid} not found")
            return
            
        print(f"🔍 Conversion {conversion_uuid} Details:")
        print(f"   Status: {conversion.status}")
        print(f"   Framework: {conversion.framework}")
        print(f"   Created: {conversion.created_at}")
        print(f"   Updated: {conversion.updated_at}")
        print(f"   Account ID: {conversion.account_id}")
        print()
        
        print("📄 Generated Content:")
        html_len = len(conversion.generated_html or "")
        css_len = len(conversion.generated_css or "")
        js_len = len(conversion.generated_js or "")
        
        print(f"   HTML: {'✅' if html_len > 0 else '❌'} ({html_len} characters)")
        print(f"   CSS:  {'✅' if css_len > 0 else '❌'} ({css_len} characters)")
        print(f"   JS:   {'✅' if js_len > 0 else '❌'} ({js_len} characters)")
        print()
        
        print("🔗 URLs:")
        print(f"   Preview URL: {conversion.preview_url or 'None'}")
        print(f"   Download URL: {conversion.download_url or 'None'}")
        print()
        
        if conversion.error_message:
            print(f"❌ Error Message: {conversion.error_message}")
            print()
            
        # Check if files exist
        if conversion.preview_url and os.path.exists(conversion.preview_url):
            print("✅ Preview file exists")
        else:
            print("❌ Preview file missing or path invalid")
            
        if conversion.download_url and os.path.exists(conversion.download_url):
            print("✅ Download file exists")
        else:
            print("❌ Download file missing or path invalid")
            
        # Suggest fix
        if conversion.status == 'completed' and html_len == 0:
            print("\n🔧 ISSUE DETECTED:")
            print("   Conversion is marked as completed but has no generated HTML.")
            print("   This suggests the AI service completed but failed to save results.")
            print("   You may want to retry this conversion.")

def create_sample_conversion():
    """Create a sample conversion with generated content for testing."""
    app = create_app('development')
    
    with app.app_context():
        # Create a sample conversion
        conversion = Conversion(
            account_id=1,  # Assuming user ID 1 exists
            original_image_url='/tmp/sample.png',
            original_filename='sample.png',
            framework='html',
            status='completed',
            generated_html='''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample Generated Page</title>
</head>
<body>
    <div class="container">
        <h1>Sample Generated HTML</h1>
        <p>This is a sample conversion for testing preview functionality.</p>
        <button onclick="alert('Hello from generated JS!')">Click me</button>
    </div>
</body>
</html>''',
            generated_css='''body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
}''',
            generated_js='''console.log("Sample generated JavaScript loaded!");'''
        )
        
        db.session.add(conversion)
        db.session.commit()
        
        print(f"✅ Created sample conversion: {conversion.uuid}")
        print(f"   You can test preview at: /converter/preview/{conversion.uuid}")
        return conversion.uuid

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "create-sample":
            create_sample_conversion()
        else:
            conversion_uuid = sys.argv[1]
            diagnose_conversion(conversion_uuid)
    else:
        print("Usage:")
        print("  python diagnose_conversion.py <conversion_uuid>  # Diagnose specific conversion")
        print("  python diagnose_conversion.py create-sample     # Create sample conversion")
