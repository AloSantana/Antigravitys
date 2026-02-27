"""
Comprehensive tests for the MCP (Model Context Protocol) client system.

Tests:
- MCPTool dataclass
- MCPServerConnection
- MCPClientManager initialization
- Tool discovery (mocked)
- Server connections (stdio, HTTP, SSE)
- Tool execution (mocked)
- Error handling
"""

import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock

from src.mcp_client import (
    MCPTool,
    MCPServerConnection,
    MCPClientManager,
    MCPClientManagerSync
)
from src.config import MCPServerConfig


# =============================================================================
# MCPTool Tests
# =============================================================================

class TestMCPTool:
    """Test MCPTool dataclass."""
    
    def test_mcp_tool_creation(self):
        """Test creating an MCPTool."""
        tool = MCPTool(
            name="read_file",
            description="Read a file from the filesystem",
            server_name="filesystem",
            input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
            original_name="read_file"
        )
        
        assert tool.name == "read_file"
        assert tool.description == "Read a file from the filesystem"
        assert tool.server_name == "filesystem"
        assert tool.original_name == "read_file"
        assert "path" in tool.input_schema["properties"]
    
    def test_get_prefixed_name(self):
        """Test getting prefixed tool name."""
        with patch('src.config.settings') as mock_settings:
            mock_settings.MCP_TOOL_PREFIX = "mcp_"
            
            tool = MCPTool(
                name="search",
                description="Search tool",
                server_name="web",
                input_schema={},
                original_name="search"
            )
            
            prefixed_name = tool.get_prefixed_name()
            
            assert prefixed_name == "mcp_web_search"
    
    def test_mcp_tool_with_complex_schema(self):
        """Test MCPTool with complex input schema."""
        schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "default": 10},
                "filters": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"}
                    }
                }
            },
            "required": ["query"]
        }
        
        tool = MCPTool(
            name="search",
            description="Search",
            server_name="test",
            input_schema=schema,
            original_name="search"
        )
        
        assert tool.input_schema["required"] == ["query"]
        assert "limit" in tool.input_schema["properties"]


# =============================================================================
# MCPServerConnection Tests
# =============================================================================

class TestMCPServerConnection:
    """Test MCPServerConnection dataclass."""
    
    def test_server_connection_creation(self):
        """Test creating a server connection."""
        config = MCPServerConfig(
            name="test-server",
            transport="stdio",
            command="npx",
            args=["mcp-server"]
        )
        
        connection = MCPServerConnection(config=config)
        
        assert connection.config == config
        assert connection.session is None
        assert connection.tools == []
        assert connection.connected is False
        assert connection.error is None
    
    def test_server_connection_with_tools(self):
        """Test server connection with tools."""
        config = MCPServerConfig(name="test")
        
        tool1 = MCPTool("tool1", "desc1", "test", {}, "tool1")
        tool2 = MCPTool("tool2", "desc2", "test", {}, "tool2")
        
        connection = MCPServerConnection(
            config=config,
            tools=[tool1, tool2],
            connected=True
        )
        
        assert len(connection.tools) == 2
        assert connection.connected is True
    
    def test_server_connection_with_error(self):
        """Test server connection with error."""
        config = MCPServerConfig(name="test")
        
        connection = MCPServerConnection(
            config=config,
            error="Connection failed"
        )
        
        assert connection.error == "Connection failed"
        assert connection.connected is False


# =============================================================================
# MCPClientManager Initialization Tests
# =============================================================================

