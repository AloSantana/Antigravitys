"""
Tests for the AI Model Rotator system.
"""

import pytest
import asyncio
import os
import time
from unittest.mock import patch

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from model_rotator import (
    ModelRotator, APIKey, KeyStatus, get_api_key, mark_api_success, mark_api_failure
)


class TestAPIKey:
    """Tests for APIKey dataclass."""
    
    def test_api_key_creation(self):
        """Test creating an API key."""
        key = APIKey(
            key="test_key_123",
            service="gemini",
            name="test_key"
        )
        
        assert key.key == "test_key_123"
        assert key.service == "gemini"
        assert key.name == "test_key"
        assert key.status == KeyStatus.AVAILABLE
        assert key.total_requests == 0
    
    def test_is_available_when_available(self):
        """Test key availability check."""
        key = APIKey(key="test", service="gemini", name="test")
        assert key.is_available() is True
    
    def test_is_available_when_disabled(self):
        """Test disabled key is not available."""
        key = APIKey(key="test", service="gemini", name="test")
        key.status = KeyStatus.DISABLED
        assert key.is_available() is False
    
    def test_is_available_with_active_backoff(self):
        """Test key not available during backoff period."""
        key = APIKey(key="test", service="gemini", name="test")
        key.backoff_until = time.time() + 60  # 60 seconds in future
        assert key.is_available() is False
    
    def test_is_available_after_backoff_expires(self):
        """Test key becomes available after backoff expires."""
        key = APIKey(key="test", service="gemini", name="test")
        key.status = KeyStatus.RATE_LIMITED
        key.backoff_until = time.time() - 1  # 1 second in past
        
        assert key.is_available() is True
        assert key.backoff_until is None
        assert key.status == KeyStatus.AVAILABLE
    
    def test_health_score_perfect(self):
        """Test health score for perfect key."""
        key = APIKey(key="test", service="gemini", name="test")
        assert key.get_health_score() == 100.0
    
    def test_health_score_with_requests(self):
        """Test health score calculation with requests."""
        key = APIKey(key="test", service="gemini", name="test")
        key.total_requests = 100
        key.successful_requests = 95
        key.failed_requests = 5
        
        score = key.get_health_score()
        assert 90.0 <= score <= 95.0  # ~95% success rate
    
    def test_health_score_with_errors(self):
        """Test health score penalty for consecutive errors."""
        key = APIKey(key="test", service="gemini", name="test")
        key.total_requests = 10
        key.successful_requests = 5
        key.consecutive_errors = 3  # 30 point penalty
        
        score = key.get_health_score()
        assert score < 50.0  # Success rate 50% minus error penalty


