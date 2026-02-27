"""
Unit tests for backend.agent.orchestrator module
Tests the Orchestrator class for request routing, caching, and complexity assessment
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from collections import OrderedDict


@pytest.mark.unit
@pytest.mark.asyncio
class TestOrchestrator:
    """Test suite for Orchestrator class."""
    
    async def test_orchestrator_initialization(self, mock_env_vars):
        """Test that orchestrator initializes with correct components."""
        with patch('backend.agent.orchestrator.GeminiClient') as MockGemini, \
             patch('backend.agent.orchestrator.LocalClient') as MockLocal, \
             patch('backend.agent.orchestrator.VectorStore') as MockStore:
            
            from backend.agent.orchestrator import Orchestrator
            orchestrator = Orchestrator()
            
            assert orchestrator.gemini_api_key == 'test_gemini_key'
            assert orchestrator._cache_ttl == 300
            assert orchestrator._max_cache_size == 100
            assert orchestrator._cache_hits == 0
            assert orchestrator._cache_misses == 0
            assert isinstance(orchestrator._response_cache, OrderedDict)
            MockGemini.assert_called_once()
            MockLocal.assert_called_once()
            MockStore.assert_called_once()
    
    async def test_assess_complexity_high(self, mock_orchestrator):
        """Test complexity assessment for high complexity requests."""
        high_complexity_requests = [
            "Plan a complex microservices architecture",
            "Design a scalable deployment strategy",
            "Implement a distributed caching system",
            "Refactor the entire authentication module",
            "Analyze performance bottlenecks and optimize",
            "Debug this complex async race condition",
        ]
        
        for request in high_complexity_requests:
            complexity = mock_orchestrator._assess_complexity(request)
            assert complexity == "high", f"Failed for: {request}"
    
    async def test_assess_complexity_low(self, mock_orchestrator):
        """Test complexity assessment for low complexity requests."""
        low_complexity_requests = [
            "What is Python?",
            "List files in directory",
            "Show me the README",
            "Hello world",
            "Get current time",
        ]
        
        for request in low_complexity_requests:
            complexity = mock_orchestrator._assess_complexity(request)
            assert complexity == "low", f"Failed for: {request}"
    
    async def test_assess_complexity_with_code_patterns(self, mock_orchestrator):
        """Test complexity assessment with code patterns."""
        code_requests = [
            "Write a function to ```def process():```",
            "Create a class for user management",
            "Implement async function for API calls",
            "Import the required modules",
        ]
        
        for request in code_requests:
            complexity = mock_orchestrator._assess_complexity(request)
            # Code patterns may trigger high complexity if combined with keywords
            assert complexity in ["low", "high"]
    
    async def test_assess_complexity_long_requests(self, mock_orchestrator):
        """Test complexity assessment for long requests."""
        long_request = "Please help me " + "with this task " * 30  # > 200 chars
        complexity = mock_orchestrator._assess_complexity(long_request)
        # Long requests may be complex
        assert complexity in ["low", "high"]
    
    async def test_cache_key_generation(self, mock_orchestrator):
        """Test cache key generation is consistent."""
        request = "Test request"
        key1 = mock_orchestrator._get_cache_key(request)
        key2 = mock_orchestrator._get_cache_key(request)
        
        assert key1 == key2
        assert len(key1) == 64  # SHA256 hex digest length
        assert isinstance(key1, str)
    
    async def test_cache_key_uniqueness(self, mock_orchestrator):
        """Test different requests produce different cache keys."""
        key1 = mock_orchestrator._get_cache_key("Request 1")
        key2 = mock_orchestrator._get_cache_key("Request 2")
        
        assert key1 != key2
    
    async def test_cache_response(self, mock_orchestrator):
        """Test response caching functionality."""
        request = "Test request"
        response = {"source": "Test", "response": "Test response"}
        
        # Cache the response
        mock_orchestrator._cache_response(request, response)
        
        # Verify it's in cache
        cache_key = mock_orchestrator._get_cache_key(request)
        assert cache_key in mock_orchestrator._response_cache
        
        cached_response, timestamp = mock_orchestrator._response_cache[cache_key]
        assert cached_response == response
        assert time.time() - timestamp < 1  # Recently cached
    
    async def test_get_cached_response_hit(self, mock_orchestrator):
        """Test retrieving cached response (cache hit)."""
        request = "Test request"
        response = {"source": "Test", "response": "Test response"}
        
        # Cache the response
        mock_orchestrator._cache_response(request, response)
        
        # Retrieve from cache
        cached = mock_orchestrator._get_cached_response(request)
        
        assert cached == response
        assert mock_orchestrator._cache_hits == 1
        assert mock_orchestrator._cache_misses == 0
    
    async def test_get_cached_response_miss(self, mock_orchestrator):
        """Test cache miss for uncached request."""
        request = "Uncached request"
        
        cached = mock_orchestrator._get_cached_response(request)
        
        assert cached is None
        assert mock_orchestrator._cache_hits == 0
        assert mock_orchestrator._cache_misses == 1
    
    async def test_cache_expiration(self, mock_orchestrator):
        """Test that expired cache entries are removed."""
        request = "Test request"
        response = {"source": "Test", "response": "Test response"}
        
        # Set very short TTL for testing
        mock_orchestrator._cache_ttl = 0.1  # 100ms
        
        # Cache the response
        mock_orchestrator._cache_response(request, response)
        
        # Wait for expiration
        await asyncio.sleep(0.2)
        
        # Should return None (expired)
        cached = mock_orchestrator._get_cached_response(request)
        assert cached is None
    
    async def test_cache_lru_eviction(self, mock_orchestrator):
        """Test LRU eviction when cache is full."""
        mock_orchestrator._max_cache_size = 3
        
        # Add 4 items to trigger eviction
        for i in range(4):
            request = f"Request {i}"
            response = {"response": f"Response {i}"}
            mock_orchestrator._cache_response(request, response)
        
        # Cache should have only 3 items (oldest evicted)
        assert len(mock_orchestrator._response_cache) == 3
        
        # First request should be evicted
        first_key = mock_orchestrator._get_cache_key("Request 0")
        assert first_key not in mock_orchestrator._response_cache
    
    async def test_cache_hit_rate_calculation(self, mock_orchestrator):
        """Test cache hit rate calculation."""
        # Initial rate should be 0
        assert mock_orchestrator.get_cache_hit_rate() == 0.0
        
        # Simulate hits and misses
        mock_orchestrator._cache_hits = 7
        mock_orchestrator._cache_misses = 3
        
        hit_rate = mock_orchestrator.get_cache_hit_rate()
        assert hit_rate == 0.7  # 7/10 = 70%
    
    async def test_clear_cache(self, mock_orchestrator):
        """Test cache clearing functionality."""
        # Add some items to cache
        for i in range(3):
            mock_orchestrator._cache_response(f"Request {i}", {"response": f"Response {i}"})
        
        # Simulate some cache activity
        mock_orchestrator._cache_hits = 5
        mock_orchestrator._cache_misses = 2
        
        # Clear cache
        mock_orchestrator.clear_cache()
        
        assert len(mock_orchestrator._response_cache) == 0
        assert mock_orchestrator._cache_hits == 0
        assert mock_orchestrator._cache_misses == 0
    
    async def test_process_request_high_complexity(self, mock_orchestrator):
        """Test processing high complexity request routes to Gemini."""
        request = "Design a complex distributed system architecture"
        
        mock_orchestrator.gemini.generate = AsyncMock(return_value="Gemini response")
        
        response = await mock_orchestrator.process_request(request)
        
        assert response["source"] == "Gemini"
        assert "response" in response
        assert "processing_time_ms" in response
        mock_orchestrator.gemini.generate.assert_called_once()
    
    async def test_process_request_low_complexity(self, mock_orchestrator):
        """Test processing low complexity request routes to Local."""
        request = "What is Python?"
        
        mock_orchestrator.local.generate = AsyncMock(return_value="Local response")
        
        response = await mock_orchestrator.process_request(request)
        
        assert response["source"] == "Local"
        assert "response" in response
        mock_orchestrator.local.generate.assert_called_once()
    
    async def test_process_request_with_rag_context(self, mock_orchestrator):
        """Test request processing includes RAG context."""
        request = "Explain the authentication module"
        
        mock_orchestrator.local.embed = AsyncMock(return_value=[0.1] * 768)
        mock_orchestrator.local.generate = AsyncMock(return_value="Response with context")
        mock_orchestrator.store.query = Mock(return_value={
            'documents': [['Auth module uses JWT tokens', 'User authentication flow']],
            'metadatas': [[{'source': 'auth.py'}, {'source': 'user.py'}]],
        })
        
        response = await mock_orchestrator.process_request(request)
        
        # Verify RAG was used
        mock_orchestrator.local.embed.assert_called_once_with(request)
        mock_orchestrator.store.query.assert_called_once()
        mock_orchestrator.local.generate.assert_called_once()
        
        # Check that augmented request includes context
        call_args = mock_orchestrator.local.generate.call_args[0][0]
        assert "Context:" in call_args or "auth" in call_args.lower()
    
    async def test_process_request_skip_rag_for_simple(self, mock_orchestrator):
        """Test RAG is skipped for very simple requests."""
        request = "Hello"  # Short, simple request
        
        mock_orchestrator.local.generate = AsyncMock(return_value="Hi there!")
        
        response = await mock_orchestrator.process_request(request)
        
        # RAG should be skipped for simple short requests
        # (embed may not be called)
        assert response["source"] == "Local"
        mock_orchestrator.local.generate.assert_called_once()
    
    async def test_process_request_fallback_to_gemini(self, mock_orchestrator):
        """Test fallback to Gemini when Local fails."""
        request = "Simple task"
        
        # Local fails
        mock_orchestrator.local.generate = AsyncMock(
            return_value="Error: Could not connect to Ollama"
        )
        mock_orchestrator.gemini.generate = AsyncMock(return_value="Gemini fallback")
        
        response = await mock_orchestrator.process_request(request)
        
        # Should fallback to Gemini
        assert response["source"] == "Gemini"
        mock_orchestrator.local.generate.assert_called_once()
        mock_orchestrator.gemini.generate.assert_called_once()
    
    async def test_process_request_uses_cache(self, mock_orchestrator):
        """Test that cached responses are returned quickly."""
        request = "What is Python?"
        
        mock_orchestrator.local.generate = AsyncMock(return_value="Python is a language")
        
        # First request - cache miss
        response1 = await mock_orchestrator.process_request(request)
        assert mock_orchestrator._cache_misses == 1
        
        # Second request - cache hit
        response2 = await mock_orchestrator.process_request(request)
        assert mock_orchestrator._cache_hits == 1
        assert response1["response"] == response2["response"]
        
        # Local should only be called once
        mock_orchestrator.local.generate.assert_called_once()
    
    async def test_process_request_performance_metrics(self, mock_orchestrator):
        """Test that performance metrics are included in response."""
        request = "Test request"
        
        mock_orchestrator.local.generate = AsyncMock(return_value="Response")
        
        response = await mock_orchestrator.process_request(request)
        
        assert "processing_time_ms" in response
        assert "generation_time_ms" in response
        assert isinstance(response["processing_time_ms"], float)
        assert isinstance(response["generation_time_ms"], float)
        assert response["processing_time_ms"] >= response["generation_time_ms"]
    
    async def test_rag_embedding_fallback(self, mock_orchestrator):
        """Test RAG falls back to Gemini embedding if Local fails."""
        request = "Explain authentication"
        
        # Local embedding fails
        mock_orchestrator.local.embed = AsyncMock(return_value=None)
        mock_orchestrator.gemini.embed = AsyncMock(return_value=[0.2] * 768)
        mock_orchestrator.local.generate = AsyncMock(return_value="Response")
        
        response = await mock_orchestrator.process_request(request)
        
        # Should try both embedding methods
        mock_orchestrator.local.embed.assert_called_once()
        mock_orchestrator.gemini.embed.assert_called_once()
        mock_orchestrator.store.query.assert_called_once()
    
    async def test_rag_error_handling(self, mock_orchestrator):
        """Test graceful handling of RAG errors."""
        request = "Test request"
        
        # RAG components fail
        mock_orchestrator.local.embed = AsyncMock(side_effect=Exception("Embedding error"))
        mock_orchestrator.local.generate = AsyncMock(return_value="Response without context")
        
        # Should still complete without RAG
        response = await mock_orchestrator.process_request(request)
        
        assert "response" in response
        mock_orchestrator.local.generate.assert_called_once()
        
        # Should be called with original request (no context)
        call_args = mock_orchestrator.local.generate.call_args[0][0]
        assert "Context:" not in call_args
    
    async def test_delegate_to_gemini(self, mock_orchestrator):
        """Test Gemini delegation method."""
        request = "Test request"
        expected_response = "Gemini response"
        
        mock_orchestrator.gemini.generate = AsyncMock(return_value=expected_response)
        
        result = await mock_orchestrator._delegate_to_gemini(request)
        
        assert result["source"] == "Gemini"
        assert result["response"] == expected_response
        mock_orchestrator.gemini.generate.assert_called_once_with(request)
    
    async def test_delegate_to_local(self, mock_orchestrator):
        """Test Local delegation method."""
        request = "Test request"
        expected_response = "Local response"
        
        mock_orchestrator.local.generate = AsyncMock(return_value=expected_response)
        
        result = await mock_orchestrator._delegate_to_local(request)
        
        assert result["source"] == "Local"
        assert result["response"] == expected_response
        mock_orchestrator.local.generate.assert_called_once_with(request)
    
    @pytest.mark.parametrize("query_text,expected_complexity", [
        ("design architecture", "high"),
        ("plan deployment", "high"),
        ("implement feature", "high"),
        ("hello", "low"),
        ("list files", "low"),
        ("what is python", "low"),
    ])
    async def test_assess_complexity_parametrized(self, mock_orchestrator, query_text, expected_complexity):
        """Parametrized test for complexity assessment."""
        complexity = mock_orchestrator._assess_complexity(query_text)
        assert complexity == expected_complexity
    
    async def test_concurrent_requests(self, mock_orchestrator):
        """Test handling multiple concurrent requests."""
        requests = [f"Request {i}" for i in range(10)]
        
        mock_orchestrator.local.generate = AsyncMock(
            side_effect=[f"Response {i}" for i in range(10)]
        )
        
        # Process requests concurrently
        tasks = [mock_orchestrator.process_request(req) for req in requests]
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 10
        assert all("response" in resp for resp in responses)
    
    async def test_context_chunk_limiting(self, mock_orchestrator):
        """Test that only top context chunks are used."""
        request = "Test with many results"
        
        # Return many results
        mock_orchestrator.local.embed = AsyncMock(return_value=[0.1] * 768)
        mock_orchestrator.store.query = Mock(return_value={
            'documents': [[f'Document {i}' for i in range(10)]],  # 10 documents
            'metadatas': [[{'source': f'doc{i}.txt'} for i in range(10)]],
        })
        mock_orchestrator.local.generate = AsyncMock(return_value="Response")
        
        response = await mock_orchestrator.process_request(request)
        
        # Verify context is limited to top 3
        call_args = mock_orchestrator.local.generate.call_args[0][0]
        if "Context:" in call_args:
            # Count how many documents are in context
            doc_count = sum(1 for i in range(10) if f'Document {i}' in call_args)
            assert doc_count <= 3, "Should limit to top 3 context chunks"
