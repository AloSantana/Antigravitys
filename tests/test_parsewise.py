"""
Tests for the ParsewiseClient and /api/parsewise/* endpoints.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# ---------------------------------------------------------------------------
# ParsewiseClient unit tests
# ---------------------------------------------------------------------------


class TestParsewiseClientInit:
    """Test ParsewiseClient initialisation."""

    def test_reads_env_api_key(self, monkeypatch):
        """API key is read from PARSEWISE_API_KEY when not passed explicitly."""
        monkeypatch.setenv("PARSEWISE_API_KEY", "test-key-from-env")
        monkeypatch.delenv("PARSEWISE_BASE_URL", raising=False)

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient()
        assert client.api_key == "test-key-from-env"

    def test_reads_env_base_url(self, monkeypatch):
        """Base URL is read from PARSEWISE_BASE_URL when not passed explicitly."""
        monkeypatch.setenv("PARSEWISE_API_KEY", "key")
        monkeypatch.setenv("PARSEWISE_BASE_URL", "https://custom.example.com/")

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient()
        # trailing slash is stripped
        assert client.base_url == "https://custom.example.com"

    def test_defaults_base_url(self, monkeypatch):
        """Base URL defaults to the Parsewise production API."""
        monkeypatch.setenv("PARSEWISE_API_KEY", "key")
        monkeypatch.delenv("PARSEWISE_BASE_URL", raising=False)

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient()
        assert client.base_url == "https://api.parsewise.ai"

    def test_explicit_args_override_env(self, monkeypatch):
        """Constructor arguments take precedence over environment variables."""
        monkeypatch.setenv("PARSEWISE_API_KEY", "env-key")
        monkeypatch.setenv("PARSEWISE_BASE_URL", "https://env.example.com")

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient(api_key="explicit-key", base_url="https://explicit.example.com")
        assert client.api_key == "explicit-key"
        assert client.base_url == "https://explicit.example.com"

    def test_missing_api_key_logs_warning(self, monkeypatch, caplog):
        """A warning is emitted when no API key is configured."""
        monkeypatch.delenv("PARSEWISE_API_KEY", raising=False)

        import logging
        from parsewise_client import ParsewiseClient

        with caplog.at_level(logging.WARNING, logger="parsewise_client"):
            client = ParsewiseClient()

        assert client.api_key is None
        assert "PARSEWISE_API_KEY" in caplog.text


class TestParsewiseClientGetStatus:
    """Test ParsewiseClient.get_status()."""

    @pytest.mark.asyncio
    async def test_returns_unavailable_when_no_key(self, monkeypatch):
        """get_status returns a degraded dict when API key is absent."""
        monkeypatch.delenv("PARSEWISE_API_KEY", raising=False)

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient()
        result = await client.get_status()

        assert result["status"] == "unavailable"
        assert result["authenticated"] is False

    @pytest.mark.asyncio
    async def test_successful_status_check(self, monkeypatch):
        """get_status returns the API response on success."""
        monkeypatch.setenv("PARSEWISE_API_KEY", "valid-key")

        import httpx

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"status": "operational", "version": "1.0"}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient()
        with patch("parsewise_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.get_status()

        assert result["status"] == "operational"
        assert result["authenticated"] is True

    @pytest.mark.asyncio
    async def test_status_returns_degraded_on_http_error(self, monkeypatch):
        """get_status returns a degraded dict on HTTP error (no exception raised)."""
        monkeypatch.setenv("PARSEWISE_API_KEY", "bad-key")

        import httpx

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "401", request=MagicMock(), response=mock_response
            )
        )

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient()
        with patch("parsewise_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.get_status()

        assert result["status"] == "error"
        assert result["authenticated"] is False  # 401 → not authenticated


class TestParsewiseClientExtractFromFile:
    """Test ParsewiseClient.extract_from_file()."""

    @pytest.mark.asyncio
    async def test_raises_runtime_error_without_api_key(self, monkeypatch, tmp_path):
        """extract_from_file raises RuntimeError when API key is absent."""
        monkeypatch.delenv("PARSEWISE_API_KEY", raising=False)

        target = tmp_path / "doc.pdf"
        target.write_bytes(b"%PDF-1.4 sample")

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient()
        with pytest.raises(RuntimeError, match="PARSEWISE_API_KEY"):
            await client.extract_from_file(str(target))

    @pytest.mark.asyncio
    async def test_raises_file_not_found(self, monkeypatch):
        """extract_from_file raises FileNotFoundError for missing files."""
        monkeypatch.setenv("PARSEWISE_API_KEY", "key")

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient()
        with pytest.raises(FileNotFoundError):
            await client.extract_from_file("/nonexistent/path/doc.pdf")

    @pytest.mark.asyncio
    async def test_successful_extraction(self, monkeypatch, tmp_path):
        """extract_from_file returns the API response on success."""
        monkeypatch.setenv("PARSEWISE_API_KEY", "key")

        target = tmp_path / "invoice.pdf"
        target.write_bytes(b"%PDF sample content")

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "status": "success",
            "extraction_id": "abc123",
            "data": {"total": 100},
        }

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient()
        with patch("parsewise_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.extract_from_file(str(target))

        assert result["status"] == "success"
        assert result["extraction_id"] == "abc123"


class TestParsewiseClientExtractFromURL:
    """Test ParsewiseClient.extract_from_url()."""

    @pytest.mark.asyncio
    async def test_raises_on_empty_url(self, monkeypatch):
        """extract_from_url raises ValueError for empty URL."""
        monkeypatch.setenv("PARSEWISE_API_KEY", "key")

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient()
        with pytest.raises(ValueError, match="url must not be empty"):
            await client.extract_from_url("")

    @pytest.mark.asyncio
    async def test_successful_url_extraction(self, monkeypatch):
        """extract_from_url returns the API response on success."""
        monkeypatch.setenv("PARSEWISE_API_KEY", "key")

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"status": "success", "data": {"name": "Test"}}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient()
        with patch("parsewise_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.extract_from_url("https://example.com/doc.pdf")

        assert result["status"] == "success"


class TestParsewiseClientValidateExtraction:
    """Test ParsewiseClient.validate_extraction()."""

    @pytest.mark.asyncio
    async def test_raises_on_empty_data(self, monkeypatch):
        """validate_extraction raises ValueError for empty data."""
        monkeypatch.setenv("PARSEWISE_API_KEY", "key")

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient()
        with pytest.raises(ValueError, match="data must not be empty"):
            await client.validate_extraction({})

    @pytest.mark.asyncio
    async def test_successful_validation(self, monkeypatch):
        """validate_extraction returns the API response on success."""
        monkeypatch.setenv("PARSEWISE_API_KEY", "key")

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"valid": True, "errors": [], "warnings": []}

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        from parsewise_client import ParsewiseClient

        client = ParsewiseClient()
        with patch("parsewise_client.httpx.AsyncClient", return_value=mock_client):
            result = await client.validate_extraction({"extraction_id": "abc123", "data": {}})

        assert result["valid"] is True
        assert result["errors"] == []
