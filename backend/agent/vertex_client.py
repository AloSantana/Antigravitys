"""
Vertex AI client for the Antigravity Workspace.
Provides integration with Google Cloud's Vertex AI API.
"""

import os
import asyncio
import logging
from typing import Optional, List, Dict, Any

try:
    from google.cloud import aiplatform
    from vertexai.preview.generative_models import GenerativeModel, ChatSession
    import vertexai
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False

logger = logging.getLogger(__name__)


class VertexClient:
    """
    Client for interacting with Google Cloud Vertex AI API.
    Supports text generation and chat functionality.
    """
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None, 
                 location: str = "us-central1"):
        """
        Initialize Vertex AI client.
        
        Args:
            api_key: Vertex AI API key (optional, can use service account instead)
            project_id: Google Cloud project ID
            location: GCP region for Vertex AI (default: us-central1)
        """
        self.api_key = api_key or os.getenv("VERTEX_API_KEY")
        self.project_id = project_id or os.getenv("VERTEX_PROJECT_ID", os.getenv("GCP_PROJECT_ID"))
        self.location = location or os.getenv("VERTEX_LOCATION", "us-central1")
        self.model_name = os.getenv("VERTEX_MODEL", "gemini-pro")
        
        self.model = None
        self.chat_session = None
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests for rate limiting
        
        # Initialize Vertex AI if available
        if not VERTEX_AVAILABLE:
            logger.warning("Vertex AI SDK not installed. Install with: pip install google-cloud-aiplatform")
            return
        
        if not self.api_key:
            logger.warning("VERTEX_API_KEY not set. Vertex AI functionality will be limited.")
            return
        
        if not self.project_id:
            logger.warning("VERTEX_PROJECT_ID not set. Using default project or service account.")
        
        try:
            # Initialize Vertex AI
            logger.info(f"Initializing Vertex AI with project={self.project_id}, location={self.location}")
            
            # Set API key as environment variable for authentication
            if self.api_key:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.api_key
            
            # Initialize vertexai
            vertexai.init(project=self.project_id, location=self.location)
            
            # Initialize the generative model
            self.model = GenerativeModel(self.model_name)
            logger.info(f"Vertex AI initialized successfully with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            self.model = None
    
    async def generate(self, prompt: str, temperature: float = 0.7, 
                      max_tokens: int = 2048) -> str:
        """
        Generate text using Vertex AI.
        
        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        if not VERTEX_AVAILABLE:
            return "Error: Vertex AI SDK not installed. Install with: pip install google-cloud-aiplatform"
        
        if not self.model:
            return "Error: Vertex AI not configured. Please set VERTEX_API_KEY and VERTEX_PROJECT_ID."
        
        # Apply rate limiting
        await self._rate_limit()
        
        try:
            # Run synchronous API call in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    }
                )
            )
            
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Vertex AI generation error: {error_msg}")
            
            # Provide helpful error messages
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                return "Vertex AI Error: API quota exceeded. Please check your usage limits."
            elif "authentication" in error_msg.lower() or "permission" in error_msg.lower():
                return "Vertex AI Error: Authentication failed. Please check your API key and project permissions."
            elif "not found" in error_msg.lower():
                return f"Vertex AI Error: Model '{self.model_name}' not found. Check your model name."
            else:
                return f"Vertex AI Error: {error_msg}"
    
    async def chat(self, message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Chat with Vertex AI maintaining conversation context.
        
        Args:
            message: User message
            history: Optional chat history (list of {"role": "user/model", "content": "..."})
            
        Returns:
            Model response
        """
        if not VERTEX_AVAILABLE or not self.model:
            return await self.generate(message)
        
        await self._rate_limit()
        
        try:
            # Start or continue chat session
            if not self.chat_session or history is None:
                self.chat_session = self.model.start_chat(history=history or [])
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.chat_session.send_message(message)
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Vertex AI chat error: {e}")
            return f"Vertex AI Chat Error: {str(e)}"
    
    async def embed(self, text: str) -> List[float]:
        """
        Generate embeddings using Vertex AI text-embedding model.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if not VERTEX_AVAILABLE:
            logger.warning("Vertex AI SDK not available, returning empty vector")
            return []
        
        if not self.project_id:
            logger.warning("Vertex AI project ID not set, cannot generate embeddings")
            return []
        
        await self._rate_limit()
        
        try:
            # Use text-embedding-004 model for embeddings
            from vertexai.language_models import TextEmbeddingModel
            
            # Initialize embedding model (cached on first use)
            if not hasattr(self, '_embedding_model'):
                self._embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            
            # Run synchronous API call in thread pool
            loop = asyncio.get_running_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self._embedding_model.get_embeddings([text])
            )
            
            if embeddings and len(embeddings) > 0:
                # Return the embedding values as a list
                return embeddings[0].values
            else:
                logger.warning("Vertex AI returned empty embeddings")
                return []
            
        except ImportError:
            logger.warning("Vertex AI language models not available. Install with: pip install google-cloud-aiplatform")
            return []
        except Exception as e:
            logger.error(f"Vertex AI embedding error: {e}")
            return []
    
    async def _rate_limit(self):
        """Simple rate limiting to avoid API throttling."""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - time_since_last)
        
        self._last_request_time = asyncio.get_event_loop().time()
    
    def reset_chat(self):
        """Reset the chat session."""
        self.chat_session = None
        logger.info("Vertex AI chat session reset")
    
    async def close(self):
        """Clean up resources."""
        self.chat_session = None
        self.model = None
        logger.info("Vertex AI client closed")
    
    def is_available(self) -> bool:
        """Check if Vertex AI is available and configured."""
        return VERTEX_AVAILABLE and self.model is not None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        return {
            "available": self.is_available(),
            "model": self.model_name if self.model else None,
            "project_id": self.project_id,
            "location": self.location,
            "api_key_set": bool(self.api_key),
        }