class TestMCPClientManagerInitialization:
    """Test MCPClientManager initialization."""
    
    def test_client_manager_initialization(self):
        """Test MCPClientManager initialization."""
        manager = MCPClientManager(config_path="test_config.json")
        
        assert manager.config_path == "test_config.json"
        assert manager.servers == {}
        assert manager.all_tools == {}
        assert manager._initialized is False
    
    def test_client_manager_default_config_path(self):
        """Test default config path from settings."""
        with patch('src.config.settings') as mock_settings:
            mock_settings.MCP_SERVERS_CONFIG = "mcp_servers.json"
            
            manager = MCPClientManager()
            
            assert manager.config_path == "mcp_servers.json"
    
    @pytest.mark.asyncio
    async def test_initialize_mcp_disabled(self):
        """Test initialization when MCP is disabled."""
        with patch('src.config.settings.MCP_ENABLED', False):
            manager = MCPClientManager()
            result = await manager.initialize()
            
            assert result is False
            assert manager._initialized is False
    
    @pytest.mark.asyncio
    async def test_initialize_config_not_found(self):
        """Test initialization when config file not found."""
        with patch('src.config.settings') as mock_settings:
            mock_settings.MCP_ENABLED = True
            
            with patch('os.path.exists', return_value=False):
                manager = MCPClientManager(config_path="nonexistent.json")
                result = await manager.initialize()
                
                assert result is False
    
    @pytest.mark.asyncio
    async def test_initialize_with_empty_config(self, tmp_path):
        """Test initialization with empty config."""
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps({"mcpServers": {}}))
        
        with patch('src.config.settings') as mock_settings:
            mock_settings.MCP_ENABLED = True
            
            manager = MCPClientManager(config_path=str(config_file))
            result = await manager.initialize()
            
            assert result is False  # No servers connected
    
    @pytest.mark.asyncio
    async def test_initialize_with_valid_config(self, tmp_path):
        """Test initialization with valid config."""
        config_data = {
            "mcpServers": {
                "filesystem": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem"],
                    "enabled": True
                }
            }
        }
        
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps(config_data))
        
        with patch('src.config.settings') as mock_settings:
            mock_settings.MCP_ENABLED = True
            
            manager = MCPClientManager(config_path=str(config_file))
            
            # Mock connection methods
            with patch.object(manager, '_connect_server', new=AsyncMock()):
                with patch.object(manager, '_discover_tools', new=AsyncMock()):
                    result = await manager.initialize()
                    
                    # Should have attempted to connect
                    assert "filesystem" in manager.servers


# =============================================================================
# Server Connection Tests
# =============================================================================

class TestServerConnections:
    """Test server connection methods."""
    
    @pytest.mark.asyncio
    async def test_connect_stdio_server(self):
        """Test connecting to stdio server."""
        config = MCPServerConfig(
            name="test",
            transport="stdio",
            command="python",
            args=["server.py"]
        )
        
        manager = MCPClientManager()
        connection = MCPServerConnection(config=config)
        manager.servers["test"] = connection
        
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.stdin = MagicMock()
        mock_process.stdout = MagicMock()
        mock_process.stderr = MagicMock()
        
        with patch('asyncio.create_subprocess_exec', new=AsyncMock(return_value=mock_process)):
            await manager._connect_stdio(connection)
            
            assert connection.connected is True
            assert connection.session == mock_process
    
    @pytest.mark.asyncio
    async def test_connect_stdio_no_command(self):
        """Test connecting to stdio server without command."""
        config = MCPServerConfig(
            name="test",
            transport="stdio",
            command=None  # No command specified
        )
        
        manager = MCPClientManager()
        connection = MCPServerConnection(config=config)
        
        with pytest.raises(ValueError):
            await manager._connect_stdio(connection)
    
    @pytest.mark.asyncio
    async def test_connect_http_server(self):
        """Test connecting to HTTP server."""
        config = MCPServerConfig(
            name="test",
            transport="http",
            url="http://localhost:8080"
        )
        
        manager = MCPClientManager()
        connection = MCPServerConnection(config=config)
        
        # Mock httpx
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        
        with patch('src.mcp_client.HTTPX_AVAILABLE', True):
            with patch('httpx.AsyncClient', return_value=mock_client):
                await manager._connect_http(connection)
                
                assert connection.connected is True
                assert connection.session == mock_client
    
    @pytest.mark.asyncio
    async def test_connect_http_no_url(self):
        """Test connecting to HTTP server without URL."""
        config = MCPServerConfig(
            name="test",
            transport="http",
            url=None
        )
        
        manager = MCPClientManager()
        connection = MCPServerConnection(config=config)
        
        with pytest.raises(ValueError):
            await manager._connect_http(connection)
    
    @pytest.mark.asyncio
    async def test_connect_sse_server(self):
        """Test connecting to SSE server."""
        config = MCPServerConfig(
            name="test",
            transport="sse",
            url="http://localhost:9000/sse"
        )
        
        manager = MCPClientManager()
        connection = MCPServerConnection(config=config)
        
        mock_client = MagicMock()
        
        with patch('src.mcp_client.HTTPX_AVAILABLE', True):
            with patch('httpx.AsyncClient', return_value=mock_client):
                await manager._connect_sse(connection)
                
                assert connection.connected is True
                assert connection.session == mock_client
    
    @pytest.mark.asyncio
    async def test_connect_unknown_transport(self):
        """Test connecting with unknown transport."""
        config = MCPServerConfig(
            name="test",
            transport="unknown"
        )
        
        manager = MCPClientManager()
        connection = MCPServerConnection(config=config)
        manager.servers["test"] = connection
        
        await manager._connect_server(config)
        
        assert connection.error is not None
        assert "Unknown transport" in connection.error


