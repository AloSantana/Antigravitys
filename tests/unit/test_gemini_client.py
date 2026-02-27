"""
Unit tests for backend.agent.gemini_client module
Tests the GeminiClient class for Google Gemini API integration
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch


@pytest.mark.unit
@pytest.mark.asyncio
class TestGeminiClient:
    """Test suite for GeminiClient class."""
    
    def test_client_initialization_with_api_key(self):
        """Test GeminiClient initializes correctly with API key."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            api_key = os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod")
            client = GeminiClient(api_key=api_key)
            
            mock_genai.configure.assert_called_once_with(api_key="test_api_key")
            mock_genai.GenerativeModel.assert_called_once_with('gemini-pro')
            assert client.embed_model == "models/embedding-001"
            assert client._min_request_interval == 0.1
    
    def test_client_initialization_without_api_key(self):
        """Test GeminiClient initialization without API key."""
        from backend.agent.gemini_client import GeminiClient
        
        client = GeminiClient(api_key="")
        
        assert client.model is None
        assert client.embed_model is None
    
    def test_client_initialization_none_api_key(self):
        """Test GeminiClient initialization with None API key."""
        from backend.agent.gemini_client import GeminiClient
        
        client = GeminiClient(api_key=None)
        
        assert client.model is None
        assert client.embed_model is None
    
    async def test_generate_success(self):
        """Test successful text generation."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            # Setup mock
            mock_response = Mock()
            mock_response.text = "Generated text from Gemini"
            mock_model = Mock()
            mock_model.generate_content = Mock(return_value=mock_response)
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            result = await client.generate("Test prompt")
            
            assert result == "Generated text from Gemini"
            mock_model.generate_content.assert_called_once_with("Test prompt")
    
    async def test_generate_without_api_key(self):
        """Test generation without API key returns error."""
        from backend.agent.gemini_client import GeminiClient
        
        client = GeminiClient(api_key="")
        result = await client.generate("Test prompt")
        
        assert "Error" in result
        assert "API Key not configured" in result
    
    async def test_generate_quota_exceeded(self):
        """Test handling of quota exceeded errors."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            mock_model = Mock()
            mock_model.generate_content = Mock(
                side_effect=Exception("Quota exceeded for requests")
            )
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            result = await client.generate("Test prompt")
            
            assert "quota" in result.lower()
            assert "API quota exceeded" in result
    
    async def test_generate_invalid_api_key(self):
        """Test handling of invalid API key errors."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            mock_model = Mock()
            mock_model.generate_content = Mock(
                side_effect=Exception("Invalid API key provided")
            )
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient(api_key="invalid_key_do_not_use_in_prod")
            result = await client.generate("Test prompt")
            
            assert "api key" in result.lower()
            assert "Invalid API key" in result
    
    async def test_generate_generic_error(self):
        """Test handling of generic errors."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            mock_model = Mock()
            mock_model.generate_content = Mock(
                side_effect=Exception("Some unexpected error")
            )
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            result = await client.generate("Test prompt")
            
            assert "Error" in result
            assert "Some unexpected error" in result
    
    async def test_rate_limiting(self):
        """Test rate limiting between requests."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            mock_response = Mock()
            mock_response.text = "Response"
            mock_model = Mock()
            mock_model.generate_content = Mock(return_value=mock_response)
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            client._min_request_interval = 0.05  # 50ms for faster test
            
            start = asyncio.get_event_loop().time()
            await client.generate("Request 1")
            await client.generate("Request 2")
            end = asyncio.get_event_loop().time()
            
            elapsed = end - start
            # Should take at least the rate limit interval
            assert elapsed >= client._min_request_interval
    
    async def test_embed_success(self):
        """Test successful embedding generation."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            expected_embedding = [0.1, 0.2, 0.3] * 256
            mock_genai.embed_content = Mock(return_value={'embedding': expected_embedding})
            mock_genai.GenerativeModel.return_value = Mock()
            
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            result = await client.embed("Test text")
            
            assert result == expected_embedding
            mock_genai.embed_content.assert_called_once()
    
    async def test_embed_without_api_key(self):
        """Test embedding without API key returns empty list."""
        from backend.agent.gemini_client import GeminiClient
        
        client = GeminiClient(api_key="")
        result = await client.embed("Test text")
        
        assert result == []
    
    async def test_embed_quota_exceeded(self):
        """Test handling of quota exceeded during embedding."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            mock_genai.embed_content = Mock(
                side_effect=Exception("Quota exceeded for embeddings")
            )
            mock_genai.GenerativeModel.return_value = Mock()
            
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            result = await client.embed("Test text")
            
            assert result == []
    
    async def test_embed_generic_error(self):
        """Test handling of generic errors during embedding."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            mock_genai.embed_content = Mock(
                side_effect=Exception("Network error")
            )
            mock_genai.GenerativeModel.return_value = Mock()
            
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            result = await client.embed("Test text")
            
            assert result == []
    
    async def test_embed_rate_limiting(self):
        """Test rate limiting applies to embedding."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            mock_genai.embed_content = Mock(return_value={'embedding': [0.1]})
            mock_genai.GenerativeModel.return_value = Mock()
            
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            client._min_request_interval = 0.05
            
            start = asyncio.get_event_loop().time()
            await client.embed("Text 1")
            await client.embed("Text 2")
            end = asyncio.get_event_loop().time()
            
            elapsed = end - start
            assert elapsed >= client._min_request_interval
    
    async def test_concurrent_requests_rate_limited(self):
        """Test that concurrent requests are properly rate limited."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            mock_response = Mock()
            mock_response.text = "Response"
            mock_model = Mock()
            mock_model.generate_content = Mock(return_value=mock_response)
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            client._min_request_interval = 0.05
            
            start = asyncio.get_event_loop().time()
            tasks = [client.generate(f"Request {i}") for i in range(3)]
            await asyncio.gather(*tasks)
            end = asyncio.get_event_loop().time()
            
            elapsed = end - start
            # Should take at least 2 intervals (3 requests with intervals between)
            assert elapsed >= client._min_request_interval * 2
    
    async def test_cached_embedding_method(self):
        """Test the cached embedding placeholder method."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            mock_genai.GenerativeModel.return_value = Mock()
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            
            # This is a placeholder that always returns None
            result = client._get_cached_embedding("test_hash")
            assert result is None
    
    @pytest.mark.parametrize("prompt,expected_call", [
        ("Simple prompt", "Simple prompt"),
        ("", ""),
        ("Very " * 100 + "long prompt", "Very " * 100 + "long prompt"),
    ])
    async def test_generate_various_prompts(self, prompt, expected_call):
        """Test generation with various prompt types."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            mock_response = Mock()
            mock_response.text = "Response"
            mock_model = Mock()
            mock_model.generate_content = Mock(return_value=mock_response)
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            await client.generate(prompt)
            
            mock_model.generate_content.assert_called_once_with(expected_call)
    
    async def test_embed_with_task_type(self):
        """Test embedding includes correct task type."""
        with patch('backend.agent.gemini_client.genai') as mock_genai:
            from backend.agent.gemini_client import GeminiClient
            
            mock_genai.embed_content = Mock(return_value={'embedding': [0.1]})
            mock_genai.GenerativeModel.return_value = Mock()
            
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            await client.embed("Test text")
            
            # Verify task_type is set correctly
            call_kwargs = mock_genai.embed_content.call_args[1]
            assert call_kwargs['task_type'] == "retrieval_query"
            assert call_kwargs['model'] == "models/embedding-001"
    
    async def test_generate_runs_in_executor(self):
        """Test that generate runs synchronous API in executor."""
        with patch('backend.agent.gemini_client.genai') as mock_genai, \
             patch('asyncio.get_event_loop') as mock_get_loop:
            
            from backend.agent.gemini_client import GeminiClient
            
            mock_response = Mock()
            mock_response.text = "Response"
            mock_model = Mock()
            mock_model.generate_content = Mock(return_value=mock_response)
            mock_genai.GenerativeModel.return_value = mock_model
            
            mock_loop = AsyncMock()
            mock_loop.run_in_executor = AsyncMock(return_value=mock_response)
            mock_get_loop.return_value = mock_loop
            
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            result = await client.generate("Test")
            
            # Verify executor was used
            mock_loop.run_in_executor.assert_called_once()
    
    async def test_embed_runs_in_executor(self):
        """Test that embed runs synchronous API in executor."""
        with patch('backend.agent.gemini_client.genai') as mock_genai, \
             patch('asyncio.get_event_loop') as mock_get_loop:
            
            from backend.agent.gemini_client import GeminiClient
            
            mock_genai.GenerativeModel.return_value = Mock()
            
            mock_loop = AsyncMock()
            mock_loop.run_in_executor = AsyncMock(
                return_value={'embedding': [0.1, 0.2]}
            )
            mock_get_loop.return_value = mock_loop
            
            client = GeminiClient(api_key=os.getenv("GOOGLE_API_KEY", "test_api_key_do_not_use_in_prod"))
            result = await client.embed("Test")
            
            # Verify executor was used
            mock_loop.run_in_executor.assert_called_once()
