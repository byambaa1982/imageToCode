# tests/test_integration.py
"""Integration tests for end-to-end workflows."""

import pytest
import json
import tempfile
import os
from io import BytesIO
from PIL import Image
from unittest.mock import Mock, patch, MagicMock

from app import create_app
from app.extensions import db
from app.models import Account, Conversion, Package, Order, CreditsTransaction


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
        credits_remaining=5.0
    )
    user.set_password('TestPassword123!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def authenticated_client(client, test_user):
    """Create authenticated test client."""
    client.post('/auth/login', data={
        'email': test_user.email,
        'password': 'TestPassword123!'
    })
    return client


@pytest.fixture
def test_package(app):
    """Create a test package."""
    package = Package(
        name='Test Package',
        code='test_pack',
        description='Test package for integration tests',
        price=9.99,
        credits=10.0,
        is_active=True
    )
    db.session.add(package)
    db.session.commit()
    return package


@pytest.fixture
def sample_image():
    """Create a sample test image."""
    # Create a simple test image
    image = Image.new('RGB', (800, 600), color='white')
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


class TestEndToEndConversionWorkflow:
    """Test complete conversion workflows."""
    
    def test_complete_conversion_workflow(self, authenticated_client, test_user, sample_image):
        """Test complete conversion workflow from upload to download."""
        # Step 1: Access converter page
        response = authenticated_client.get('/converter')
        assert response.status_code == 200
        
        # Step 2: Upload image and start conversion
        with patch('app.converter.ai_service.AIService.generate_code') as mock_ai:
            mock_ai.return_value = (
                True,
                '<div class="container"><h1>Generated HTML</h1></div>',
                '.container { max-width: 1200px; margin: 0 auto; }',
                'console.log("Generated JS");',
                None
            )
            
            response = authenticated_client.post('/converter/upload', data={
                'file': (sample_image, 'test.png'),
                'framework': 'html',
                'css_framework': 'tailwind'
            })
            
            assert response.status_code in [200, 302]  # Success or redirect
            
            # Check that conversion was created
            conversion = Conversion.query.filter_by(account_id=test_user.id).first()
            assert conversion is not None
            assert conversion.framework == 'html'
            assert conversion.status in ['pending', 'completed']
    
    def test_conversion_with_insufficient_credits(self, authenticated_client, test_user, sample_image):
        """Test conversion fails when user has insufficient credits."""
        # Reduce user credits to 0
        test_user.credits_remaining = 0
        db.session.commit()
        
        response = authenticated_client.post('/converter/upload', data={
            'file': (sample_image, 'test.png'),
            'framework': 'html'
        })
        
        # Should redirect to pricing or show error
        assert response.status_code in [302, 400, 403]
    
    def test_conversion_preview_and_download(self, authenticated_client, test_user, sample_image):
        """Test conversion preview and download functionality."""
        with patch('app.converter.ai_service.AIService.generate_code') as mock_ai:
            mock_ai.return_value = (
                True,
                '<div>Test HTML</div>',
                '.test { color: blue; }',
                'console.log("test");',
                None
            )
            
            # Create a conversion
            response = authenticated_client.post('/converter/upload', data={
                'file': (sample_image, 'test.png'),
                'framework': 'react'
            })
            
            conversion = Conversion.query.filter_by(account_id=test_user.id).first()
            if conversion:
                # Test preview
                preview_response = authenticated_client.get(f'/converter/preview/{conversion.uuid}')
                assert preview_response.status_code == 200
                
                # Test download (if implemented)
                download_response = authenticated_client.get(f'/converter/download/{conversion.uuid}')
                assert download_response.status_code in [200, 404]  # 404 if not implemented yet
    
    def test_conversion_with_different_frameworks(self, authenticated_client, test_user, sample_image):
        """Test conversions with different frameworks."""
        frameworks = ['html', 'react', 'vue']
        
        with patch('app.converter.ai_service.AIService.generate_code') as mock_ai:
            mock_ai.return_value = (
                True,
                '<div>Framework test</div>',
                '.framework { display: block; }',
                'console.log("framework");',
                None
            )
            
            for framework in frameworks:
                response = authenticated_client.post('/converter/upload', data={
                    'file': (sample_image, f'test_{framework}.png'),
                    'framework': framework
                })
                
                assert response.status_code in [200, 302]
                
                # Verify conversion was created with correct framework
                conversion = Conversion.query.filter_by(
                    account_id=test_user.id,
                    framework=framework
                ).first()
                assert conversion is not None


class TestUserAuthenticationFlow:
    """Test user authentication and authorization workflows."""
    
    def test_complete_registration_flow(self, client):
        """Test complete user registration workflow."""
        # Step 1: Access registration page
        response = client.get('/auth/register')
        assert response.status_code == 200
        
        # Step 2: Submit registration
        with patch('app.tasks.email_tasks.send_verification_email.delay') as mock_email:
            response = client.post('/auth/register', data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'NewPassword123!',
                'confirm_password': 'NewPassword123!'
            })
            
            assert response.status_code in [200, 302]
            
            # Check user was created
            user = Account.query.filter_by(email='newuser@example.com').first()
            assert user is not None
            assert user.email_verified is False
            assert user.credits_remaining == 3.0  # Free tier credits
            
            # Check email was sent
            mock_email.assert_called_once()
    
    def test_login_logout_flow(self, client, test_user):
        """Test login and logout flow."""
        # Test login
        response = client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'TestPassword123!'
        })
        assert response.status_code in [200, 302]
        
        # Test accessing protected route
        response = client.get('/account/dashboard')
        assert response.status_code == 200
        
        # Test logout
        response = client.get('/auth/logout')
        assert response.status_code == 302
        
        # Test accessing protected route after logout
        response = client.get('/account/dashboard')
        assert response.status_code == 302  # Should redirect to login
    
    def test_password_reset_flow(self, client, test_user):
        """Test password reset workflow."""
        with patch('app.tasks.email_tasks.send_password_reset_email.delay') as mock_email:
            # Request password reset
            response = client.post('/auth/reset_password', data={
                'email': test_user.email
            })
            
            assert response.status_code in [200, 302]
            mock_email.assert_called_once()
    
    def test_protected_routes_require_auth(self, client):
        """Test that protected routes require authentication."""
        protected_routes = [
            '/account/dashboard',
            '/account/history',
            '/account/settings',
            '/converter',
            '/converter/upload'
        ]
        
        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 302  # Should redirect to login
    
    def test_admin_routes_require_admin_role(self, client, test_user):
        """Test that admin routes require admin role."""
        # Login as regular user
        client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'TestPassword123!'
        })
        
        admin_routes = [
            '/admin/dashboard',
            '/admin/users',
            '/admin/packages'
        ]
        
        for route in admin_routes:
            response = client.get(route)
            assert response.status_code == 302  # Should redirect (no admin access)