# =============================================================================
# Tool Discovery Tests
# =============================================================================

class TestToolDiscovery:
    """Test tool discovery functionality."""
    
    @pytest.mark.asyncio
    async def test_discover_tools_stdio(self):
        """Test discovering tools from stdio server."""
        config = MCPServerConfig(name="test", transport="stdio")
        connection = MCPServerConnection(config=config, connected=True)
        
        manager = MCPClientManager()
        manager.servers["test"] = connection
        
        # Mock the discovery method
        with patch.object(manager, '_discover_stdio_tools', new=AsyncMock(return_value=[
            {
                "name": "read_file",
                "description": "Read a file",
                "inputSchema": {"type": "object"}
            }
        ])):
            await manager._discover_tools(connection)
            
            assert len(connection.tools) == 1
            assert connection.tools[0].name == "read_file"
    
    @pytest.mark.asyncio
    async def test_discover_tools_http(self):
        """Test discovering tools from HTTP server."""
        config = MCPServerConfig(
            name="test",
            transport="http",
            url="http://localhost:8080"
        )
        connection = MCPServerConnection(config=config, connected=True)
        
        manager = MCPClientManager()
        manager.servers["test"] = connection
        
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tools": [
                {"name": "search", "description": "Search", "inputSchema": {}}
            ]
        }
        
        mock_session = MagicMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        connection.session = mock_session
        
        await manager._discover_tools(connection)
        
        assert len(connection.tools) == 1
        assert connection.tools[0].name == "search"
    
    @pytest.mark.asyncio
    async def test_discover_tools_registers_with_prefix(self):
        """Test that discovered tools are registered with prefix."""
        config = MCPServerConfig(name="test", transport="stdio")
        connection = MCPServerConnection(config=config, connected=True)
        
        manager = MCPClientManager()
        manager.servers["test"] = connection
        
        with patch('src.config.settings') as mock_settings:
            mock_settings.MCP_TOOL_PREFIX = "mcp_"
            
            with patch.object(manager, '_discover_stdio_tools', new=AsyncMock(return_value=[
                {"name": "tool1", "description": "Tool 1", "inputSchema": {}}
            ])):
                await manager._discover_tools(connection)
                
                # Check if tool is registered with prefix
                prefixed_name = "mcp_test_tool1"
                assert prefixed_name in manager.all_tools
    
    @pytest.mark.asyncio
    async def test_discover_tools_handles_errors(self):
        """Test that tool discovery handles errors gracefully."""
        config = MCPServerConfig(name="test", transport="stdio")
        connection = MCPServerConnection(config=config, connected=True)
        
        manager = MCPClientManager()
        manager.servers["test"] = connection
        
        # Mock discovery to raise error
        with patch.object(manager, '_discover_stdio_tools', new=AsyncMock(side_effect=Exception("Discovery failed"))):
            # Should not raise, just log error
            await manager._discover_tools(connection)
            
            assert len(connection.tools) == 0


