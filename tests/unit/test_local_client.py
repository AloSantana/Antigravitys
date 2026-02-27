"""
Unit tests for backend.agent.local_client module
Tests the LocalClient class for Ollama integration
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from aiohttp import ClientError, ClientTimeout


@pytest.mark.unit
@pytest.mark.asyncio
class TestLocalClient:
    """Test suite for LocalClient class."""
    
    async def test_client_initialization(self):
        """Test LocalClient initializes with correct defaults."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        
        assert client.base_url == "http://localhost:11434"
        assert client.model == "llama3.2"
        assert client._max_retries == 2
        assert client._session is None
        assert isinstance(client._timeout, ClientTimeout)
    
    async def test_client_initialization_custom_url(self):
        """Test LocalClient with custom base URL."""
        from backend.agent.local_client import LocalClient
        
        custom_url = "http://custom-host:8080"
        client = LocalClient(base_url=custom_url)
        
        assert client.base_url == custom_url
    
    async def test_client_initialization_custom_model(self, mock_env_vars):
        """Test LocalClient uses custom model from environment."""
        with patch.dict('os.environ', {'LOCAL_MODEL': 'llama3.1'}):
            from backend.agent.local_client import LocalClient
            client = LocalClient()
            assert client.model == "llama3.1"
    
    async def test_get_session_creates_new(self):
        """Test that _get_session creates a new session if none exists."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        session = await client._get_session()
        
        assert session is not None
        assert isinstance(session, aiohttp.ClientSession)
        assert not session.closed
        
        await client.close()
    
    async def test_get_session_reuses_existing(self):
        """Test that _get_session reuses existing session."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        session1 = await client._get_session()
        session2 = await client._get_session()
        
        assert session1 is session2
        
        await client.close()
    
    async def test_get_session_recreates_if_closed(self):
        """Test that _get_session recreates session if closed."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        session1 = await client._get_session()
        await session1.close()
        
        session2 = await client._get_session()
        
        assert session2 is not session1
        assert not session2.closed
        
        await client.close()
    
    async def test_close_session(self):
        """Test closing the client session."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        session = await client._get_session()
        
        await client.close()
        
        assert session.closed
        assert client._session is None
    
    async def test_generate_success(self):
        """Test successful text generation."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"response": "Generated text"})
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_get_session.return_value = mock_session
            
            result = await client.generate("Test prompt")
        
        assert result == "Generated text"
    
    async def test_generate_model_not_found(self):
        """Test handling when model is not found."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        
        # Mock 404 response
        mock_response = AsyncMock()
        mock_response.status = 404
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_get_session.return_value = mock_session
            
            result = await client.generate("Test prompt")
        
        assert "Model" in result
        assert "not found" in result
        assert "ollama pull" in result
    
    async def test_generate_http_error(self):
        """Test handling HTTP errors during generation."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        client._max_retries = 0  # No retries for faster test
        
        # Mock 500 error
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_get_session.return_value = mock_session
            
            result = await client.generate("Test prompt")
        
        assert "Error: 500" in result
    
    async def test_generate_connection_error(self):
        """Test handling connection errors."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        client._max_retries = 0  # No retries for faster test
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(side_effect=aiohttp.ClientError("Connection failed"))
            mock_get_session.return_value = mock_session
            
            result = await client.generate("Test prompt")
        
        assert "Could not connect to Ollama" in result
    
    async def test_generate_timeout_error(self):
        """Test handling timeout errors."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        client._max_retries = 0  # No retries for faster test
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(side_effect=asyncio.TimeoutError())
            mock_get_session.return_value = mock_session
            
            result = await client.generate("Test prompt")
        
        assert "timed out" in result
    
    async def test_generate_generic_exception(self):
        """Test handling generic exceptions."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        client._max_retries = 0
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(side_effect=Exception("Unexpected error"))
            mock_get_session.return_value = mock_session
            
            result = await client.generate("Test prompt")
        
        assert "Error:" in result
        assert "Unexpected error" in result
    
    async def test_generate_retry_logic(self):
        """Test retry logic on failures."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        client._max_retries = 2
        
        # First two attempts fail, third succeeds
        mock_response_fail = AsyncMock()
        mock_response_fail.status = 500
        mock_response_fail.text = AsyncMock(return_value="Error")
        
        mock_response_success = AsyncMock()
        mock_response_success.status = 200
        mock_response_success.json = AsyncMock(return_value={"response": "Success"})
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(
                side_effect=[mock_response_fail, mock_response_fail, mock_response_success]
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_get_session.return_value = mock_session
            
            result = await client.generate("Test prompt")
        
        assert result == "Success"
        assert mock_session.post.call_count == 3
    
    async def test_generate_max_retries_exceeded(self):
        """Test behavior when max retries are exceeded."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        client._max_retries = 1
        
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Error")
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_get_session.return_value = mock_session
            
            result = await client.generate("Test prompt")
        
        assert "Error: 500" in result
        assert mock_session.post.call_count == 2  # Initial + 1 retry
    
    async def test_embed_success(self):
        """Test successful embedding generation."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        expected_embedding = [0.1, 0.2, 0.3] * 256
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"embedding": expected_embedding})
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_get_session.return_value = mock_session
            
            result = await client.embed("Test text")
        
        assert result == expected_embedding
    
    async def test_embed_http_error(self):
        """Test handling errors during embedding."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        client._max_retries = 0
        
        mock_response = AsyncMock()
        mock_response.status = 500
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_get_session.return_value = mock_session
            
            result = await client.embed("Test text")
        
        assert result == []
    
    async def test_embed_connection_error(self):
        """Test handling connection errors during embedding."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        client._max_retries = 0
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(side_effect=aiohttp.ClientError("Connection failed"))
            mock_get_session.return_value = mock_session
            
            result = await client.embed("Test text")
        
        assert result == []
    
    async def test_embed_timeout_error(self):
        """Test handling timeout during embedding."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        client._max_retries = 0
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(side_effect=asyncio.TimeoutError())
            mock_get_session.return_value = mock_session
            
            result = await client.embed("Test text")
        
        assert result == []
    
    async def test_embed_retry_logic(self):
        """Test retry logic for embedding."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        client._max_retries = 2
        
        mock_response_fail = AsyncMock()
        mock_response_fail.status = 500
        
        mock_response_success = AsyncMock()
        mock_response_success.status = 200
        mock_response_success.json = AsyncMock(return_value={"embedding": [0.1, 0.2]})
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(
                side_effect=[mock_response_fail, mock_response_success]
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_get_session.return_value = mock_session
            
            result = await client.embed("Test text")
        
        assert result == [0.1, 0.2]
        assert mock_session.post.call_count == 2
    
    async def test_generate_payload_format(self):
        """Test that generate creates correct payload."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"response": "Test"})
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            
            # Capture the post call
            posted_data = None
            async def capture_post(url, json=None, **kwargs):
                nonlocal posted_data
                posted_data = json
                return mock_response
            
            mock_session.post = capture_post
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_get_session.return_value = mock_session
            
            await client.generate("Test prompt")
        
        assert posted_data["model"] == client.model
        assert posted_data["prompt"] == "Test prompt"
        assert posted_data["stream"] is False
    
    async def test_embed_payload_format(self):
        """Test that embed creates correct payload."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"embedding": [0.1]})
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            
            # Capture the post call
            posted_data = None
            async def capture_post(url, json=None, **kwargs):
                nonlocal posted_data
                posted_data = json
                return mock_response
            
            mock_session.post = capture_post
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_get_session.return_value = mock_session
            
            await client.embed("Test text")
        
        assert posted_data["model"] == client.model
        assert posted_data["prompt"] == "Test text"
    
    @pytest.mark.parametrize("prompt,expected_length", [
        ("Short prompt", 12),
        ("", 0),
        ("A" * 1000, 1000),
    ])
    async def test_generate_various_prompts(self, prompt, expected_length):
        """Test generation with various prompt lengths."""
        from backend.agent.local_client import LocalClient
        
        client = LocalClient()
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"response": "Response"})
        
        with patch.object(client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock()
            mock_get_session.return_value = mock_session
            
            result = await client.generate(prompt)
        
        assert result == "Response"
        assert len(prompt) == expected_length
