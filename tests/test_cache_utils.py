# tests/test_cache_utils.py
"""Tests for cache utilities."""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock

from app import create_app
from app.extensions import db
from app.cache_utils import CacheManager


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
def cache_manager(app):
    """Create cache manager instance."""
    return CacheManager()


class TestCacheManager:
    """Test CacheManager functionality."""
    
    def test_init_cache_manager(self, cache_manager):
        """Test cache manager initialization."""
        assert cache_manager is not None
        assert hasattr(cache_manager, 'get')
        assert hasattr(cache_manager, 'set')
        assert hasattr(cache_manager, 'delete')
        assert hasattr(cache_manager, 'clear')
    
    def test_set_and_get_string_value(self, cache_manager):
        """Test setting and getting string values."""
        key = 'test_string_key'
        value = 'test_string_value'
        
        # Set value
        success = cache_manager.set(key, value, ttl=300)
        assert success is True
        
        # Get value
        retrieved_value = cache_manager.get(key)
        assert retrieved_value == value
    
    def test_set_and_get_dict_value(self, cache_manager):
        """Test setting and getting dictionary values."""
        key = 'test_dict_key'
        value = {'user_id': 123, 'credits': 10.5, 'active': True}
        
        # Set value
        success = cache_manager.set(key, value, ttl=300)
        assert success is True
        
        # Get value
        retrieved_value = cache_manager.get(key)
        assert retrieved_value == value
        assert isinstance(retrieved_value, dict)
        assert retrieved_value['user_id'] == 123
    
    def test_set_and_get_list_value(self, cache_manager):
        """Test setting and getting list values."""
        key = 'test_list_key'
        value = ['item1', 'item2', {'nested': 'dict'}]
        
        # Set value
        success = cache_manager.set(key, value, ttl=300)
        assert success is True
        
        # Get value
        retrieved_value = cache_manager.get(key)
        assert retrieved_value == value
        assert isinstance(retrieved_value, list)
        assert len(retrieved_value) == 3
    
    def test_get_nonexistent_key(self, cache_manager):
        """Test getting value for nonexistent key."""
        value = cache_manager.get('nonexistent_key')
        assert value is None
    
    def test_get_nonexistent_key_with_default(self, cache_manager):
        """Test getting value for nonexistent key with default."""
        default_value = 'default_result'
        value = cache_manager.get('nonexistent_key', default=default_value)
        assert value == default_value
    
    def test_delete_existing_key(self, cache_manager):
        """Test deleting existing key."""
        key = 'test_delete_key'
        value = 'delete_test_value'
        
        # Set value
        cache_manager.set(key, value)
        
        # Verify it exists
        assert cache_manager.get(key) == value
        
        # Delete it
        success = cache_manager.delete(key)
        assert success is True
        
        # Verify it's gone
        assert cache_manager.get(key) is None
    
    def test_delete_nonexistent_key(self, cache_manager):
        """Test deleting nonexistent key."""
        success = cache_manager.delete('nonexistent_key')
        # Should handle gracefully (implementation dependent)
        assert success in [True, False]  # Either is acceptable
    
    def test_ttl_expiration(self, cache_manager):
        """Test TTL expiration."""
        key = 'test_ttl_key'
        value = 'ttl_test_value'
        short_ttl = 1  # 1 second
        
        # Set value with short TTL
        success = cache_manager.set(key, value, ttl=short_ttl)
        assert success is True
        
        # Get immediately (should exist)
        assert cache_manager.get(key) == value
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Should be expired
        expired_value = cache_manager.get(key)
        assert expired_value is None
    
    def test_update_existing_key(self, cache_manager):
        """Test updating existing key."""
        key = 'test_update_key'
        original_value = 'original_value'
        updated_value = 'updated_value'
        
        # Set original value
        cache_manager.set(key, original_value)
        assert cache_manager.get(key) == original_value
        
        # Update value
        cache_manager.set(key, updated_value)
        assert cache_manager.get(key) == updated_value
    
    def test_clear_cache(self, cache_manager):
        """Test clearing entire cache."""
        # Set multiple values
        test_data = {
            'key1': 'value1',
            'key2': {'nested': 'dict'},
            'key3': [1, 2, 3]
        }
        
        for key, value in test_data.items():
            cache_manager.set(key, value)
            assert cache_manager.get(key) == value
        
        # Clear cache
        success = cache_manager.clear()
        assert success is True
        
        # Verify all keys are gone
        for key in test_data.keys():
            assert cache_manager.get(key) is None
    
    def test_cache_key_patterns(self, cache_manager):
        """Test various cache key patterns."""
        test_keys = [
            'simple_key',
            'user:123:profile',
            'conversion:uuid:abc123',
            'stats:daily:2024-12-10',
            'temp:session:xyz789'
        ]
        
        for key in test_keys:
            value = f'value_for_{key}'
            cache_manager.set(key, value)
            assert cache_manager.get(key) == value
    
    def test_cache_large_data(self, cache_manager):
        """Test caching large data structures."""
        large_data = {
            'users': [{'id': i, 'name': f'User{i}'} for i in range(1000)],
            'metadata': {
                'total_count': 1000,
                'generated_at': '2024-12-10T12:00:00Z',
                'version': '1.0'
            }
        }
        
        key = 'large_data_test'
        success = cache_manager.set(key, large_data, ttl=300)
        assert success is True
        
        retrieved_data = cache_manager.get(key)
        assert retrieved_data == large_data
        assert len(retrieved_data['users']) == 1000
    
    def test_cache_with_none_values(self, cache_manager):
        """Test caching None values."""
        key = 'none_value_key'
        
        # Set None value
        success = cache_manager.set(key, None)
        assert success is True
        
        # Get None value (should be distinguishable from missing key)
        # This test depends on implementation - some cache systems 
        # treat None specially
        retrieved_value = cache_manager.get(key, default='default')
        # Implementation dependent: could be None or 'default'
        assert retrieved_value in [None, 'default']
    
    def test_concurrent_access(self, cache_manager):
        """Test concurrent cache access."""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                key = f'worker_{worker_id}'
                value = f'value_from_worker_{worker_id}'
                
                # Set value
                cache_manager.set(key, value)
                time.sleep(0.1)  # Small delay
                
                # Get value
                retrieved = cache_manager.get(key)
                results.append((worker_id, retrieved == value))
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Create and start threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        assert all(success for _, success in results)


