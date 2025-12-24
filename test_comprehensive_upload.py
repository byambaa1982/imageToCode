#!/usr/bin/env python3
"""
Comprehensive test to verify uploaded screenshots are processed correctly.
"""

import sys
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont

# Add the project root to the Python path
sys.path.insert(0, '/Users/zoloo/project_v2/imageToCode')

from app import create_app
from app.converter.ai_service import AIService

def create_distinctive_test_image():
    """Create a distinctive test image that would be recognizable in analysis."""
    # Create a colorful image with different elements
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add a blue header section
    draw.rectangle([0, 0, 800, 100], fill='blue')
    
    # Add some red elements
    draw.rectangle([50, 150, 200, 250], fill='red')
    draw.rectangle([250, 150, 400, 250], fill='red')
    
    # Add green elements  
    draw.rectangle([450, 150, 600, 250], fill='green')
    
    # Add some text areas (represented as gray boxes)
    draw.rectangle([50, 300, 750, 350], fill='lightgray')
    draw.rectangle([50, 370, 500, 420], fill='lightgray')
    
    # Add a purple footer
    draw.rectangle([0, 500, 800, 600], fill='purple')
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name, 'PNG')
    return temp_file.name

def create_mobile_test_image():
    """Create a mobile-style test image."""
    # Create a tall, narrow image (mobile-like)
    img = Image.new('RGB', (375, 812), color='white')  # iPhone dimensions
    draw = ImageDraw.Draw(img)
    
    # Mobile header
    draw.rectangle([0, 0, 375, 60], fill='darkblue')
    
    # Content area with warm colors
    draw.rectangle([20, 80, 355, 200], fill='orange')
    draw.rectangle([20, 220, 355, 340], fill='yellow')
    draw.rectangle([20, 360, 355, 480], fill='red')
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name, 'PNG')
    return temp_file.name

def test_image_processing_and_analysis():
    """Test image processing and analysis capabilities."""
    app = create_app()
    
    with app.app_context():
        print("=== Testing Image Processing and Analysis ===")
        
        # Test 1: Regular landscape image
        print("\n1. Testing Landscape Image:")
        test_image_path = create_distinctive_test_image()
        print(f"   Created test image: {test_image_path}")
        
        ai_service = AIService()
        
        # Test image processing
        processed_image = ai_service._process_image(test_image_path)
        if processed_image:
            print(f"   ✓ Image processed successfully, base64 length: {len(processed_image)}")
        else:
            print("   ✗ Image processing failed")
        
        # Test image analysis
        image_properties = ai_service._analyze_image_properties(test_image_path)
        print(f"   ✓ Image properties: {image_properties}")
        
        # Test demo code generation with properties
        demo_code = ai_service._generate_demo_code('react', 'tailwind', image_properties)
        print(f"   ✓ Demo code generated - HTML length: {len(demo_code.get('html', ''))}")
        
        # Cleanup
        os.unlink(test_image_path)
        
        # Test 2: Mobile-style image
        print("\n2. Testing Mobile-Style Image:")
        mobile_image_path = create_mobile_test_image()
        print(f"   Created mobile test image: {mobile_image_path}")
        
        # Test image analysis for mobile
        mobile_properties = ai_service._analyze_image_properties(mobile_image_path)
        print(f"   ✓ Mobile image properties: {mobile_properties}")
        
        # Test full conversion
        result = ai_service.convert_screenshot_to_code(
            image_path=mobile_image_path,
            framework='react',
            css_framework='tailwind'
        )
        
        print(f"   ✓ Conversion success: {result.get('success', False)}")
        print(f"   ✓ Is demo mode: {result.get('is_demo', False)}")
        print(f"   ✓ HTML length: {len(result.get('html', ''))}")
        print(f"   ✓ Processing time: {result.get('processing_time', 0):.3f}s")
        
        # Check if the HTML contains any image-specific content
        html_content = result.get('html', '')
        if mobile_properties.get('is_mobile'):
            print(f"   ✓ Mobile layout detected: {mobile_properties.get('is_mobile')}")
        
        if result.get('error'):
            print(f"   ✗ Error: {result['error']}")
            
        # Cleanup
        os.unlink(mobile_image_path)
        
        return result

def test_upload_flow_simulation():
    """Simulate the full upload flow."""
    print("\n=== Simulating Full Upload Flow ===")
    
    # This would simulate what happens when a user uploads an image
    test_image_path = create_distinctive_test_image()
    print(f"Simulated upload of: {test_image_path}")
    
    app = create_app()
    with app.app_context():
        # Simulate the conversion task
        from app.tasks.conversion_tasks import process_screenshot_conversion
        from app.models import Conversion, Account
        from app.extensions import db
        import uuid
        
        # Would normally be handled by the upload route, but we'll simulate
        conversion_uuid = str(uuid.uuid4())
        print(f"Generated conversion UUID: {conversion_uuid}")
        
        # Create a test conversion record (this would normally be done in routes.py)
        test_conversion = Conversion(
            uuid=conversion_uuid,
            account_id=1,  # Assume test account exists
            original_image_url=test_image_path,
            original_filename='test_image.png',
            framework='react',
            css_framework='tailwind',
            status='pending'
        )
        
        try:
            db.session.add(test_conversion)
            db.session.commit()
            print("✓ Test conversion record created")
            
            # This is what would be called by the background thread
            result = process_screenshot_conversion(conversion_uuid)
            print(f"✓ Conversion processed: {result.get('success', False)}")
            
            # Check the final result in database
            final_conversion = Conversion.query.filter_by(uuid=conversion_uuid).first()
            if final_conversion:
                print(f"✓ Final status: {final_conversion.status}")
                print(f"✓ Generated HTML length: {len(final_conversion.generated_html or '')}")
                print(f"✓ Processing time: {final_conversion.processing_time}")
                print(f"✓ Tokens used: {final_conversion.tokens_used}")
                
                # Check if this was demo mode
                is_demo = (
                    final_conversion.tokens_used == 0 and 
                    'Your App' in (final_conversion.generated_html or '')
                )
                print(f"✓ Demo mode detected: {is_demo}")
            
        except Exception as e:
            print(f"✗ Error in flow simulation: {e}")
        finally:
            # Cleanup
            try:
                if 'final_conversion' in locals() and final_conversion:
                    db.session.delete(final_conversion)
                    db.session.commit()
                os.unlink(test_image_path)
            except:
                pass

if __name__ == '__main__':
    print("Testing Screenshot Processing and Upload Flow")
    print("=" * 50)
    
    try:
        test_image_processing_and_analysis()
        test_upload_flow_simulation()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Test completed.")