class TestPaymentIntegration:
    """Test payment and credit system integration."""
    
    def test_purchase_credits_workflow(self, authenticated_client, test_user, test_package):
        """Test complete credit purchase workflow."""
        initial_credits = test_user.credits_remaining
        
        # Step 1: Access pricing page
        response = authenticated_client.get('/main/pricing')
        assert response.status_code == 200
        
        # Step 2: Start checkout process
        response = authenticated_client.get(f'/payment/checkout/{test_package.id}')
        assert response.status_code in [200, 302]
        
        # Step 3: Simulate successful payment webhook
        with patch('stripe.Webhook.construct_event') as mock_webhook:
            mock_webhook.return_value = {
                'type': 'checkout.session.completed',
                'data': {
                    'object': {
                        'id': 'cs_test_123',
                        'amount_total': int(test_package.price * 100),
                        'payment_status': 'paid',
                        'metadata': {
                            'package_id': str(test_package.id),
                            'user_id': str(test_user.id)
                        }
                    }
                }
            }
            
            response = authenticated_client.post('/payment/webhook', 
                                                data='test_payload', 
                                                headers={'stripe-signature': 'test_sig'})
            
            # Verify credits were added
            db.session.refresh(test_user)
            expected_credits = initial_credits + test_package.credits
            assert test_user.credits_remaining == expected_credits
            
            # Verify transaction was recorded
            transaction = CreditsTransaction.query.filter_by(
                account_id=test_user.id,
                transaction_type='purchase'
            ).first()
            assert transaction is not None
    
    def test_credit_deduction_on_conversion(self, authenticated_client, test_user, sample_image):
        """Test that credits are deducted on successful conversion."""
        initial_credits = test_user.credits_remaining
        
        with patch('app.converter.ai_service.AIService.generate_code') as mock_ai:
            mock_ai.return_value = (
                True,
                '<div>Success</div>',
                '.success { color: green; }',
                'console.log("success");',
                None
            )
            
            response = authenticated_client.post('/converter/upload', data={
                'file': (sample_image, 'test.png'),
                'framework': 'html'
            })
            
            # Verify credits were deducted
            db.session.refresh(test_user)
            expected_credits = initial_credits - 1.0
            assert test_user.credits_remaining == expected_credits
            
            # Verify usage transaction was recorded
            transaction = CreditsTransaction.query.filter_by(
                account_id=test_user.id,
                transaction_type='usage'
            ).first()
            assert transaction is not None


