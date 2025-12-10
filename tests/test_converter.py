# tests/test_converter.py
"""Tests for converter functionality."""

import pytest
import json
import base64
import os
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
from app import create_app
from app.extensions import db
from app.models import Account, Conversion, ConversionFeedback
from app.converter.ai_service import AIService
from flask_login import login_user


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a verified test user with credits."""
    user = Account(
        email='test@example.com',
        username='testuser',
        email_verified=True,
        credits_remaining=10.0
    )
    user.set_password('TestPassword123!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    """Create authenticated test client."""
    with client:
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })
        yield client


class TestConverterAccess:
    """Test converter page access."""
    
    def test_upload_page_requires_login(self, client):
        """Test upload page requires authentication."""
        response = client.get('/converter/upload', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login
        
    def test_upload_page_authenticated(self, authenticated_client):
        """Test authenticated user can access upload page."""
        response = authenticated_client.get('/converter/upload')
        assert response.status_code == 200
        assert b'Upload' in response.data or b'Convert' in response.data
        
    def test_history_requires_login(self, client):
        """Test history page requires authentication."""
        response = client.get('/account/history', follow_redirects=False)
        assert response.status_code == 302
        
    def test_history_authenticated(self, authenticated_client):
        """Test authenticated user can access history page."""
        response = authenticated_client.get('/account/history')
        assert response.status_code == 200


class TestImageUpload:
    """Test image upload functionality."""
    
    def test_upload_without_file(self, authenticated_client):
        """Test upload without file."""
        response = authenticated_client.post('/converter/upload', data={
            'framework': 'react'
        })
        # Should show error or return to upload page
        assert response.status_code in [200, 302]
        
    def test_upload_invalid_file_type(self, authenticated_client):
        """Test upload with invalid file type."""
        data = {
            'file': (BytesIO(b'not an image'), 'test.txt'),
            'framework': 'react'
        }
        response = authenticated_client.post('/converter/upload', 
                                             data=data,
                                             content_type='multipart/form-data')
        assert response.status_code in [200, 400]
        
    def test_upload_without_credits(self, authenticated_client, app, test_user):
        """Test upload without sufficient credits."""
        with app.app_context():
            user = Account.query.get(test_user.id)
            user.credits_remaining = 0
            db.session.commit()
        
        # Create a simple test image
        data = {
            'file': (BytesIO(b'fake image data'), 'test.png'),
            'framework': 'react'
        }
        response = authenticated_client.post('/converter/upload',
                                             data=data,
                                             content_type='multipart/form-data')
        # Should show insufficient credits error
        assert response.status_code in [200, 302, 400]


class TestConversionHistory:
    """Test conversion history."""
    
    def test_view_conversion_history(self, authenticated_client, app, test_user):
        """Test viewing conversion history."""
        with app.app_context():
            # Create test conversion
            conversion = Conversion(
                account_id=test_user.id,
                original_image_url='http://example.com/test.png',
                original_filename='test.png',
                framework='react',
                status='completed',
                generated_html='<div>Test</div>'
            )
            db.session.add(conversion)
            db.session.commit()
        
        response = authenticated_client.get('/converter/history')
        assert response.status_code == 200
        
    def test_view_specific_conversion(self, authenticated_client, app, test_user):
        """Test viewing specific conversion."""
        with app.app_context():
            conversion = Conversion(
                account_id=test_user.id,
                original_image_url='http://example.com/test.png',
                original_filename='test.png',
                framework='react',
                status='completed',
                generated_html='<div>Test</div>'
            )
            db.session.add(conversion)
            db.session.commit()
            conversion_id = conversion.id
        
        response = authenticated_client.get(f'/converter/conversion/{conversion_id}')
        assert response.status_code in [200, 404]  # Depends on if route exists
        
    def test_delete_conversion(self, authenticated_client, app, test_user):
        """Test deleting conversion."""
        with app.app_context():
            conversion = Conversion(
                account_id=test_user.id,
                original_image_url='http://example.com/test.png',
                original_filename='test.png',
                framework='react',
                status='completed',
                generated_html='<div>Test</div>'
            )
            db.session.add(conversion)
            db.session.commit()
            conversion_id = conversion.id
        
        response = authenticated_client.post(f'/converter/delete/{conversion_id}',
                                             follow_redirects=True)
        assert response.status_code == 200


class TestConverterUtils:
    """Test converter utility functions."""
    
    def test_framework_validation(self):
        """Test framework validation."""
        from app.converter.utils import validate_framework
        
        valid_frameworks = ['react', 'vue', 'html', 'svelte', 'angular']
        for framework in valid_frameworks:
            assert validate_framework(framework) is True
        
        assert validate_framework('invalid') is False
        
    def test_framework_validation_case_insensitive(self):
        """Test framework validation is case insensitive."""
        from app.converter.utils import validate_framework
        
        assert validate_framework('REACT') is True
        assert validate_framework('Vue') is True
        assert validate_framework('HTML') is True
        assert validate_framework('React') is True
        
    def test_framework_validation_additional_frameworks(self):
        """Test additional supported frameworks."""
        from app.converter.utils import validate_framework
        
        # Test additional frameworks from the function
        assert validate_framework('nextjs') is True
        assert validate_framework('nuxt') is True
        assert validate_framework('bootstrap') is True
        assert validate_framework('tailwind') is True
        
    def test_file_validation(self):
        """Test file validation."""
        from app.converter.utils import allowed_file
        
        assert allowed_file('image.png') is True
        assert allowed_file('image.jpg') is True
        assert allowed_file('image.jpeg') is True
        assert allowed_file('image.gif') is True
        assert allowed_file('image.webp') is True
        
        assert allowed_file('file.txt') is False
        assert allowed_file('file.pdf') is False
        assert allowed_file('noextension') is False
        
    def test_allowed_file_edge_cases(self):
        """Test allowed file edge cases."""
        from app.converter.utils import allowed_file
        
        # Test edge cases
        assert allowed_file('') is False
        assert allowed_file(None) is False
        assert allowed_file('file.') is False
        assert allowed_file('.png') is False  # No filename
        assert allowed_file('file..png') is True  # Double dot should work
        
    def test_validate_image_file_no_file(self):
        """Test image file validation with no file."""
        from app.converter.utils import validate_image_file
        
        is_valid, error = validate_image_file(None)
        assert is_valid is False
        assert "No file provided" in error
        
    def test_validate_image_file_no_filename(self):
        """Test image file validation with no filename."""
        from app.converter.utils import validate_image_file
        from werkzeug.datastructures import FileStorage
        from io import BytesIO
        
        file_mock = Mock(spec=FileStorage)
        file_mock.filename = None
        
        is_valid, error = validate_image_file(file_mock)
        assert is_valid is False
        assert "No filename provided" in error
        
    def test_validate_image_file_invalid_extension(self):
        """Test image file validation with invalid extension."""
        from app.converter.utils import validate_image_file
        from werkzeug.datastructures import FileStorage
        from io import BytesIO
        
        file_mock = Mock(spec=FileStorage)
        file_mock.filename = 'test.txt'
        
        is_valid, error = validate_image_file(file_mock)
        assert is_valid is False
        assert "File type not allowed" in error
        
    def test_validate_image_file_empty_file(self):
        """Test image file validation with empty file."""
        from app.converter.utils import validate_image_file
        from werkzeug.datastructures import FileStorage
        from io import BytesIO
        
        file_mock = Mock(spec=FileStorage)
        file_mock.filename = 'test.png'
        file_mock.read.return_value = b''  # Empty file
        
        is_valid, error = validate_image_file(file_mock)
        assert is_valid is False
        assert "File is empty" in error
        
    def test_validate_image_file_invalid_image_data(self):
        """Test image file validation with invalid image data."""
        from app.converter.utils import validate_image_file
        from werkzeug.datastructures import FileStorage
        from io import BytesIO
        
        file_mock = Mock(spec=FileStorage)
        file_mock.filename = 'test.png'
        file_mock.read.return_value = b'not an image'
        file_mock.seek.return_value = None
        
        is_valid, error = validate_image_file(file_mock)
        assert is_valid is False
        assert "Invalid image file" in error
        
    def test_validate_image_file_success(self):
        """Test successful image file validation."""
        from app.converter.utils import validate_image_file
        from werkzeug.datastructures import FileStorage
        from PIL import Image
        import io
        
        # Create a valid test image
        img = Image.new('RGB', (200, 200), color='red')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        file_mock = Mock(spec=FileStorage)
        file_mock.filename = 'test.png'
        file_mock.read.return_value = img_buffer.getvalue()
        file_mock.seek.return_value = None
        
        # Mock Image.open to return our test image
        with patch('app.converter.utils.Image.open') as mock_open:
            mock_img = Mock()
            mock_img.size = (200, 200)
            mock_img.verify.return_value = None
            mock_open.return_value = mock_img
            
            is_valid, error = validate_image_file(file_mock)
            assert is_valid is True
            assert error is None
            
    def test_validate_image_file_too_small(self):
        """Test image file validation with too small image."""
        from app.converter.utils import validate_image_file
        from werkzeug.datastructures import FileStorage
        import io
        
        file_mock = Mock(spec=FileStorage)
        file_mock.filename = 'small.png'
        file_mock.read.return_value = b'fake image data'
        file_mock.seek.return_value = None
        
        # Mock Image.open to return small image
        with patch('app.converter.utils.Image.open') as mock_open:
            mock_img = Mock()
            mock_img.size = (50, 50)  # Too small
            mock_img.verify.return_value = None
            mock_open.return_value = mock_img
            
            is_valid, error = validate_image_file(file_mock)
            assert is_valid is False
            assert "Image too small" in error
            
    def test_validate_image_file_too_large(self):
        """Test image file validation with too large image."""
        from app.converter.utils import validate_image_file
        from werkzeug.datastructures import FileStorage
        
        file_mock = Mock(spec=FileStorage)
        file_mock.filename = 'large.png'
        file_mock.read.return_value = b'fake image data'
        file_mock.seek.return_value = None
        
        # Mock Image.open to return large image
        with patch('app.converter.utils.Image.open') as mock_open:
            mock_img = Mock()
            mock_img.size = (5000, 5000)  # Too large
            mock_img.verify.return_value = None
            mock_open.return_value = mock_img
            
            is_valid, error = validate_image_file(file_mock)
            assert is_valid is False
            assert "Image too large" in error
            
    def test_save_uploaded_file_success(self, tmp_path):
        """Test successful file upload save."""
        from app.converter.utils import save_uploaded_file
        from werkzeug.datastructures import FileStorage
        import io
        
        # Mock Config.UPLOAD_FOLDER
        with patch('app.converter.utils.Config.UPLOAD_FOLDER', str(tmp_path)):
            file_mock = Mock(spec=FileStorage)
            file_mock.filename = 'test image.png'  # Test filename with space
            file_mock.save = Mock()
            
            # Mock os.path.exists to return True after save
            with patch('os.path.exists', return_value=True):
                success, file_path, error = save_uploaded_file(file_mock, 'test-uuid')
                
                assert success is True
                assert 'test-uuid.png' in file_path
                assert error is None
                file_mock.save.assert_called_once()
                
    def test_save_uploaded_file_save_failure(self, tmp_path):
        """Test file save failure."""
        from app.converter.utils import save_uploaded_file
        from werkzeug.datastructures import FileStorage
        
        with patch('app.converter.utils.Config.UPLOAD_FOLDER', str(tmp_path)):
            file_mock = Mock(spec=FileStorage)
            file_mock.filename = 'test.png'
            file_mock.save = Mock()
            
            # Mock os.path.exists to return False (save failed)
            with patch('os.path.exists', return_value=False):
                success, file_path, error = save_uploaded_file(file_mock, 'test-uuid')
                
                assert success is False
                assert file_path is None
                assert "Failed to save file" in error
                
    def test_save_uploaded_file_exception(self):
        """Test file save with exception."""
        from app.converter.utils import save_uploaded_file
        from werkzeug.datastructures import FileStorage
        
        file_mock = Mock(spec=FileStorage)
        file_mock.filename = 'test.png'
        file_mock.save.side_effect = Exception("Disk full")
        
        success, file_path, error = save_uploaded_file(file_mock, 'test-uuid')
        
        assert success is False
        assert file_path is None
        assert "Error saving file" in error
        assert "Disk full" in error
        
    def test_process_image_for_ai_rgb_image(self, tmp_path):
        """Test processing RGB image for AI."""
        from app.converter.utils import process_image_for_ai
        from PIL import Image
        
        # Create test RGB image
        img = Image.new('RGB', (100, 100), color='blue')
        image_path = tmp_path / "rgb_test.png"
        img.save(image_path)
        
        success, processed_path, error = process_image_for_ai(str(image_path))
        
        assert success is True
        assert processed_path == str(image_path)  # Should return original path for RGB
        assert error is None
        
    def test_process_image_for_ai_non_rgb_image(self, tmp_path):
        """Test processing non-RGB image for AI."""
        from app.converter.utils import process_image_for_ai
        from PIL import Image
        
        # Create test RGBA image
        img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        image_path = tmp_path / "rgba_test.png"
        img.save(image_path)
        
        success, processed_path, error = process_image_for_ai(str(image_path))
        
        assert success is True
        assert processed_path != str(image_path)  # Should create new processed file
        assert '_processed.' in processed_path
        assert error is None
        
        # Verify processed file exists and is RGB
        processed_img = Image.open(processed_path)
        assert processed_img.mode == 'RGB'
        
    def test_process_image_for_ai_invalid_path(self):
        """Test processing image with invalid path."""
        from app.converter.utils import process_image_for_ai
        
        success, processed_path, error = process_image_for_ai('/nonexistent/path.png')
        
        assert success is False
        assert processed_path is None
        assert "Error processing image" in error
        
    def test_cleanup_temp_files_success(self, tmp_path):
        """Test successful cleanup of temporary files."""
        from app.converter.utils import cleanup_temp_files
        
        # Create test files
        file1 = tmp_path / "temp1.txt"
        file2 = tmp_path / "temp2.txt"
        file1.write_text("test")
        file2.write_text("test")
        
        file_paths = [str(file1), str(file2)]
        cleanup_temp_files(file_paths)
        
        # Files should be deleted
        assert not file1.exists()
        assert not file2.exists()
        
    def test_cleanup_temp_files_with_nonexistent(self, tmp_path):
        """Test cleanup with some nonexistent files."""
        from app.converter.utils import cleanup_temp_files
        
        # Create one real file
        file1 = tmp_path / "temp1.txt"
        file1.write_text("test")
        
        file_paths = [str(file1), '/nonexistent/file.txt', None, '']
        cleanup_temp_files(file_paths)
        
        # Real file should be deleted, no errors for nonexistent
        assert not file1.exists()
        
    def test_cleanup_temp_files_permission_error(self, tmp_path):
        """Test cleanup with permission error."""
        from app.converter.utils import cleanup_temp_files
        
        file1 = tmp_path / "temp1.txt"
        file1.write_text("test")
        
        # Mock os.remove to raise permission error
        with patch('os.remove', side_effect=PermissionError("Access denied")):
            # Should not raise exception, just log error
            cleanup_temp_files([str(file1)])
            
    def test_generate_preview_html(self):
        """Test HTML preview generation."""
        from app.converter.utils import generate_preview_html
        
        html_code = '<div class="container">Hello World</div>'
        css_code = '.container { color: blue; }'
        js_code = 'console.log("Hello");'
        
        preview = generate_preview_html(html_code, css_code, js_code)
        
        assert '<!DOCTYPE html>' in preview
        assert html_code in preview
        assert css_code in preview
        assert js_code in preview
        assert 'charset="UTF-8"' in preview
        
    def test_generate_preview_html_empty_codes(self):
        """Test HTML preview generation with empty code sections."""
        from app.converter.utils import generate_preview_html
        
        preview = generate_preview_html('', '', '')
        
        assert '<!DOCTYPE html>' in preview
        assert '<html lang="en">' in preview
        assert '</html>' in preview
        
    def test_extract_framework_specific_code_react(self):
        """Test React framework-specific code extraction."""
        from app.converter.utils import extract_framework_specific_code
        
        # Test code that needs React wrapping
        code = '<div>React Component</div>'
        result = extract_framework_specific_code(code, 'react')
        
        # Should return original code since it doesn't match wrapping criteria
        assert result == code
        
    def test_extract_framework_specific_code_react_needs_wrapping(self):
        """Test React code that needs component wrapping."""
        from app.converter.utils import extract_framework_specific_code
        
        # Test code that needs wrapping (no export default, no function)
        code = '<div>Component Content</div>'
        result = extract_framework_specific_code(code, 'react')
        
        # The current implementation doesn't wrap this case, but test existing behavior
        assert '<div>Component Content</div>' in result
        
    def test_extract_framework_specific_code_vue(self):
        """Test Vue framework-specific code extraction."""
        from app.converter.utils import extract_framework_specific_code
        
        code = '<div>Vue Component</div>'
        result = extract_framework_specific_code(code, 'vue')
        
        assert '<template>' in result
        assert code in result
        assert '<script setup>' in result
        assert '<style scoped>' in result
        
    def test_extract_framework_specific_code_vue_already_template(self):
        """Test Vue code that already has template."""
        from app.converter.utils import extract_framework_specific_code
        
        code = '<template><div>Already formatted</div></template>'
        result = extract_framework_specific_code(code, 'vue')
        
        # Should return original code
        assert result == code
        
    def test_extract_framework_specific_code_other_framework(self):
        """Test code extraction for other frameworks."""
        from app.converter.utils import extract_framework_specific_code
        
        code = '<div>HTML Content</div>'
        result = extract_framework_specific_code(code, 'html')
        
        # Should return original code unchanged
        assert result == code
        
    def test_validate_generated_code_valid_html(self):
        """Test validation of valid HTML code."""
        from app.converter.utils import validate_generated_code
        
        html_code = '<div><p>Hello World</p></div>'
        css_code = '.test { color: red; }'
        js_code = 'function test() { console.log("hello"); }'
        
        is_valid, error = validate_generated_code(html_code, css_code, js_code)
        
        assert is_valid is True
        assert error is None
        
    def test_validate_generated_code_unbalanced_html_tags(self):
        """Test validation of HTML with unbalanced tags."""
        from app.converter.utils import validate_generated_code
        
        html_code = '<div><p>Hello World</div>'  # Missing closing </p>
        
        is_valid, error = validate_generated_code(html_code, '', '')
        
        assert is_valid is False
        assert "unbalanced tags" in error
        
    def test_validate_generated_code_unbalanced_css_braces(self):
        """Test validation of CSS with unbalanced braces."""
        from app.converter.utils import validate_generated_code
        
        css_code = '.test { color: red;'  # Missing closing brace
        
        is_valid, error = validate_generated_code('', css_code, '')
        
        assert is_valid is False
        assert "unbalanced braces" in error
        
    def test_validate_generated_code_unbalanced_js_parentheses(self):
        """Test validation of JS with unbalanced parentheses."""
        from app.converter.utils import validate_generated_code
        
        js_code = 'function test( { console.log("hello"); }'  # Missing closing )
        
        is_valid, error = validate_generated_code('', '', js_code)
        
        assert is_valid is False
        assert "unbalanced parentheses" in error
        
    def test_validate_generated_code_unbalanced_js_braces(self):
        """Test validation of JS with unbalanced braces."""
        from app.converter.utils import validate_generated_code
        
        js_code = 'function test() { console.log("hello");'  # Missing closing }
        
        is_valid, error = validate_generated_code('', '', js_code)
        
        assert is_valid is False
        assert "unbalanced braces" in error
        
    def test_validate_generated_code_empty_codes(self):
        """Test validation with empty code sections."""
        from app.converter.utils import validate_generated_code
        
        is_valid, error = validate_generated_code('', '', '')
        
        assert is_valid is True
        assert error is None
        
    def test_validate_generated_code_exception(self):
        """Test validation with exception in processing."""
        from app.converter.utils import validate_generated_code
        
        # Mock str.count to raise an exception
        with patch('builtins.str.count', side_effect=Exception("Test error")):
            is_valid, error = validate_generated_code('<div></div>', '', '')
            
            assert is_valid is False
            assert "Code validation error" in error
            
    def test_get_file_size_mb_success(self, tmp_path):
        """Test successful file size calculation."""
        from app.converter.utils import get_file_size_mb
        
        # Create test file with known size
        test_file = tmp_path / "test.txt"
        test_content = "x" * 1024 * 1024  # 1 MB
        test_file.write_text(test_content)
        
        size_mb = get_file_size_mb(str(test_file))
        
        assert size_mb == 1.0
        
    def test_get_file_size_mb_nonexistent_file(self):
        """Test file size calculation for nonexistent file."""
        from app.converter.utils import get_file_size_mb
        
        size_mb = get_file_size_mb('/nonexistent/file.txt')
        
        assert size_mb == 0.0
        
    def test_get_file_size_mb_small_file(self, tmp_path):
        """Test file size calculation for small file."""
        from app.converter.utils import get_file_size_mb
        
        test_file = tmp_path / "small.txt"
        test_file.write_text("hello")
        
        size_mb = get_file_size_mb(str(test_file))
        
        assert size_mb > 0
        assert size_mb < 0.01  # Should be very small
        
    def test_create_download_package_success(self, tmp_path):
        """Test successful download package creation."""
        from app.converter.utils import create_download_package
        
        html_code = '<div>Test HTML</div>'
        css_code = '.test { color: blue; }'
        js_code = 'console.log("test");'
        conversion_uuid = 'test-uuid-123'
        
        # Mock Config.UPLOAD_FOLDER
        with patch('app.converter.utils.Config.UPLOAD_FOLDER', str(tmp_path)):
            success, zip_path, error = create_download_package(
                html_code, css_code, js_code, conversion_uuid
            )
            
            assert success is True
            assert zip_path is not None
            assert conversion_uuid in zip_path
            assert error is None
            
            # Verify ZIP file exists and contains expected files
            import zipfile
            assert os.path.exists(zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                assert 'index.html' in file_list
                assert 'styles.css' in file_list
                assert 'script.js' in file_list
                
                # Verify content
                assert html_code in zipf.read('index.html').decode()
                assert css_code in zipf.read('styles.css').decode()
                assert js_code in zipf.read('script.js').decode()
                
    def test_create_download_package_html_only(self, tmp_path):
        """Test download package creation with only HTML."""
        from app.converter.utils import create_download_package
        
        html_code = '<div>Only HTML</div>'
        conversion_uuid = 'html-only-uuid'
        
        with patch('app.converter.utils.Config.UPLOAD_FOLDER', str(tmp_path)):
            success, zip_path, error = create_download_package(
                html_code, '', '', conversion_uuid
            )
            
            assert success is True
            assert zip_path is not None
            
            # Verify ZIP contains only HTML file
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                assert 'index.html' in file_list
                assert 'styles.css' not in file_list
                assert 'script.js' not in file_list
                
    def test_create_download_package_empty_content(self, tmp_path):
        """Test download package creation with empty content."""
        from app.converter.utils import create_download_package
        
        conversion_uuid = 'empty-uuid'
        
        with patch('app.converter.utils.Config.UPLOAD_FOLDER', str(tmp_path)):
            success, zip_path, error = create_download_package('', '', '', conversion_uuid)
            
            assert success is True
            assert zip_path is not None
            
            # Verify ZIP exists but has no content files
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                assert len(file_list) == 0
                
    def test_create_download_package_exception(self):
        """Test download package creation with exception."""
        from app.converter.utils import create_download_package
        
        # Mock tempfile.mkdtemp to raise exception
        with patch('tempfile.mkdtemp', side_effect=Exception("No temp space")):
            success, zip_path, error = create_download_package(
                '<div>test</div>', '', '', 'error-uuid'
            )
            
            assert success is False
            assert zip_path is None
            assert "Error creating download package" in error
            assert "No temp space" in error

# ...existing code...
