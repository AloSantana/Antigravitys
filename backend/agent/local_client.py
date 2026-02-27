import aiohttp
import os
import asyncio
from typing import Optional

class LocalClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = os.getenv("LOCAL_MODEL", "llama3.2")  # Default to llama3.2
        # Connection pool for reusing connections
        self._session: Optional[aiohttp.ClientSession] = None
        self._max_retries = 2
        self._timeout = aiohttp.ClientTimeout(total=30, connect=5)
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create a shared session for connection pooling."""
        if self._session is None or self._session.closed:
            # Create session with connection pooling
            connector = aiohttp.TCPConnector(
                limit=10,  # Max 10 concurrent connections
                limit_per_host=5,  # Max 5 per host
                ttl_dns_cache=300  # Cache DNS for 5 minutes
            )
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=self._timeout
            )
        return self._session
    
    async def close(self):
        """Close the session and cleanup resources."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def generate(self, prompt: str) -> str:
        """
        Generates a response from the local Ollama instance with retry logic.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        for attempt in range(self._max_retries + 1):
            try:
                session = await self._get_session()
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    elif response.status == 404:
                        return f"Error: Model '{self.model}' not found. Please pull it with: ollama pull {self.model}"
                    else:
                        error_text = await response.text()
                        if attempt < self._max_retries:
                            print(f"Attempt {attempt + 1} failed, retrying...")
                            await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                            continue
                        return f"Error: {response.status} - {error_text}"
            except asyncio.TimeoutError:
                if attempt < self._max_retries:
                    print(f"Request timeout, retrying (attempt {attempt + 1})...")
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                return f"Local LLM Error: Request timed out after {self._max_retries + 1} attempts"
            except aiohttp.ClientError:
                if attempt < self._max_retries:
                    print(f"Connection error, retrying (attempt {attempt + 1})...")
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                return f"Local LLM Error: Could not connect to Ollama at {self.base_url}. Is it running?"
            except Exception as e:
                return f"Local LLM Error: {str(e)}"
        
        return "Local LLM Error: Max retries exceeded"

    async def embed(self, text: str) -> list[float]:
        """
        Generates embeddings using Ollama with retry logic.
        """
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": self.model,
            "prompt": text
        }
        
        for attempt in range(self._max_retries + 1):
            try:
                session = await self._get_session()
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("embedding", [])
                    else:
                        if attempt < self._max_retries:
                            print(f"Embedding attempt {attempt + 1} failed, retrying...")
                            await asyncio.sleep(0.5 * (attempt + 1))
                            continue
                        print(f"Embedding Error: {response.status}")
                        return []
            except asyncio.TimeoutError:
                if attempt < self._max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                print("Embedding Error: Request timed out")
                return []
            except aiohttp.ClientError as e:
                if attempt < self._max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                print(f"Embedding Connection Error: {e}")
                return []
            except Exception as e:
                print(f"Embedding Error: {e}")
                return []
        
        return []
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        # Note: asyncio cleanup in __del__ is tricky, better to use close() explicitly
        if self._session and not self._session.closed:
            # Try to close gracefully, but don't fail if event loop is closed
            try:
                asyncio.create_task(self._session.close())
            except:
                pass