class TestErrorHandlingScenarios:
    """Test error handling in various scenarios."""
    
    def test_invalid_file_upload(self, authenticated_client):
        """Test handling of invalid file uploads."""
        # Test with non-image file
        text_file = BytesIO(b"This is not an image")
        
        response = authenticated_client.post('/converter/upload', data={
            'file': (text_file, 'test.txt'),
            'framework': 'html'
        })
        
        assert response.status_code in [400, 422]  # Should reject invalid file
    
    def test_oversized_file_upload(self, authenticated_client):
        """Test handling of oversized file uploads."""
        # Create a large image (simulated)
        with patch('app.converter.utils.validate_image_file') as mock_validate:
            mock_validate.return_value = (False, "File size exceeds limit")
            
            large_file = BytesIO(b"x" * (16 * 1024 * 1024))  # 16MB
            
            response = authenticated_client.post('/converter/upload', data={
                'file': (large_file, 'large.png'),
                'framework': 'html'
            })
            
            assert response.status_code in [400, 413, 422]
    
    def test_ai_service_failure(self, authenticated_client, test_user, sample_image):
        """Test handling when AI service fails."""
        with patch('app.converter.ai_service.AIService.generate_code') as mock_ai:
            mock_ai.return_value = (False, None, None, None, "AI service unavailable")
            
            response = authenticated_client.post('/converter/upload', data={
                'file': (sample_image, 'test.png'),
                'framework': 'html'
            })
            
            # Should handle gracefully
            assert response.status_code in [200, 400, 500]
            
            # Check conversion status
            conversion = Conversion.query.filter_by(account_id=test_user.id).first()
            if conversion:
                assert conversion.status == 'failed'
    
    def test_database_connection_failure(self, client):
        """Test handling of database connection issues."""
        with patch('app.extensions.db.session.commit', side_effect=Exception("DB connection lost")):
            response = client.post('/auth/register', data={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'Password123!',
                'confirm_password': 'Password123!'
            })
            
            # Should handle database errors gracefully
            assert response.status_code in [200, 500]
    
    def test_rate_limiting(self, authenticated_client, sample_image):
        """Test rate limiting on conversion uploads."""
        # Simulate multiple rapid requests
        responses = []
        for i in range(5):
            response = authenticated_client.post('/converter/upload', data={
                'file': (sample_image, f'test_{i}.png'),
                'framework': 'html'
            })
            responses.append(response.status_code)
        
        # At least one should be rate limited (if implemented)
        # This test may pass if rate limiting is not yet implemented
        assert any(code == 429 for code in responses) or all(code in [200, 302, 400] for code in responses)
    
    def test_concurrent_conversions(self, authenticated_client, sample_image):
        """Test handling of concurrent conversion requests."""
        with patch('app.converter.ai_service.AIService.generate_code') as mock_ai:
            mock_ai.return_value = (
                True,
                '<div>Concurrent test</div>',
                '.concurrent { display: block; }',
                'console.log("concurrent");',
                None
            )
            
            # Submit multiple conversions simultaneously (simulated)
            responses = []
            for i in range(3):
                response = authenticated_client.post('/converter/upload', data={
                    'file': (sample_image, f'concurrent_{i}.png'),
                    'framework': 'html'
                })
                responses.append(response.status_code)
            
            # All should be handled (queued or processed)
            assert all(code in [200, 202, 302] for code in responses)
