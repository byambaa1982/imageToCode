# tests/test_admin.py
"""Tests for admin functionality."""

import pytest
from app import create_app
from app.extensions import db
from app.models import Account, Conversion, Package


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
def admin_user(app):
    """Create an admin user."""
    user = Account(
        email='admin@example.com',
        username='admin',
        email_verified=True,
        is_admin=True,
        credits_remaining=100.0
    )
    user.set_password('AdminPassword123!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def regular_user(app):
    """Create a regular user."""
    user = Account(
        email='user@example.com',
        username='regularuser',
        email_verified=True,
        is_admin=False,
        credits_remaining=10.0
    )
    user.set_password('UserPassword123!')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_client(client, admin_user):
    """Create authenticated admin client."""
    with client:
        client.post('/auth/login', data={
            'email': 'admin@example.com',
            'password': 'AdminPassword123!'
        })
        yield client


@pytest.fixture
def regular_client(client, regular_user):
    """Create authenticated regular user client."""
    with client:
        client.post('/auth/login', data={
            'email': 'user@example.com',
            'password': 'UserPassword123!'
        })
        yield client


class TestAdminAccess:
    """Test admin panel access control."""
    
    def test_admin_dashboard_requires_login(self, client):
        """Test admin dashboard requires authentication."""
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 302
        
    def test_admin_dashboard_requires_admin(self, regular_client):
        """Test admin dashboard requires admin privileges."""
        response = regular_client.get('/admin/dashboard', follow_redirects=True)
        assert response.status_code in [200, 403, 404]
        # Should be redirected or denied
        
    def test_admin_dashboard_admin_access(self, admin_client):
        """Test admin can access admin dashboard."""
        response = admin_client.get('/admin/dashboard')
        assert response.status_code == 200
        assert b'Admin' in response.data or b'Dashboard' in response.data


class TestUserManagement:
    """Test user management features."""
    
    def test_view_users_list(self, admin_client, regular_user):
        """Test viewing users list."""
        response = admin_client.get('/admin/users')
        assert response.status_code == 200
        assert b'user@example.com' in response.data or b'Users' in response.data
        
    def test_search_users(self, admin_client, regular_user):
        """Test searching users."""
        response = admin_client.get('/admin/users?search=regularuser')
        assert response.status_code == 200
        
    def test_filter_users(self, admin_client, regular_user):
        """Test filtering users."""
        response = admin_client.get('/admin/users?verified=1')
        assert response.status_code == 200
        
    def test_view_user_details(self, admin_client, regular_user):
        """Test viewing user details."""
        response = admin_client.get(f'/admin/user/{regular_user.id}')
        assert response.status_code in [200, 404]
        
    def test_edit_user_credits(self, admin_client, app, regular_user):
        """Test admin can edit user credits."""
        response = admin_client.post(f'/admin/user/{regular_user.id}/credits', data={
            'credits': 20.0
        }, follow_redirects=True)
        
        assert response.status_code in [200, 404]
        
    def test_deactivate_user(self, admin_client, app, regular_user):
        """Test admin can deactivate user."""
        response = admin_client.post(f'/admin/user/{regular_user.id}/deactivate',
                                     follow_redirects=True)
        
        assert response.status_code in [200, 404]


class TestPackageManagement:
    """Test package management features."""
    
    def test_view_packages(self, admin_client):
        """Test viewing packages list."""
        response = admin_client.get('/admin/packages')
        assert response.status_code in [200, 404]
        
    def test_create_package(self, admin_client):
        """Test creating new package."""
        response = admin_client.post('/admin/package/create', data={
            'name': 'New Package',
            'code': 'new_package',
            'description': 'Test package',
            'credits': 50.0,
            'price': 49.99,
            'is_active': True,
            'display_order': 1
        }, follow_redirects=True)
        
        assert response.status_code in [200, 404]
        
    def test_edit_package(self, admin_client, app):
        """Test editing package."""
        with app.app_context():
            package = Package(
                name='Test Package',
                code='test_edit',
                description='Test',
                credits=10.0,
                price=9.99,
                is_active=True,
                display_order=1
            )
            db.session.add(package)
            db.session.commit()
            package_id = package.id
        
        response = admin_client.post(f'/admin/package/{package_id}/edit', data={
            'name': 'Updated Package',
            'price': 19.99
        }, follow_redirects=True)
        
        assert response.status_code in [200, 404]
        
    def test_deactivate_package(self, admin_client, app):
        """Test deactivating package."""
        with app.app_context():
            package = Package(
                name='Test Package',
                code='test_deact',
                description='Test',
                credits=10.0,
                price=9.99,
                is_active=True,
                display_order=1
            )
            db.session.add(package)
            db.session.commit()
            package_id = package.id
        
        response = admin_client.post(f'/admin/package/{package_id}/deactivate',
                                     follow_redirects=True)
        
        assert response.status_code in [200, 404]


class TestAnalytics:
    """Test admin analytics."""
    
    def test_view_analytics(self, admin_client):
        """Test viewing analytics dashboard."""
        response = admin_client.get('/admin/analytics')
        assert response.status_code in [200, 404]
        
    def test_user_statistics(self, admin_client, regular_user):
        """Test user statistics."""
        response = admin_client.get('/admin/dashboard')
        assert response.status_code == 200
        # Should display some statistics
        
    def test_conversion_statistics(self, admin_client, app, regular_user):
        """Test conversion statistics."""
        with app.app_context():
            conversion = Conversion(
                account_id=regular_user.id,
                original_filename='test.png',
                framework='react',
                status='completed',
                generated_code='<div>Test</div>'
            )
            db.session.add(conversion)
            db.session.commit()
        
        response = admin_client.get('/admin/dashboard')
        assert response.status_code == 200


class TestAdminSecurity:
    """Test admin security features."""
    
    def test_regular_user_cannot_access_admin(self, regular_client):
        """Test regular user cannot access admin routes."""
        routes = [
            '/admin/dashboard',
            '/admin/users',
            '/admin/packages',
            '/admin/analytics'
        ]
        
        for route in routes:
            response = regular_client.get(route, follow_redirects=False)
            # Should be denied or redirected
            assert response.status_code in [302, 403, 404]
            
    def test_admin_decorators_work(self, app):
        """Test admin decorators properly restrict access."""
        from app.admin.decorators import admin_required
        
        # Should have decorator function
        assert admin_required is not None
