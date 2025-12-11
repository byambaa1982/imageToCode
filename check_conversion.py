#!/usr/bin/env python3
"""
Simple conversion checker that works with SQLite database directly.
"""

import sqlite3
import os
from datetime import datetime

def check_conversion_in_sqlite():
    """Check the conversion directly in SQLite database."""
    conversion_uuid = "0c715064-ae41-4c41-a3c9-b5a0aab6af27"
    
    # Try to find the SQLite database
    db_paths = [
        "instance/screenshot_to_code.db",
        "screenshot_to_code.db",
        "app.db"
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ SQLite database not found")
        print("   Checked paths:", db_paths)
        return False
    
    print(f"✅ Found database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if conversions table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='conversions'
        """)
        
        if not cursor.fetchone():
            print("❌ Conversions table not found in database")
            return False
        
        # Find the specific conversion
        cursor.execute("""
            SELECT id, uuid, account_id, status, framework, original_filename,
                   generated_html, generated_css, generated_js, 
                   preview_url, download_url, error_message,
                   created_at, updated_at
            FROM conversions 
            WHERE uuid = ?
        """, (conversion_uuid,))
        
        row = cursor.fetchone()
        
        if not row:
            print(f"❌ Conversion {conversion_uuid} not found in database")
            
            # Show all conversions to help debug
            cursor.execute("SELECT uuid, status, framework, created_at FROM conversions ORDER BY created_at DESC LIMIT 5")
            recent = cursor.fetchall()
            
            if recent:
                print("\n📋 Recent conversions in database:")
                for r in recent:
                    print(f"   UUID: {r[0][:8]}... Status: {r[1]} Framework: {r[2]} Created: {r[3]}")
            else:
                print("\n❌ No conversions found in database")
            
            return False
        
        # Parse the row data
        (id, uuid, account_id, status, framework, filename, 
         html, css, js, preview_url, download_url, error_msg, 
         created_at, updated_at) = row
        
        print(f"\n🔍 Conversion Details:")
        print(f"   ID: {id}")
        print(f"   UUID: {uuid}")
        print(f"   Account ID: {account_id}")
        print(f"   Status: {status}")
        print(f"   Framework: {framework}")
        print(f"   Filename: {filename}")
        print(f"   Created: {created_at}")
        print(f"   Updated: {updated_at}")
        
        if error_msg:
            print(f"   ❌ Error: {error_msg}")
        
        print(f"\n📄 Generated Content:")
        html_len = len(html or "")
        css_len = len(css or "")
        js_len = len(js or "")
        
        print(f"   HTML: {'✅' if html_len > 0 else '❌'} ({html_len:,} characters)")
        print(f"   CSS:  {'✅' if css_len > 0 else '❌'} ({css_len:,} characters)")
        print(f"   JS:   {'✅' if js_len > 0 else '❌'} ({js_len:,} characters)")
        
        if html_len > 0:
            print(f"\n📖 HTML Preview (first 200 chars):")
            print(f"   {html[:200]}...")
        
        print(f"\n🔗 File URLs:")
        print(f"   Preview URL: {preview_url or 'None'}")
        print(f"   Download URL: {download_url or 'None'}")
        
        # Check file existence
        if preview_url and os.path.exists(preview_url):
            print(f"   ✅ Preview file exists")
        elif preview_url:
            print(f"   ❌ Preview file missing")
        
        if download_url and os.path.exists(download_url):
            print(f"   ✅ Download file exists")
        elif download_url:
            print(f"   ❌ Download file missing")
        
        # Diagnosis
        print(f"\n🔧 DIAGNOSIS:")
        
        if status != 'completed':
            print(f"   ⚠️  Status: '{status}' (not completed)")
            if status == 'failed':
                print("   💡 Recommendation: Retry the conversion")
            elif status in ['pending', 'processing']:
                print("   💡 Recommendation: Wait for processing to complete")
        elif html_len == 0:
            print("   ❌ CRITICAL: Status 'completed' but no generated HTML")
            print("   💡 This is why preview shows 'Preview Not Available'")
            print("   💡 The AI service completed but failed to save the generated content")
        else:
            print("   ✅ Conversion looks healthy!")
            print("   💡 Preview should work (after login)")
            
        # Solution
        print(f"\n💡 SOLUTION:")
        if status == 'completed' and html_len == 0:
            print("   1. The conversion needs to be retried")
            print("   2. Use the retry button in the web interface")
            print(f"   3. Or access: /converter/retry/{conversion_uuid}")
        elif status == 'completed' and html_len > 0:
            print("   1. Login to your account")
            print(f"   2. Access: /converter/preview/{conversion_uuid}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 SQLite Conversion Checker")
    print("=" * 50)
    check_conversion_in_sqlite()