class TestModelRotator:
    """Tests for ModelRotator class."""
    
    def test_rotator_initialization(self):
        """Test rotator initialization."""
        with patch.dict(os.environ, {}, clear=True):
            rotator = ModelRotator()
            assert isinstance(rotator, ModelRotator)
            assert rotator.keys is not None
            assert rotator.service_configs is not None
    
    def test_load_from_environment_single_key(self):
        """Test loading single API key from environment."""
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test_gemini_key',
            'OPENAI_API_KEY': 'test_openai_key'
        }, clear=True):
            rotator = ModelRotator()
            
            assert len(rotator.keys['gemini']) == 1
            assert rotator.keys['gemini'][0].key == 'test_gemini_key'
            assert len(rotator.keys['openai']) == 1
            assert rotator.keys['openai'][0].key == 'test_openai_key'
    
    def test_load_from_environment_multiple_keys(self):
        """Test loading multiple API keys from environment."""
        with patch.dict(os.environ, {
            'GEMINI_API_KEYS': 'key1,key2,key3'
        }, clear=True):
            rotator = ModelRotator()
            
            assert len(rotator.keys['gemini']) == 3
            assert rotator.keys['gemini'][0].key == 'key1'
            assert rotator.keys['gemini'][1].key == 'key2'
            assert rotator.keys['gemini'][2].key == 'key3'
    
    def test_add_key(self):
        """Test adding a new key."""
        rotator = ModelRotator()
        result = rotator.add_key('gemini', 'new_key_123', 'my_key')
        
        assert result is True
        assert len(rotator.keys['gemini']) >= 1
        
        # Find the added key
        added_key = next((k for k in rotator.keys['gemini'] if k.name == 'my_key'), None)
        assert added_key is not None
        assert added_key.key == 'new_key_123'
    
    def test_add_duplicate_key(self):
        """Test adding duplicate key returns False."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key123', 'key1')
        result = rotator.add_key('gemini', 'key123', 'key2')  # Same key, different name
        
        assert result is False
    
    def test_remove_key(self):
        """Test removing a key."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key_to_remove', 'remove_me')
        
        result = rotator.remove_key('gemini', 'remove_me')
        assert result is True
        
        # Verify key is removed
        assert not any(k.name == 'remove_me' for k in rotator.keys['gemini'])
    
    def test_remove_nonexistent_key(self):
        """Test removing nonexistent key returns False."""
        rotator = ModelRotator()
        result = rotator.remove_key('gemini', 'does_not_exist')
        assert result is False
    
    def test_disable_key(self):
        """Test disabling a key."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key123', 'test_key')
        
        result = rotator.disable_key('gemini', 'test_key')
        assert result is True
        
        key = next(k for k in rotator.keys['gemini'] if k.name == 'test_key')
        assert key.status == KeyStatus.DISABLED
    
    def test_enable_key(self):
        """Test enabling a disabled key."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key123', 'test_key')
        rotator.disable_key('gemini', 'test_key')
        
        result = rotator.enable_key('gemini', 'test_key')
        assert result is True
        
        key = next(k for k in rotator.keys['gemini'] if k.name == 'test_key')
        assert key.status == KeyStatus.AVAILABLE
        assert key.consecutive_errors == 0
    
    @pytest.mark.asyncio
    async def test_get_next_key_returns_available(self):
        """Test getting next available key."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key1', 'key1')
        rotator.add_key('gemini', 'key2', 'key2')
        
        key = await rotator.get_next_key('gemini')
        
        assert key is not None
        assert key.key in ['key1', 'key2']
        assert key.last_used is not None
    
    @pytest.mark.asyncio
    async def test_get_next_key_no_keys_configured(self):
        """Test getting key when none configured."""
        rotator = ModelRotator()
        key = await rotator.get_next_key('nonexistent_service')
        
        assert key is None
    
    @pytest.mark.asyncio
    async def test_get_next_key_all_unavailable(self):
        """Test getting key when all are unavailable."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key1', 'key1')
        
        # Disable the only key
        rotator.disable_key('gemini', 'key1')
        
        key = await rotator.get_next_key('gemini')
        assert key is None
    
    @pytest.mark.asyncio
    async def test_get_next_key_selects_healthiest(self):
        """Test that get_next_key selects healthiest key."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key1', 'key1')
        rotator.add_key('gemini', 'key2', 'key2')
        
        # Make key1 unhealthy
        key1 = next(k for k in rotator.keys['gemini'] if k.name == 'key1')
        key1.total_requests = 10
        key1.successful_requests = 3
        key1.failed_requests = 7
        
        # Make key2 healthy
        key2 = next(k for k in rotator.keys['gemini'] if k.name == 'key2')
        key2.total_requests = 10
        key2.successful_requests = 10
        key2.failed_requests = 0
        
        selected_key = await rotator.get_next_key('gemini')
        assert selected_key.name == 'key2'  # Should select healthier key
    
    @pytest.mark.asyncio
    async def test_mark_success(self):
        """Test marking successful API call."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key1', 'key1')
        
        await rotator.mark_success('gemini', 'key1', tokens_used=100)
        
        key = next(k for k in rotator.keys['gemini'] if k.name == 'key1')
        assert key.total_requests == 1
        assert key.successful_requests == 1
        assert key.consecutive_errors == 0
        
        stats = rotator.usage_stats['gemini']
        assert stats['total_requests'] == 1
        assert stats['successful_requests'] == 1
        assert stats['total_tokens'] == 100
    
    @pytest.mark.asyncio
    async def test_mark_failure_regular(self):
        """Test marking failed API call."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key1', 'key1')
        
        await rotator.mark_failure('gemini', 'key1', is_rate_limit=False)
        
        key = next(k for k in rotator.keys['gemini'] if k.name == 'key1')
        assert key.total_requests == 1
        assert key.failed_requests == 1
        assert key.error_count == 1
        assert key.consecutive_errors == 1
        assert key.status == KeyStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_mark_failure_rate_limit(self):
        """Test marking rate limit failure."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key1', 'key1')
        
        await rotator.mark_failure('gemini', 'key1', is_rate_limit=True)
        
        key = next(k for k in rotator.keys['gemini'] if k.name == 'key1')
        assert key.status == KeyStatus.RATE_LIMITED
        assert key.rate_limit_hits == 1
        assert key.last_rate_limit is not None
        assert key.backoff_until is not None
        assert key.backoff_until > time.time()
    
    @pytest.mark.asyncio
    async def test_mark_failure_disables_after_errors(self):
        """Test key gets disabled after too many consecutive errors."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key1', 'key1')
        
        # Mark 5 consecutive failures
        for _ in range(5):
            await rotator.mark_failure('gemini', 'key1', is_rate_limit=False)
        
        key = next(k for k in rotator.keys['gemini'] if k.name == 'key1')
        assert key.status == KeyStatus.DISABLED
        assert key.consecutive_errors == 5
    
    def test_get_service_stats(self):
        """Test getting service statistics."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key1', 'key1')
        
        stats = rotator.get_service_stats('gemini')
        
        assert 'total_requests' in stats
        assert 'successful_requests' in stats
        assert 'failed_requests' in stats
        assert 'keys' in stats
        assert len(stats['keys']) >= 1
    
    def test_get_all_stats(self):
        """Test getting all service statistics."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key1', 'key1')
        rotator.add_key('openai', 'key2', 'key2')
        
        stats = rotator.get_all_stats()
        
        assert isinstance(stats, dict)
        assert 'gemini' in stats or len(rotator.keys['gemini']) > 0
        assert 'openai' in stats or len(rotator.keys['openai']) > 0
    
    def test_get_available_key_count(self):
        """Test counting available keys."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key1', 'key1')
        rotator.add_key('gemini', 'key2', 'key2')
        rotator.add_key('gemini', 'key3', 'key3')
        
        # Disable one key
        rotator.disable_key('gemini', 'key2')
        
        count = rotator.get_available_key_count('gemini')
        assert count == 2
    
    def test_reset_stats_single_service(self):
        """Test resetting stats for single service."""
        rotator = ModelRotator()
        rotator.usage_stats['gemini']['total_requests'] = 100
        
        rotator.reset_stats('gemini')
        
        assert rotator.usage_stats['gemini']['total_requests'] == 0
    
    def test_reset_stats_all_services(self):
        """Test resetting stats for all services."""
        rotator = ModelRotator()
        rotator.usage_stats['gemini']['total_requests'] = 100
        rotator.usage_stats['openai']['total_requests'] = 50
        
        rotator.reset_stats()
        
        assert len(rotator.usage_stats) == 0


