"""
OpenAI-compatible API proxy tool.

Allows calling any OpenAI-compatible API endpoint from the agent.
"""

from typing import List, Dict, Any, Optional
import logging

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from src.config import settings

logger = logging.getLogger(__name__)


async def call_openai_chat(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> Dict[str, Any]:
    """
    Call an OpenAI-compatible chat completion API.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Model to use (defaults to settings.OPENAI_MODEL)
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens to generate
        
    Returns:
        API response as dictionary
        
    Raises:
        ValueError: If OpenAI API is not configured
        RuntimeError: If API call fails
    """
    if not HTTPX_AVAILABLE:
        raise ImportError("httpx is required for OpenAI proxy. Install with: pip install httpx")
    
    if not settings.OPENAI_BASE_URL:
        raise ValueError("OPENAI_BASE_URL not configured in settings")
    
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not configured - may fail for some providers")
    
    model = model or settings.OPENAI_MODEL
    
    # Prepare the request
    url = f"{settings.OPENAI_BASE_URL}/chat/completions"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if settings.OPENAI_API_KEY:
        headers["Authorization"] = f"Bearer {settings.OPENAI_API_KEY}"
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }
    
    if max_tokens:
        payload["max_tokens"] = max_tokens
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data,
                    "content": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "model": data.get("model", model),
                    "usage": data.get("usage", {})
                }
            else:
                error_msg = f"API call failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
    except Exception as e:
        error_msg = f"Error calling OpenAI API: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }


def call_openai_chat_sync(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> Dict[str, Any]:
    """
    Synchronous wrapper for call_openai_chat.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Model to use (defaults to settings.OPENAI_MODEL)
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens to generate
        
    Returns:
        API response as dictionary
    """
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(
        call_openai_chat(messages, model, temperature, max_tokens)
    )


def is_openai_proxy_configured() -> bool:
    """
    Check if OpenAI proxy is properly configured.
    
    Returns:
        True if base URL and API key are set
    """
    return bool(settings.OPENAI_BASE_URL and settings.OPENAI_API_KEY)


# Convenience function for simple queries
async def ask_openai(question: str, system_prompt: str = "") -> str:
    """
    Simple convenience function to ask OpenAI a question.
    
    Args:
        question: The question to ask
        system_prompt: Optional system prompt to set context
        
    Returns:
        Response text
    """
    messages = []
    
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": question})
    
    result = await call_openai_chat(messages)
    
    if result.get("success"):
        return result.get("content", "")
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


def ask_openai_sync(question: str, system_prompt: str = "") -> str:
    """
    Synchronous version of ask_openai.
    
    Args:
        question: The question to ask
        system_prompt: Optional system prompt to set context
        
    Returns:
        Response text
    """
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(ask_openai(question, system_prompt))


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_openai_proxy():
        """Test the OpenAI proxy."""
        if not is_openai_proxy_configured():
            print("OpenAI proxy is not configured.")
            print("Set OPENAI_BASE_URL and OPENAI_API_KEY in .env file.")
            return
        
        print("Testing OpenAI proxy...")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in 5 words or less."}
        ]
        
        result = await call_openai_chat(messages)
        
        if result.get("success"):
            print(f"Success! Response: {result.get('content')}")
            print(f"Model: {result.get('model')}")
            print(f"Usage: {result.get('usage')}")
        else:
            print(f"Failed: {result.get('error')}")
    
    asyncio.run(test_openai_proxy())
