import asyncio
import logging

logger = logging.getLogger(__name__)

# Resilient import for google-genai SDK
try:
    from google import genai
    from google.genai import types
    _GENAI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"google-genai SDK not available: {e}. Gemini features will be disabled.")
    logger.info("Install with: pip install google-genai>=1.0.0")
    genai = None
    types = None
    _GENAI_AVAILABLE = False

class GeminiClient:
    def __init__(self, api_key: str):
        if not _GENAI_AVAILABLE:
            logger.warning("GeminiClient: google-genai SDK not installed. Client disabled.")
            self.client = None
            return

        if not api_key:
            logger.warning("GeminiClient: GEMINI_API_KEY not set.")
            self.client = None
            return
            
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'  # Latest stable model
        self.embed_model_name = "models/text-embedding-004"
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests

    async def generate(self, prompt: str) -> str:
        """
        Generates a response from Gemini with rate limiting.
        """
        if not self.client:
            return "Error: Gemini API Key not configured."
        
        # Simple rate limiting
        await self._rate_limit()
            
        try:
            # Run synchronous API call in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            # Provide helpful error messages
            if "quota" in error_msg.lower():
                return "Gemini Error: API quota exceeded. Please check your usage limits."
            elif "api key" in error_msg.lower():
                return "Gemini Error: Invalid API key. Please check your configuration."
            else:
                return f"Gemini Error: {error_msg}"
    
    async def _rate_limit(self):
        """Simple rate limiting to avoid API throttling."""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - time_since_last)
        self._last_request_time = asyncio.get_event_loop().time()

    async def embed(self, text: str) -> list[float]:
        """
        Generates embeddings using Gemini with caching and rate limiting.
        """
        if not self.client:
            return []
        
        # Simple rate limiting
        await self._rate_limit()
            
        try:
            # Run synchronous API call in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.models.embed_content(
                    model=self.embed_model_name,
                    contents=text
                )
            )
            # The new SDK returns embeddings in a slightly different structure
            if result.embeddings:
                return result.embeddings[0].values
            return []
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower():
                print("Gemini Embedding Error: API quota exceeded")
            else:
                print(f"Gemini Embedding Error: {error_msg}")
            return []
