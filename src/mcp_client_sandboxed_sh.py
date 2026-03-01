"""
MCP (Model Context Protocol) Client for sandboxed.sh control API.

This module provides a comprehensive MCP server wrapping the sandboxed.sh control API,
enabling Claude to invoke tools on sandboxed.sh and receive streaming agent responses.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, AsyncIterator
from uuid import UUID

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents a tool exposed by an MCP server."""

    name: str
    description: str
    server_name: str
    input_schema: Dict[str, Any]
    original_name: str

    def get_prefixed_name(self) -> str:
        """Get the tool name with server prefix."""
        prefix = settings.MCP_TOOL_PREFIX
        return f"{prefix}{self.server_name}_{self.original_name}"


@dataclass
class SandboxedShConnection:
    """Represents a connection to sandboxed.sh control API."""

    base_url: str
    client: Optional[httpx.AsyncClient] = None
    tools: List[MCPTool] = field(default_factory=list)
    connected: bool = False
    error: Optional[str] = None
    mission_id: Optional[str] = None
    pending_tool_calls: Dict[str, asyncio.Future] = field(default_factory=dict)


# Hardcoded tools for sandboxed.sh (can be extended or made dynamic)
SANDBOXED_SH_TOOLS = [
    MCPTool(
        name="bash_execution",
        description="Execute bash commands in sandboxed environment",
        server_name="sandboxed-sh",
        input_schema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Bash command to execute"
                }
            },
            "required": ["command"]
        },
        original_name="bash"
    ),
    MCPTool(
        name="python_execution",
        description="Execute Python code in sandboxed environment",
        server_name="sandboxed-sh",
        input_schema={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                }
            },
            "required": ["code"]
        },
        original_name="python"
    ),
    MCPTool(
        name="file_write",
        description="Write content to a file in sandboxed environment",
        server_name="sandboxed-sh",
        input_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path"
                },
                "content": {
                    "type": "string",
                    "description": "File content"
                }
            },
            "required": ["path", "content"]
        },
        original_name="write_file"
    ),
    MCPTool(
        name="file_read",
        description="Read content from a file in sandboxed environment",
        server_name="sandboxed-sh",
        input_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path"
                }
            },
            "required": ["path"]
        },
        original_name="read_file"
    ),
]


