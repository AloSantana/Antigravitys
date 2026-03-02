"""OpenRouter client for accessing 200+ models via unified API."""

import os
import asyncio
import logging
import aiohttp
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Client for OpenRouter API - unified access to 200+ AI models.

    Provides access to models from: Anthropic (Claude), OpenAI (GPT-4),
    Google (Gemini), Meta (Llama), Mistral, and many others via a single API.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key. If None, reads from OPENROUTER_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-5")
        self.base_url = "https://openrouter.ai/api/v1"

        if not self.api_key:
            logger.warning("OpenRouterClient: OPENROUTER_API_KEY not set.")

    def is_available(self) -> bool:
        """Check if OpenRouter is available.

        Returns:
            bool: True if API key is configured, False otherwise.
        """
        return bool(self.api_key)

    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate a response from OpenRouter.

        Args:
            prompt: The input prompt to send to the model.
            model: Optional model override (e.g., "anthropic/claude-opus-4-5").
                   If None, uses the model from OPENROUTER_MODEL env var.

        Returns:
            str: The generated response text or error message.
        """
        if not self.api_key:
            return "Error: OpenRouter API Key not configured. Set OPENROUTER_API_KEY in .env"

        model_to_use = model or self.model
        logger.info(f"OpenRouter: Generating response with {model_to_use}")

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/AloSantana/Antigravitys",
                    "X-Title": "Antigravity Workspace"
                }

                payload = {
                    "model": model_to_use,
                    "messages": [{"role": "user", "content": prompt}]
                }

                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 min timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        logger.info(f"OpenRouter: Response received ({len(content)} chars)")
                        return content
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                        return f"Error: OpenRouter API returned status {response.status}. {error_text[:200]}"

        except asyncio.TimeoutError:
            logger.error("OpenRouter: Request timed out after 300s")
            return "Error: OpenRouter request timed out. Try again or use a different model."
        except Exception as e:
            logger.error(f"OpenRouter generate error: {e}")
            return f"Error: {str(e)}"

    async def embed(self, text: str):
        """OpenRouter doesn't provide embeddings - return None.

        Note: OpenRouter focuses on text generation, not embeddings.
        Use Gemini or OpenAI for embedding tasks.

        Args:
            text: Text to embed (ignored).

        Returns:
            None: OpenRouter does not support embeddings.
        """
        logger.warning("OpenRouter does not support embeddings, use Gemini or OpenAI instead")
        return None

    async def list_models(self) -> Dict[str, Any]:
        """Fetch available models from OpenRouter.

        Returns:
            dict: List of available models with metadata.
        """
        if not self.api_key:
            return {"error": "OpenRouter API Key not configured"}

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}

                async with session.get(
                    f"{self.base_url}/models",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter list_models error: {response.status}")
                        return {"error": error_text}

        except Exception as e:
            logger.error(f"OpenRouter list_models error: {e}")
            return {"error": str(e)}