# =============================================================================
# Tool Execution Tests
# =============================================================================

class TestToolExecution:
    """Test tool execution functionality."""
    
    @pytest.mark.asyncio
    async def test_call_tool_success(self):
        """Test successful tool call."""
        manager = MCPClientManager()
        
        # Setup tool and server
        tool = MCPTool(
            name="test_tool",
            description="Test",
            server_name="test",
            input_schema={},
            original_name="test_tool"
        )
        
        config = MCPServerConfig(name="test", transport="http", url="http://localhost")
        connection = MCPServerConnection(config=config, connected=True)
        
        manager.all_tools["mcp_test_test_tool"] = tool
        manager.servers["test"] = connection
        
        # Mock tool execution
        expected_result = {"status": "success", "data": "result"}
        with patch.object(manager, '_call_http_tool', new=AsyncMock(return_value=expected_result)):
            result = await manager.call_tool("mcp_test_test_tool", {"arg": "value"})
            
            assert result == expected_result
    
    @pytest.mark.asyncio
    async def test_call_tool_not_found(self):
        """Test calling non-existent tool."""
        manager = MCPClientManager()
        
        with pytest.raises(ValueError, match="Tool not found"):
            await manager.call_tool("nonexistent_tool", {})
    
    @pytest.mark.asyncio
    async def test_call_tool_server_not_connected(self):
        """Test calling tool when server not connected."""
        manager = MCPClientManager()
        
        tool = MCPTool(
            name="test_tool",
            description="Test",
            server_name="test",
            input_schema={},
            original_name="test_tool"
        )
        
        config = MCPServerConfig(name="test")
        connection = MCPServerConnection(config=config, connected=False)
        
        manager.all_tools["mcp_test_test_tool"] = tool
        manager.servers["test"] = connection
        
        with pytest.raises(RuntimeError, match="not connected"):
            await manager.call_tool("mcp_test_test_tool", {})
    
    @pytest.mark.asyncio
    async def test_call_http_tool(self):
        """Test calling HTTP tool."""
        manager = MCPClientManager()
        
        tool = MCPTool(
            name="search",
            description="Search",
            server_name="test",
            input_schema={},
            original_name="search"
        )
        
        config = MCPServerConfig(name="test", transport="http", url="http://localhost")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        
        mock_session = MagicMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        
        connection = MCPServerConnection(
            config=config,
            connected=True,
            session=mock_session
        )
        
        result = await manager._call_http_tool(connection, tool, {"query": "test"})
        
        assert result == {"result": "success"}
    
    @pytest.mark.asyncio
    async def test_call_stdio_tool_not_implemented(self):
        """Test that stdio tool calls raise NotImplementedError."""
        manager = MCPClientManager()
        
        tool = MCPTool("test", "test", "test", {}, "test")
        config = MCPServerConfig(name="test", transport="stdio")
        connection = MCPServerConnection(config=config)
        
        with pytest.raises(NotImplementedError):
            await manager._call_stdio_tool(connection, tool, {})


# =============================================================================
# Tool Wrapper Tests
# =============================================================================

