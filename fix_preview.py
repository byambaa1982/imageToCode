#!/usr/bin/env python3
"""
Fix conversion preview by creating test data with local SQLite.
"""

import os
import sys

# Force local SQLite database
os.environ['FLASK_ENV'] = 'testing'
os.environ['TESTING'] = 'True'

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import Account, Conversion
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import uuid

def setup_test_data():
    """Create test account and conversion with generated content."""
    
    app = create_app('testing')  # Use testing config with SQLite
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create test account if it doesn't exist
        test_account = Account.query.filter_by(email='test@example.com').first()
        if not test_account:
            test_account = Account(
                email='test@example.com',
                password=generate_password_hash('testpassword'),
                first_name='Test',
                last_name='User',
                credits_remaining=10.0,
                is_verified=True
            )
            db.session.add(test_account)
            db.session.commit()
            print(f"✅ Created test account: {test_account.id}")
        else:
            print(f"✅ Using existing test account: {test_account.id}")
        
        # Create test conversion with generated content
        test_uuid = str(uuid.uuid4())
        conversion = Conversion(
            uuid=test_uuid,
            account_id=test_account.id,
            original_image_url='/tmp/test-image.png',
            original_filename='test-image.png',
            framework='html',
            status='completed',
            generated_html='''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Generated Page</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f8ff; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header { color: #2c3e50; text-align: center; margin-bottom: 20px; }
        .content { line-height: 1.6; color: #34495e; }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; margin: 10px; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
        .feature-box { background: #ecf0f1; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Preview Working!</h1>
            <p>This is a test conversion with generated HTML content</p>
        </div>
        
        <div class="content">
            <div class="feature-box">
                <h3>✅ Success!</h3>
                <p>If you can see this page, the preview functionality is working correctly.</p>
            </div>
            
            <div class="feature-box">
                <h3>🔧 Technical Details</h3>
                <p><strong>Conversion UUID:</strong> ''' + test_uuid + '''</p>
                <p><strong>Status:</strong> completed</p>
                <p><strong>Framework:</strong> HTML</p>
                <p><strong>Generated:</strong> ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
            </div>
            
            <button class="btn" onclick="testJS()">Test JavaScript</button>
            <button class="btn" onclick="alert('CSS animations and JavaScript are working!')">Click Me!</button>
        </div>
    </div>
    
    <script>
        console.log('✅ JavaScript loaded successfully!');
        
        function testJS() {
            alert('🎯 JavaScript is working perfectly!\\n\\nThis confirms that:\\n• HTML is rendering\\n• CSS is styling\\n• JavaScript is executing');
        }
        
        // Add some dynamic behavior
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 Page loaded and JavaScript initialized');
        });
    </script>
</body>
</html>''',
            generated_css='''/* Additional CSS styles */
.btn:active {
    transform: translateY(0);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.container {
    animation: fadeIn 0.6s ease-out;
}''',
            generated_js='''// Additional JavaScript
console.log('🎨 CSS and JavaScript files loaded separately');

// Add interactive features
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.02)';
        });
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-2px) scale(1)';
        });
    });
});''',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(conversion)
        db.session.commit()
        
        print(f"✅ Created test conversion: {test_uuid}")
        print(f"📱 Test the preview at: http://localhost:5000/converter/preview/{test_uuid}")
        print(f"🔑 Login with: test@example.com / testpassword")
        print()
        print("Next steps:")
        print("1. Start the Flask development server: python app.py")
        print("2. Login with the test credentials")
        print(f"3. Navigate to: /converter/preview/{test_uuid}")
        
        return test_uuid, test_account

if __name__ == "__main__":
    setup_test_data()