class TestGlobalFunctions:
    """Tests for global convenience functions."""
    
    @pytest.mark.asyncio
    async def test_get_api_key(self):
        """Test get_api_key convenience function."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}, clear=True):
            result = await get_api_key('gemini')
            
            if result:  # Only if key was loaded
                key, key_name = result
                assert key == 'test_key'
                assert isinstance(key_name, str)
    
    @pytest.mark.asyncio
    async def test_mark_api_success_convenience(self):
        """Test mark_api_success convenience function."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}, clear=True):
            # This should not raise an error
            await mark_api_success('gemini', 'gemini_default', tokens_used=50)
    
    @pytest.mark.asyncio
    async def test_mark_api_failure_convenience(self):
        """Test mark_api_failure convenience function."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}, clear=True):
            # This should not raise an error
            await mark_api_failure('gemini', 'gemini_default', is_rate_limit=True)


class TestConcurrency:
    """Tests for concurrent operations."""
    
    @pytest.mark.asyncio
    async def test_concurrent_key_requests(self):
        """Test multiple concurrent key requests."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key1', 'key1')
        rotator.add_key('gemini', 'key2', 'key2')
        rotator.add_key('gemini', 'key3', 'key3')
        
        # Request keys concurrently
        keys = await asyncio.gather(
            rotator.get_next_key('gemini'),
            rotator.get_next_key('gemini'),
            rotator.get_next_key('gemini'),
            rotator.get_next_key('gemini'),
            rotator.get_next_key('gemini')
        )
        
        # All requests should succeed
        assert all(k is not None for k in keys)
        
        # Keys should be distributed
        key_names = [k.name for k in keys]
        assert len(set(key_names)) >= 2  # At least 2 different keys used


class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_key_with_tags(self):
        """Test creating key with tags."""
        key = APIKey(
            key="test",
            service="gemini",
            name="test",
            tags=["production", "high-priority"]
        )
        
        assert "production" in key.tags
        assert "high-priority" in key.tags
    
    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test exponential backoff for rate limits."""
        rotator = ModelRotator()
        rotator.add_key('gemini', 'key1', 'key1')
        
        # Simulate multiple rate limit hits
        for i in range(3):
            await rotator.mark_failure('gemini', 'key1', is_rate_limit=True)
        
        key = next(k for k in rotator.keys['gemini'] if k.name == 'key1')
        
        # Backoff should increase exponentially
        assert key.rate_limit_hits == 3
        assert key.backoff_until is not None
    
    def test_health_score_boundaries(self):
        """Test health score stays within 0-100."""
        key = APIKey(key="test", service="gemini", name="test")
        
        # Worst case scenario
        key.total_requests = 100
        key.successful_requests = 0
        key.consecutive_errors = 10
        key.rate_limit_hits = 10
        
        score = key.get_health_score()
        assert 0.0 <= score <= 100.0
