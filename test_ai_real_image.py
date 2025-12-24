#!/usr/bin/env python3
"""
Test script to check if uploaded images are being used in AI conversion.
"""

import sys
import os
import tempfile
from PIL import Image

# Add the project root to the Python path
sys.path.insert(0, '/Users/zoloo/project_v2/imageToCode')

from app import create_app
from app.converter.ai_service import AIService
from app.converter.utils import save_uploaded_file

def create_test_image():
    """Create a simple test image with text."""
    # Create a simple image with text
    img = Image.new('RGB', (800, 600), color='white')
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name, 'PNG')
    return temp_file.name

def test_ai_service_with_real_image():
    """Test if AI service actually processes the uploaded image."""
    app = create_app()
    
    with app.app_context():
        # Create test image
        test_image_path = create_test_image()
        print(f"Created test image: {test_image_path}")
        
        # Initialize AI service
        ai_service = AIService()
        
        # Test image processing
        print("\n=== Testing Image Processing ===")
        processed_image = ai_service._process_image(test_image_path)
        if processed_image:
            print(f"✓ Image processed successfully, base64 length: {len(processed_image)}")
        else:
            print("✗ Image processing failed")
            
        # Test full conversion
        print("\n=== Testing Full Conversion ===")
        result = ai_service.convert_screenshot_to_code(
            image_path=test_image_path,
            framework='react',
            css_framework='tailwind'
        )
        
        print(f"Conversion success: {result.get('success', False)}")
        print(f"HTML length: {len(result.get('html', ''))}")
        print(f"CSS length: {len(result.get('css', ''))}")
        print(f"JS length: {len(result.get('js', ''))}")
        print(f"Model used: {result.get('model_used', 'none')}")
        print(f"Processing time: {result.get('processing_time', 0):.2f}s")
        print(f"Tokens used: {result.get('tokens_used', 0)}")
        
        # Check if it's demo code
        html_content = result.get('html', '')
        is_demo = 'Demo mode' in html_content or 'Your App' in html_content
        print(f"Is demo code: {is_demo}")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
            
        # Cleanup
        os.unlink(test_image_path)
        
        return result

if __name__ == '__main__':
    print("Testing AI Service with Real Image Upload")
    print("=" * 50)
    
    result = test_ai_service_with_real_image()
    
    print("\n" + "=" * 50)
    print("Test completed.")
