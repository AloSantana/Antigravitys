"""
MCP (Model Context Protocol) Client Manager for Antigravity Workspace.

This module provides a comprehensive client for connecting to and managing
MCP servers via stdio, HTTP, and SSE transports.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from src.config import settings, MCPServerConfig

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
class MCPServerConnection:
    """Represents a connection to an MCP server."""
    config: MCPServerConfig
    session: Optional[Any] = None
    read_stream: Optional[Any] = None
    write_stream: Optional[Any] = None
    tools: List[MCPTool] = field(default_factory=list)
    connected: bool = False
    error: Optional[str] = None


class MCPClientManager:
    """
    Manages connections to multiple MCP servers and provides unified tool access.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the MCP client manager.
        
        Args:
            config_path: Path to mcp_servers.json config file
        """
        self.config_path = config_path or settings.MCP_SERVERS_CONFIG
        self.servers: Dict[str, MCPServerConnection] = {}
        self.all_tools: Dict[str, MCPTool] = {}
        self._initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize all MCP server connections.
        
        Returns:
            True if at least one server connected successfully
        """
        if not settings.MCP_ENABLED:
            logger.info("MCP is disabled in settings")
            return False
            
        if not os.path.exists(self.config_path):
            logger.warning(f"MCP config file not found: {self.config_path}")
            return False
        
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            servers_config = config_data.get("mcpServers", {})
            
            # Connect to each server
            tasks = []
            for name, server_cfg in servers_config.items():
                if server_cfg.get("enabled", True):
                    # Gracefully skip servers whose required env vars are missing
                    server_env = server_cfg.get("env", {})
                    missing_env_vars = [
                        ref[2:-1]
                        for ref in server_env.values()
                        if isinstance(ref, str) and ref.startswith("${") and ref.endswith("}")
                        and not os.getenv(ref[2:-1])
                    ]
                    if missing_env_vars:
                        logger.info(
                            f"Skipping MCP server '{name}': required env vars not set: "
                            f"{missing_env_vars}"
                        )
                        continue
                    config = MCPServerConfig(
                        name=name,
                        transport=server_cfg.get("transport", "stdio"),
                        command=server_cfg.get("command"),
                        args=server_cfg.get("args", []),
                        url=server_cfg.get("url"),
                        env=server_cfg.get("env", {}),
                        enabled=True
                    )
                    tasks.append(self._connect_server(config))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Discover tools from connected servers
            for server in self.servers.values():
                if server.connected:
                    await self._discover_tools(server)
            
            self._initialized = len([s for s in self.servers.values() if s.connected]) > 0
            
            if self._initialized:
                logger.info(f"MCP initialized with {len(self.servers)} servers, {len(self.all_tools)} tools")
            
            return self._initialized
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            return False
    
    async def _connect_server(self, config: MCPServerConfig):
        """Connect to a single MCP server."""
        connection = MCPServerConnection(config=config)
        self.servers[config.name] = connection
        
        try:
            if config.transport == "stdio":
                await self._connect_stdio(connection)
            elif config.transport == "http":
                await self._connect_http(connection)
            elif config.transport == "sse":
                await self._connect_sse(connection)
            else:
                connection.error = f"Unknown transport: {config.transport}"
                logger.error(connection.error)
                
        except Exception as e:
            connection.error = str(e)
            logger.error(f"Failed to connect to {config.name}: {e}")
    
    async def _connect_stdio(self, connection: MCPServerConnection):
        """Connect to an MCP server via stdio."""
        config = connection.config
        
        if not config.command:
            raise ValueError(f"No command specified for stdio server {config.name}")
        
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(config.env)
            
            # Start the process
            process = await asyncio.create_subprocess_exec(
                config.command,
                *config.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            connection.session = process
            connection.read_stream = process.stdout
            connection.write_stream = process.stdin
            connection.connected = True
            
            logger.info(f"Connected to {config.name} via stdio")
            
        except Exception as e:
            raise RuntimeError(f"Failed to start stdio server {config.name}: {e}")
    
    async def _connect_http(self, connection: MCPServerConnection):
        """Connect to an MCP server via HTTP."""
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx is required for HTTP transport")
        
        config = connection.config
        
        if not config.url:
            raise ValueError(f"No URL specified for HTTP server {config.name}")
        
        try:
            client = httpx.AsyncClient(timeout=settings.MCP_CONNECTION_TIMEOUT)
            
            # Test connection with a health check
            response = await client.get(f"{config.url}/health")
            
            if response.status_code == 200:
                connection.session = client
                connection.connected = True
                logger.info(f"Connected to {config.name} via HTTP at {config.url}")
            else:
                raise RuntimeError(f"Health check failed with status {response.status_code}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to connect to HTTP server {config.name}: {e}")
    
    async def _connect_sse(self, connection: MCPServerConnection):
        """Connect to an MCP server via Server-Sent Events."""
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx is required for SSE transport")
        
        config = connection.config
        
        if not config.url:
            raise ValueError(f"No URL specified for SSE server {config.name}")
        
        try:
            client = httpx.AsyncClient(timeout=settings.MCP_CONNECTION_TIMEOUT)
            
            # SSE connections are typically long-lived
            connection.session = client
            connection.connected = True
            logger.info(f"Connected to {config.name} via SSE at {config.url}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to connect to SSE server {config.name}: {e}")
    
    async def _discover_tools(self, connection: MCPServerConnection):
        """Discover tools available from a connected server."""
        try:
            # For stdio, send a list_tools request
            if connection.config.transport == "stdio":
                tools = await self._discover_stdio_tools(connection)
            elif connection.config.transport in ["http", "sse"]:
                tools = await self._discover_http_tools(connection)
            else:
                tools = []
            
            # Register discovered tools
            for tool_data in tools:
                tool = MCPTool(
                    name=tool_data.get("name", ""),
                    description=tool_data.get("description", ""),
                    server_name=connection.config.name,
                    input_schema=tool_data.get("inputSchema", {}),
                    original_name=tool_data.get("name", "")
                )
                
                prefixed_name = tool.get_prefixed_name()
                connection.tools.append(tool)
                self.all_tools[prefixed_name] = tool
            
            logger.info(f"Discovered {len(tools)} tools from {connection.config.name}")
            
        except Exception as e:
            logger.error(f"Failed to discover tools from {connection.config.name}: {e}")
    
    async def _discover_stdio_tools(self, connection: MCPServerConnection) -> List[Dict[str, Any]]:
        """Discover tools from a stdio server."""
        # Simplified implementation - would need full JSON-RPC protocol
        # For now, return empty list as placeholder
        return []
    
    async def _discover_http_tools(self, connection: MCPServerConnection) -> List[Dict[str, Any]]:
        """Discover tools from an HTTP/SSE server."""
        try:
            if connection.session:
                response = await connection.session.get(f"{connection.config.url}/tools")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("tools", [])
        except Exception as e:
            logger.error(f"Failed to discover HTTP tools: {e}")
        
        return []
    
    def get_all_tools(self) -> List[MCPTool]:
        """Get all discovered tools from all servers."""
        return list(self.all_tools.values())
    
    def get_all_tools_as_callables(self) -> Dict[str, Callable]:
        """
        Get all tools as callable functions.
        
        Returns:
            Dictionary of tool_name -> callable function
        """
        callables = {}
        
        for tool_name, tool in self.all_tools.items():
            callables[tool_name] = self._create_tool_wrapper(tool)
        
        return callables
    
    def _create_tool_wrapper(self, tool: MCPTool) -> Callable:
        """Create an async callable wrapper for a tool."""
        
        async def tool_wrapper(**kwargs) -> Any:
            """Async wrapper for MCP tool."""
            return await self.call_tool(tool.get_prefixed_name(), kwargs)
        
        # Add metadata to the wrapper
        tool_wrapper.__name__ = tool.get_prefixed_name()
        tool_wrapper.__doc__ = tool.description
        tool_wrapper._mcp_tool = tool
        
        return tool_wrapper
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool by name with the given arguments.
        
        Args:
            tool_name: Prefixed tool name (e.g., "mcp_filesystem_read_file")
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        tool = self.all_tools.get(tool_name)
        
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        server = self.servers.get(tool.server_name)
        
        if not server or not server.connected:
            raise RuntimeError(f"Server {tool.server_name} not connected")
        
        try:
            # Execute tool based on transport
            if server.config.transport == "stdio":
                result = await self._call_stdio_tool(server, tool, arguments)
            elif server.config.transport in ["http", "sse"]:
                result = await self._call_http_tool(server, tool, arguments)
            else:
                raise ValueError(f"Unknown transport: {server.config.transport}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise
    
    async def _call_stdio_tool(
        self,
        server: MCPServerConnection,
        tool: MCPTool,
        arguments: Dict[str, Any]
    ) -> Any:
        """Call a tool on a stdio server."""
        # Simplified - would need full JSON-RPC implementation
        raise NotImplementedError("Stdio tool calls not fully implemented")
    
    async def _call_http_tool(
        self,
        server: MCPServerConnection,
        tool: MCPTool,
        arguments: Dict[str, Any]
    ) -> Any:
        """Call a tool on an HTTP/SSE server."""
        if not server.session:
            raise RuntimeError("Server session not available")
        
        try:
            response = await server.session.post(
                f"{server.config.url}/tools/{tool.original_name}",
                json=arguments
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise RuntimeError(f"Tool call failed with status {response.status_code}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to call HTTP tool: {e}")
    
    def get_tool_descriptions(self) -> str:
        """
        Get formatted descriptions of all available tools for agent prompts.
        
        Returns:
            Formatted string describing all tools
        """
        if not self.all_tools:
            return "No MCP tools available."
        
        descriptions = ["Available MCP Tools:\n"]
        
        for tool_name, tool in self.all_tools.items():
            descriptions.append(f"- {tool_name}: {tool.description}")
            
            # Add input schema info if available
            if tool.input_schema:
                properties = tool.input_schema.get("properties", {})
                if properties:
                    params = ", ".join(properties.keys())
                    descriptions.append(f"  Parameters: {params}")
        
        return "\n".join(descriptions)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get status information about all servers and tools.
        
        Returns:
            Dictionary with server and tool status
        """
        server_status = {}
        
        for name, server in self.servers.items():
            server_status[name] = {
                "connected": server.connected,
                "transport": server.config.transport,
                "tools_count": len(server.tools),
                "error": server.error
            }
        
        return {
            "initialized": self._initialized,
            "servers": server_status,
            "total_tools": len(self.all_tools),
            "tool_names": list(self.all_tools.keys())
        }
    
    async def shutdown(self):
        """Gracefully shutdown all server connections."""
        for server in self.servers.values():
            if server.connected:
                try:
                    if server.config.transport == "stdio":
                        if server.session and hasattr(server.session, 'terminate'):
                            server.session.terminate()
                            await server.session.wait()
                    elif server.config.transport in ["http", "sse"]:
                        if server.session and hasattr(server.session, 'aclose'):
                            await server.session.aclose()
                    
                    server.connected = False
                    
                except Exception as e:
                    logger.error(f"Error shutting down server {server.config.name}: {e}")
        
        logger.info("MCP client manager shut down")


class MCPClientManagerSync:
    """
    Synchronous wrapper for MCPClientManager for non-async contexts.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.manager = MCPClientManager(config_path)
        self._loop = None
    
    def initialize(self) -> bool:
        """Initialize all MCP server connections synchronously."""
        return self._run_async(self.manager.initialize())
    
    def get_all_tools(self) -> List[MCPTool]:
        """Get all discovered tools from all servers."""
        return self.manager.get_all_tools()
    
    def get_tool_descriptions(self) -> str:
        """Get formatted descriptions of all available tools."""
        return self.manager.get_tool_descriptions()
    
    def get_status(self) -> Dict[str, Any]:
        """Get status information about all servers and tools."""
        return self.manager.get_status()
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool synchronously."""
        return self._run_async(self.manager.call_tool(tool_name, arguments))
    
    def shutdown(self):
        """Shutdown all server connections synchronously."""
        self._run_async(self.manager.shutdown())
    
    def _run_async(self, coro):
        """Helper to run async code in sync context."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
