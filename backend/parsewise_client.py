"""
Parsewise.ai API client for AI-powered document extraction and validation.

Wraps the Parsewise REST API to provide document processing capabilities
within the Antigravity workspace.
"""
import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class ParsewiseClient:
    """Client for the Parsewise.ai document processing API.

    Provides methods for extracting structured data from documents,
    validating extracted results, and checking service availability.

    Args:
        api_key: Parsewise API key. Defaults to the ``PARSEWISE_API_KEY``
            environment variable.
        base_url: Base URL for the Parsewise API. Defaults to the
            ``PARSEWISE_BASE_URL`` environment variable or
            ``https://api.parsewise.ai``.
        timeout: HTTP request timeout in seconds (default: 30).
    """

    DEFAULT_BASE_URL = "https://api.parsewise.ai"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        self.api_key: Optional[str] = api_key or os.getenv("PARSEWISE_API_KEY")
        self.base_url: str = (
            base_url
            or os.getenv("PARSEWISE_BASE_URL", self.DEFAULT_BASE_URL)
        ).rstrip("/")
        self.timeout = timeout

        if not self.api_key:
            logger.warning(
                "ParsewiseClient: PARSEWISE_API_KEY not set. "
                "API calls will fail until a key is configured."
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> Dict[str, str]:
        """Build authorization headers for every request.

        Note: This is an internal helper. Always call :meth:`_check_api_key`
        before invoking methods that use these headers.
        """
        return {
            "Authorization": f"Bearer {self.api_key or ''}",
            "Accept": "application/json",
        }

    def _check_api_key(self) -> None:
        """Raise ``RuntimeError`` when the API key is not configured."""
        if not self.api_key:
            raise RuntimeError(
                "PARSEWISE_API_KEY is not configured. "
                "Set the environment variable or pass api_key= to the constructor."
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def extract_from_file(self, file_path: str) -> Dict[str, Any]:
        """Upload a local file and extract structured data from it.

        Args:
            file_path: Absolute or relative path to the document to process.

        Returns:
            A dict containing the extraction result, e.g.::

                {
                    "status": "success",
                    "extraction_id": "abc123",
                    "data": {...},
                }

        Raises:
            RuntimeError: If the API key is not configured.
            FileNotFoundError: If ``file_path`` does not exist.
            httpx.HTTPStatusError: On non-2xx responses from the API.
        """
        self._check_api_key()

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info("ParsewiseClient: extracting from file '%s'", path.name)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                with open(path, "rb") as fh:
                    response = await client.post(
                        f"{self.base_url}/v1/extract",
                        headers=self._headers(),
                        files={"file": (path.name, fh)},
                    )
                response.raise_for_status()
                result: Dict[str, Any] = response.json()
                logger.info(
                    "ParsewiseClient: extraction successful for '%s'", path.name
                )
                return result
        except httpx.HTTPStatusError as exc:
            logger.error(
                "ParsewiseClient: HTTP %s error extracting file '%s': %s",
                exc.response.status_code,
                path.name,
                exc.response.text,
            )
            raise
        except Exception as exc:
            logger.error(
                "ParsewiseClient: unexpected error extracting file '%s': %s",
                path.name,
                exc,
            )
            raise

    async def extract_from_url(self, url: str) -> Dict[str, Any]:
        """Submit a public URL for document extraction.

        Args:
            url: Publicly accessible URL of the document to process.

        Returns:
            A dict containing the extraction result.

        Raises:
            RuntimeError: If the API key is not configured.
            ValueError: If ``url`` is empty.
            httpx.HTTPStatusError: On non-2xx responses from the API.
        """
        self._check_api_key()

        if not url:
            raise ValueError("url must not be empty")

        logger.info("ParsewiseClient: extracting from URL '%s'", url)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/extract/url",
                    headers={**self._headers(), "Content-Type": "application/json"},
                    json={"url": url},
                )
                response.raise_for_status()
                result: Dict[str, Any] = response.json()
                logger.info("ParsewiseClient: extraction successful for URL '%s'", url)
                return result
        except httpx.HTTPStatusError as exc:
            logger.error(
                "ParsewiseClient: HTTP %s error extracting URL '%s': %s",
                exc.response.status_code,
                url,
                exc.response.text,
            )
            raise
        except Exception as exc:
            logger.error(
                "ParsewiseClient: unexpected error extracting URL '%s': %s", url, exc
            )
            raise

    async def validate_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit previously extracted data to Parsewise for validation.

        Args:
            data: The extraction payload to validate (as returned by
                :meth:`extract_from_file` or :meth:`extract_from_url`).

        Returns:
            A dict with validation results, e.g.::

                {
                    "valid": True,
                    "errors": [],
                    "warnings": [...],
                }

        Raises:
            RuntimeError: If the API key is not configured.
            ValueError: If ``data`` is empty.
            httpx.HTTPStatusError: On non-2xx responses from the API.
        """
        self._check_api_key()

        if not data:
            raise ValueError("data must not be empty")

        logger.info("ParsewiseClient: validating extraction data")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/v1/validate",
                    headers={**self._headers(), "Content-Type": "application/json"},
                    json={"data": data},
                )
                response.raise_for_status()
                result: Dict[str, Any] = response.json()
                logger.info("ParsewiseClient: validation complete")
                return result
        except httpx.HTTPStatusError as exc:
            logger.error(
                "ParsewiseClient: HTTP %s error during validation: %s",
                exc.response.status_code,
                exc.response.text,
            )
            raise
        except Exception as exc:
            logger.error("ParsewiseClient: unexpected error during validation: %s", exc)
            raise

    async def get_status(self) -> Dict[str, Any]:
        """Check the availability and status of the Parsewise service.

        Returns:
            A dict with service status information, e.g.::

                {
                    "status": "operational",
                    "version": "1.2.3",
                    "authenticated": True,
                }

        The ``"authenticated"`` key reflects whether the stored API key
        is valid. If the key is absent or the service is unreachable the
        method returns a degraded status dict rather than raising.
        """
        if not self.api_key:
            return {
                "status": "unavailable",
                "authenticated": False,
                "error": "PARSEWISE_API_KEY not configured",
            }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/v1/status",
                    headers=self._headers(),
                )
                response.raise_for_status()
                result: Dict[str, Any] = response.json()
                result.setdefault("authenticated", True)
                return result
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "ParsewiseClient: service returned HTTP %s on status check: %s",
                exc.response.status_code,
                exc.response.text,
            )
            return {
                "status": "error",
                "authenticated": exc.response.status_code != 401,
                "http_status": exc.response.status_code,
                "error": exc.response.text,
            }
        except Exception as exc:
            logger.warning("ParsewiseClient: status check failed: %s", exc)
            return {
                "status": "unreachable",
                "authenticated": False,
                "error": str(exc),
            }