class TestToolWrappers:
    """Test tool wrapper functionality."""
    
    def test_get_all_tools_as_callables(self):
        """Test getting all tools as callable functions."""
        manager = MCPClientManager()
        
        tool = MCPTool(
            name="test_tool",
            description="Test tool",
            server_name="test",
            input_schema={},
            original_name="test_tool"
        )
        
        manager.all_tools["mcp_test_test_tool"] = tool
        
        callables = manager.get_all_tools_as_callables()
        
        assert "mcp_test_test_tool" in callables
        assert callable(callables["mcp_test_test_tool"])
    
    def test_tool_wrapper_has_metadata(self):
        """Test that tool wrapper has metadata."""
        manager = MCPClientManager()
        
        tool = MCPTool(
            name="test_tool",
            description="Test description",
            server_name="test",
            input_schema={},
            original_name="test_tool"
        )
        
        wrapper = manager._create_tool_wrapper(tool)
        
        assert wrapper.__doc__ == "Test description"
        assert hasattr(wrapper, '_mcp_tool')
        assert wrapper._mcp_tool == tool


# =============================================================================
# Status and Info Tests
# =============================================================================

class TestStatusAndInfo:
    """Test status and information methods."""
    
    def test_get_all_tools(self):
        """Test getting all tools."""
        manager = MCPClientManager()
        
        tool1 = MCPTool("tool1", "desc1", "server1", {}, "tool1")
        tool2 = MCPTool("tool2", "desc2", "server2", {}, "tool2")
        
        manager.all_tools["mcp_tool1"] = tool1
        manager.all_tools["mcp_tool2"] = tool2
        
        tools = manager.get_all_tools()
        
        assert len(tools) == 2
        assert tool1 in tools
        assert tool2 in tools
    
    def test_get_tool_descriptions(self):
        """Test getting formatted tool descriptions."""
        manager = MCPClientManager()
        
        tool = MCPTool(
            name="read_file",
            description="Read a file from filesystem",
            server_name="filesystem",
            input_schema={
                "properties": {
                    "path": {"type": "string"}
                }
            },
            original_name="read_file"
        )
        
        manager.all_tools["mcp_filesystem_read_file"] = tool
        
        descriptions = manager.get_tool_descriptions()
        
        assert "mcp_filesystem_read_file" in descriptions
        assert "Read a file from filesystem" in descriptions
        assert "path" in descriptions
    
    def test_get_tool_descriptions_empty(self):
        """Test getting tool descriptions when no tools available."""
        manager = MCPClientManager()
        
        descriptions = manager.get_tool_descriptions()
        
        assert "No MCP tools available" in descriptions
    
    def test_get_status(self):
        """Test getting manager status."""
        manager = MCPClientManager()
        manager._initialized = True
        
        config1 = MCPServerConfig(name="server1", transport="stdio")
        config2 = MCPServerConfig(name="server2", transport="http")
        
        connection1 = MCPServerConnection(config=config1, connected=True)
        connection2 = MCPServerConnection(config=config2, connected=False, error="Failed")
        
        manager.servers["server1"] = connection1
        manager.servers["server2"] = connection2
        
        tool1 = MCPTool("tool1", "desc", "server1", {}, "tool1")
        connection1.tools.append(tool1)
        manager.all_tools["mcp_tool1"] = tool1
        
        status = manager.get_status()
        
        assert status["initialized"] is True
        assert "server1" in status["servers"]
        assert status["servers"]["server1"]["connected"] is True
        assert status["servers"]["server1"]["tools_count"] == 1
        assert status["servers"]["server2"]["connected"] is False
        assert status["servers"]["server2"]["error"] == "Failed"
        assert status["total_tools"] == 1


# =============================================================================
# Shutdown Tests
# =============================================================================

