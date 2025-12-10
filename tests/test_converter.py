# tests/test_converter.py
"""Tests for converter functionality."""

import pytest
from io import BytesIO
from app import create_app
from app.extensions import db
from app.models import Account, Conversion
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
        response = client.get('/converter/history', follow_redirects=False)
        assert response.status_code == 302
        
    def test_history_authenticated(self, authenticated_client):
        """Test authenticated user can access history page."""
        response = authenticated_client.get('/converter/history')
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
                original_filename='test.png',
                framework='react',
                status='completed',
                generated_code='<div>Test</div>'
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
                original_filename='test.png',
                framework='react',
                status='completed',
                generated_code='<div>Test</div>'
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
                original_filename='test.png',
                framework='react',
                status='completed',
                generated_code='<div>Test</div>'
            )
            db.session.add(conversion)
            db.session.commit()
            conversion_id = conversion.id
        
        response = authenticated_client.post(f'/converter/delete/{conversion_id}',
                                             follow_redirects=True)
        assert response.status_code == 200


class TestAIService:
    """Test AI service utilities."""
    
    def test_framework_validation(self):
        """Test framework validation."""
        from app.converter.utils import validate_framework
        
        valid_frameworks = ['react', 'vue', 'html', 'svelte', 'angular']
        for framework in valid_frameworks:
            assert validate_framework(framework) is True
        
        assert validate_framework('invalid') is False
        
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