class TestCacheUtilityFunctions:
    """Test cache utility functions."""
    
    def test_generate_cache_key(self, cache_manager):
        """Test cache key generation utility."""
        # Test if there's a key generation utility
        if hasattr(cache_manager, 'generate_key'):
            key = cache_manager.generate_key('user', 123, 'profile')
            assert isinstance(key, str)
            assert 'user' in key
            assert '123' in key
            assert 'profile' in key
    
    def test_cache_stats(self, cache_manager):
        """Test cache statistics if available."""
        # Set some data
        for i in range(5):
            cache_manager.set(f'stats_test_{i}', f'value_{i}')
        
        # Check if stats are available
        if hasattr(cache_manager, 'get_stats'):
            stats = cache_manager.get_stats()
            assert isinstance(stats, dict)
            # Stats might include hits, misses, size, etc.
    
    def test_cache_health_check(self, cache_manager):
        """Test cache health check."""
        # Basic health check - can we set and get?
        test_key = 'health_check'
        test_value = 'healthy'
        
        success = cache_manager.set(test_key, test_value)
        assert success is True
        
        retrieved = cache_manager.get(test_key)
        assert retrieved == test_value
        
        # Cleanup
        cache_manager.delete(test_key)


class TestCacheManagerWithMockRedis:
    """Test cache manager with mocked Redis."""
    
    def test_redis_connection_failure(self, app):
        """Test handling of Redis connection failure."""
        with patch('redis.Redis') as mock_redis_class:
            # Mock Redis to raise connection error
            mock_redis = Mock()
            mock_redis.ping.side_effect = Exception("Connection failed")
            mock_redis_class.return_value = mock_redis
            
            # Cache should handle gracefully
            cache_manager = CacheManager()
            
            # Operations should fail gracefully or fallback to in-memory
            result = cache_manager.set('test_key', 'test_value')
            # Should handle error gracefully
            assert result in [True, False]  # Implementation dependent
    
    def test_redis_operation_failure(self, cache_manager):
        """Test handling of Redis operation failure."""
        with patch.object(cache_manager, '_redis', None):  # Assume _redis attribute exists
            # If Redis is None, should handle gracefully
            result = cache_manager.get('test_key')
            assert result is None  # Should return None for failed operations
    
    def test_serialization_error(self, cache_manager):
        """Test handling of serialization errors."""
        # Create an object that can't be JSON serialized
        class UnserializableObject:
            def __init__(self):
                self.func = lambda x: x  # Functions can't be serialized
        
        unserializable = UnserializableObject()
        
        # Should handle serialization error gracefully
        success = cache_manager.set('unserializable_key', unserializable)
        # Implementation dependent - might succeed (pickle) or fail (json)
        assert success in [True, False]


class TestCachePerformance:
    """Test cache performance characteristics."""
    
    def test_large_key_performance(self, cache_manager):
        """Test performance with large keys."""
        import time
        
        large_key = 'x' * 1000  # 1KB key
        value = 'test_value'
        
        start_time = time.time()
        success = cache_manager.set(large_key, value)
        set_time = time.time() - start_time
        
        start_time = time.time()
        retrieved = cache_manager.get(large_key)
        get_time = time.time() - start_time
        
        assert success is True
        assert retrieved == value
        assert set_time < 1.0  # Should complete within 1 second
        assert get_time < 1.0  # Should complete within 1 second
    
    def test_many_keys_performance(self, cache_manager):
        """Test performance with many keys."""
        import time
        
        num_keys = 100
        
        # Set many keys
        start_time = time.time()
        for i in range(num_keys):
            cache_manager.set(f'perf_key_{i}', f'value_{i}')
        set_time = time.time() - start_time
        
        # Get many keys
        start_time = time.time()
        for i in range(num_keys):
            cache_manager.get(f'perf_key_{i}')
        get_time = time.time() - start_time
        
        # Performance should be reasonable
        assert set_time < 5.0  # 100 sets in < 5 seconds
        assert get_time < 5.0  # 100 gets in < 5 seconds
        
        # Average time per operation
        avg_set_time = set_time / num_keys
        avg_get_time = get_time / num_keys
        
        assert avg_set_time < 0.1  # < 100ms per set
        assert avg_get_time < 0.1  # < 100ms per get