class TestShutdown:
    """Test shutdown functionality."""
    
    @pytest.mark.asyncio
    async def test_shutdown_stdio_server(self):
        """Test shutting down stdio server."""
        manager = MCPClientManager()
        
        mock_process = MagicMock()
        mock_process.terminate = MagicMock()
        mock_process.wait = AsyncMock()
        
        config = MCPServerConfig(name="test", transport="stdio")
        connection = MCPServerConnection(
            config=config,
            connected=True,
            session=mock_process
        )
        
        manager.servers["test"] = connection
        
        await manager.shutdown()
        
        mock_process.terminate.assert_called_once()
        assert connection.connected is False
    
    @pytest.mark.asyncio
    async def test_shutdown_http_server(self):
        """Test shutting down HTTP server."""
        manager = MCPClientManager()
        
        mock_client = MagicMock()
        mock_client.aclose = AsyncMock()
        
        config = MCPServerConfig(name="test", transport="http")
        connection = MCPServerConnection(
            config=config,
            connected=True,
            session=mock_client
        )
        
        manager.servers["test"] = connection
        
        await manager.shutdown()
        
        mock_client.aclose.assert_called_once()
        assert connection.connected is False
    
    @pytest.mark.asyncio
    async def test_shutdown_handles_errors(self):
        """Test that shutdown handles errors gracefully."""
        manager = MCPClientManager()
        
        mock_process = MagicMock()
        mock_process.terminate.side_effect = Exception("Shutdown error")
        
        config = MCPServerConfig(name="test", transport="stdio")
        connection = MCPServerConnection(
            config=config,
            connected=True,
            session=mock_process
        )
        
        manager.servers["test"] = connection
        
        # Should not raise
        await manager.shutdown()


# =============================================================================
# Synchronous Wrapper Tests
# =============================================================================

class TestMCPClientManagerSync:
    """Test synchronous wrapper for MCPClientManager."""
    
    def test_sync_manager_initialization(self):
        """Test MCPClientManagerSync initialization."""
        sync_manager = MCPClientManagerSync(config_path="test.json")
        
        assert isinstance(sync_manager.manager, MCPClientManager)
        assert sync_manager.manager.config_path == "test.json"
    
    def test_sync_get_all_tools(self):
        """Test synchronous get_all_tools."""
        sync_manager = MCPClientManagerSync()
        
        tool = MCPTool("test", "desc", "server", {}, "test")
        sync_manager.manager.all_tools["mcp_test"] = tool
        
        tools = sync_manager.get_all_tools()
        
        assert len(tools) == 1
        assert tools[0] == tool
    
    def test_sync_get_tool_descriptions(self):
        """Test synchronous get_tool_descriptions."""
        sync_manager = MCPClientManagerSync()
        
        descriptions = sync_manager.get_tool_descriptions()
        
        assert isinstance(descriptions, str)
    
    def test_sync_get_status(self):
        """Test synchronous get_status."""
        sync_manager = MCPClientManagerSync()
        sync_manager.manager._initialized = True
        
        status = sync_manager.get_status()
        
        assert status["initialized"] is True


# =============================================================================
# Integration Tests
# =============================================================================

class TestMCPIntegration:
    """Integration tests for MCP client system."""
    
    @pytest.mark.asyncio
    async def test_full_mcp_workflow(self, tmp_path):
        """Test complete MCP workflow."""
        # Create config
        config_data = {
            "mcpServers": {
                "test": {
                    "transport": "http",
                    "url": "http://localhost:8080",
                    "enabled": True
                }
            }
        }
        
        config_file = tmp_path / "mcp_config.json"
        config_file.write_text(json.dumps(config_data))
        
        # Initialize manager
        with patch('src.config.settings') as mock_settings:
            mock_settings.MCP_ENABLED = True
            mock_settings.MCP_TOOL_PREFIX = "mcp_"
            
            manager = MCPClientManager(config_path=str(config_file))
            
            # Mock connections
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "tools": [
                    {
                        "name": "search",
                        "description": "Search tool",
                        "inputSchema": {"properties": {"query": {"type": "string"}}}
                    }
                ]
            }
            
            mock_client = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            
            with patch('src.mcp_client.HTTPX_AVAILABLE', True):
                with patch('httpx.AsyncClient', return_value=mock_client):
                    # Initialize
                    result = await manager.initialize()
                    
                    # Verify setup
                    assert result or len(manager.servers) > 0
                    
                    # Get status
                    status = manager.get_status()
                    assert "test" in status["servers"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