class SandboxedShMCPServer:
    """MCP server wrapping sandboxed.sh control API.
    
    Enables Claude to invoke tools on sandboxed.sh and receive streaming
    agent responses through SSE events.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3000",
        timeout: int = 30
    ):
        """Initialize the MCP server.
        
        Args:
            base_url: Base URL for sandboxed.sh control API
            timeout: HTTP request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.connection = SandboxedShConnection(
            base_url=base_url,
            tools=SANDBOXED_SH_TOOLS.copy()
        )
        self.stream_task: Optional[asyncio.Task] = None

    async def initialize(self) -> bool:
        """Initialize connection to sandboxed.sh.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connection.client = httpx.AsyncClient(
                timeout=self.timeout,
                base_url=self.base_url
            )
            
            # Test connection with health check
            response = await self.connection.client.get(
                "/health",
                timeout=5
            )
            
            if response.status_code == 200:
                self.connection.connected = True
                logger.info(f"Connected to sandboxed.sh at {self.base_url}")
                return True
            else:
                self.connection.error = f"Health check failed: {response.status_code}"
                logger.warning(f"Health check returned {response.status_code}")
                return False
                
        except httpx.ConnectError as e:
            self.connection.error = f"Failed to connect: {str(e)}"
            logger.error(f"Connection error to {self.base_url}: {e}")
            return False
        except Exception as e:
            self.connection.error = f"Initialization error: {str(e)}"
            logger.error(f"Failed to initialize connection: {e}", exc_info=True)
            return False

    async def send_message(
        self,
        content: str,
        agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send message to sandboxed.sh agent.
        
        Args:
            content: Message content (non-empty)
            agent: Optional agent name (e.g., 'coder', 'researcher')
            
        Returns:
            Response dict with message ID and mission ID
            
        Raises:
            RuntimeError: If not connected or request fails
            ValueError: If content is empty
        """
        if not content or not isinstance(content, str) or not content.strip():
            raise ValueError("content must be a non-empty string")
        
        if not self.connection.connected or not self.connection.client:
            raise RuntimeError("Not connected to sandboxed.sh")
        
        try:
            payload: Dict[str, Any] = {"content": content.strip()}
            if agent:
                payload["agent"] = agent
            
            response = await self.connection.client.post(
                "/api/control/message",
                json=payload
            )
            
            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to send message: {response.status_code} - {response.text}"
                )
            
            data = response.json()
            self.connection.mission_id = data.get("mission_id")
            
            logger.debug(f"Message sent: {data.get('id')}, mission: {self.connection.mission_id}")
            return data
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending message: {e}", exc_info=True)
            raise RuntimeError(f"HTTP error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to send message: {e}", exc_info=True)
            raise RuntimeError(f"Message send failed: {e}") from e

    async def stream_events(self) -> AsyncIterator[Dict[str, Any]]:
        """Stream events from sandboxed.sh via SSE.
        
        Yields:
            Event dict with "type" field and event-specific payload
            
        Raises:
            RuntimeError: If not connected or stream fails
        """
        if not self.connection.connected or not self.connection.client:
            raise RuntimeError("Not connected to sandboxed.sh")
        
        try:
            async with self.connection.client.stream(
                "GET",
                "/api/control/stream",
                headers={"Accept": "text/event-stream"}
            ) as response:
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Stream connection failed: {response.status_code}"
                    )
                
                logger.info("SSE stream connected")
                
                async for line in response.aiter_lines():
                    if not line or line.startswith(":"):
                        continue
                    
                    # Parse SSE format: "data: {json}"
                    if line.startswith("data: "):
                        try:
                            json_str = line[6:].strip()
                            event_data = json.loads(json_str)
                            
                            # Ensure "type" field exists
                            if "type" not in event_data:
                                logger.warning(f"Event missing type field: {event_data}")
                                continue
                            
                            logger.debug(f"Event: {event_data.get('type')}")
                            yield event_data
                            
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse event JSON: {line}: {e}")
                            continue
                    
        except httpx.StreamClosed:
            logger.info("Stream closed")
        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            raise RuntimeError(f"Stream error: {e}") from e

    async def handle_tool_call(
        self,
        tool_call_id: str,
        name: str,
        args: Dict[str, Any]
    ) -> Optional[asyncio.Future]:
        """Process tool_call event.
        
        Args:
            tool_call_id: Unique identifier for the tool call
            name: Tool name
            args: Tool arguments
            
        Returns:
            Future object for tracking tool result
        """
        future: asyncio.Future = asyncio.Future()
        self.connection.pending_tool_calls[tool_call_id] = future
        
        logger.debug(f"Tool call received: {name} (id: {tool_call_id})")
        logger.debug(f"Tool arguments: {args}")
        
        return future

    async def submit_tool_result(
        self,
        tool_call_id: str,
        result: str
    ) -> bool:
        """Submit tool result via POST.
        
        Args:
            tool_call_id: ID from ToolCall event
            result: Tool execution output/result
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            RuntimeError: If not connected or request fails
        """
        if not self.connection.connected or not self.connection.client:
            raise RuntimeError("Not connected to sandboxed.sh")
        
        try:
            response = await self.connection.client.post(
                "/api/control/tool_result",
                json={
                    "tool_call_id": tool_call_id,
                    "result": result
                }
            )
            
            if response.status_code != 200:
                logger.error(
                    f"Failed to submit tool result: {response.status_code} - {response.text}"
                )
                return False
            
            data = response.json()
            success = data.get("success", False)
            
            # Resolve pending future if exists
            if tool_call_id in self.connection.pending_tool_calls:
                future = self.connection.pending_tool_calls[tool_call_id]
                if not future.done():
                    future.set_result({"success": success, "result": result})
                del self.connection.pending_tool_calls[tool_call_id]
            
            logger.debug(f"Tool result submitted for {tool_call_id}: success={success}")
            return success
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error submitting tool result: {e}", exc_info=True)
            raise RuntimeError(f"HTTP error: {e}") from e
        except Exception as e:
            logger.error(f"Failed to submit tool result: {e}", exc_info=True)
            raise RuntimeError(f"Tool result submission failed: {e}") from e

    async def list_tools(self) -> List[MCPTool]:
        """List available tools.
        
        Returns:
            List of MCPTool objects
        """
        return self.connection.tools

    async def cleanup(self) -> None:
        """Clean up resources.
        
        Closes HTTP client and cancels stream task.
        """
        if self.stream_task and not self.stream_task.done():
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass
        
        if self.connection.client:
            await self.connection.client.aclose()
            self.connection.connected = False
            logger.info("Connection closed")

    def __del__(self) -> None:
        """Cleanup on deletion."""
        if self.connection.connected:
            try:
                # Note: Can't use await in __del__, schedule cleanup instead
                if asyncio.get_event_loop().is_running():
                    asyncio.create_task(self.cleanup())
                else:
                    asyncio.run(self.cleanup())
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")


async def create_mcp_server(
    base_url: str = "http://localhost:3000"
) -> Optional[SandboxedShMCPServer]:
    """Factory function to create and initialize MCP server.
    
    Args:
        base_url: Base URL for sandboxed.sh control API
        
    Returns:
        Initialized SandboxedShMCPServer or None if initialization fails
    """
    server = SandboxedShMCPServer(base_url=base_url)
    
    if await server.initialize():
        return server
    else:
        await server.cleanup()
        return None


# Demo usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def demo():
        """Demo of MCP server functionality."""
        server = await create_mcp_server()
        
        if not server:
            logger.error("Failed to create MCP server")
            return
        
        try:
            # List available tools
            tools = await server.list_tools()
            logger.info(f"Available tools: {[t.name for t in tools]}")
            
            # Send a message
            response = await server.send_message(
                content="Execute bash: echo 'Hello from sandboxed.sh'",
                agent="coder"
            )
            logger.info(f"Message sent: {response}")
            
            # Start streaming events
            logger.info("Starting event stream...")
            async for event in server.stream_events():
                logger.info(f"Event received: {event.get('type')}")
                
                # Handle tool calls
                if event.get("type") == "tool_call":
                    tool_call_id = event.get("tool_call_id")
                    tool_name = event.get("name")
                    tool_args = event.get("args", {})
                    
                    logger.info(
                        f"Tool call: {tool_name} (id: {tool_call_id}, args: {tool_args})"
                    )
                    
                    # Create a future for tracking
                    future = await server.handle_tool_call(
                        tool_call_id,
                        tool_name,
                        tool_args
                    )
                    
                    # Submit result
                    result = f"Simulated result from {tool_name}"
                    success = await server.submit_tool_result(tool_call_id, result)
                    logger.info(f"Tool result submitted: {success}")
                
                # Stop after assistant message
                if event.get("type") == "assistant_message":
                    logger.info("Assistant message received, stopping stream")
                    break
        
        finally:
            await server.cleanup()
    
    asyncio.run(demo())
