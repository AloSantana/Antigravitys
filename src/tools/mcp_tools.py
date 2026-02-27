"""
MCP helper tools for agent use.

These tools provide convenient access to MCP server information
and tool discovery for agents.
"""

from typing import Dict, Any, List
import asyncio
from src.mcp_client import MCPClientManagerSync


# Global MCP client instance (lazy initialization)
_mcp_client = None


def _get_mcp_client() -> MCPClientManagerSync:
    """Get or initialize the global MCP client."""
    global _mcp_client
    
    if _mcp_client is None:
        _mcp_client = MCPClientManagerSync()
        _mcp_client.initialize()
    
    return _mcp_client


def list_mcp_servers() -> str:
    """
    List all configured MCP servers and their connection status.
    
    Returns:
        Formatted string with server information
    """
    try:
        client = _get_mcp_client()
        status = client.get_status()
        
        if not status.get("initialized"):
            return "MCP is not initialized or disabled."
        
        servers = status.get("servers", {})
        
        if not servers:
            return "No MCP servers configured."
        
        lines = ["MCP Servers:\n"]
        
        for name, info in servers.items():
            status_icon = "✓" if info["connected"] else "✗"
            lines.append(f"{status_icon} {name}")
            lines.append(f"  Transport: {info['transport']}")
            lines.append(f"  Tools: {info['tools_count']}")
            
            if info.get("error"):
                lines.append(f"  Error: {info['error']}")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error listing MCP servers: {str(e)}"


def list_mcp_tools(server_name: str = "") -> str:
    """
    List all available MCP tools, optionally filtered by server.
    
    Args:
        server_name: Optional server name to filter tools
        
    Returns:
        Formatted string with tool information
    """
    try:
        client = _get_mcp_client()
        tools = client.get_all_tools()
        
        if not tools:
            return "No MCP tools available."
        
        # Filter by server if specified
        if server_name:
            tools = [t for t in tools if t.server_name == server_name]
            
            if not tools:
                return f"No tools found for server: {server_name}"
        
        lines = [f"Available MCP Tools ({len(tools)}):\n"]
        
        for tool in tools:
            lines.append(f"• {tool.get_prefixed_name()}")
            lines.append(f"  Server: {tool.server_name}")
            lines.append(f"  Description: {tool.description}")
            
            # Show parameters if available
            if tool.input_schema:
                properties = tool.input_schema.get("properties", {})
                if properties:
                    params = ", ".join(properties.keys())
                    lines.append(f"  Parameters: {params}")
            
            lines.append("")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error listing MCP tools: {str(e)}"


def get_mcp_tool_help(tool_name: str) -> str:
    """
    Get detailed help for a specific MCP tool.
    
    Args:
        tool_name: Name of the tool (with or without mcp_ prefix)
        
    Returns:
        Detailed tool information
    """
    try:
        client = _get_mcp_client()
        tools = client.get_all_tools()
        
        # Find the tool
        tool = None
        for t in tools:
            if t.get_prefixed_name() == tool_name or t.original_name == tool_name:
                tool = t
                break
        
        if not tool:
            return f"Tool not found: {tool_name}"
        
        lines = [
            f"Tool: {tool.get_prefixed_name()}",
            f"Original Name: {tool.original_name}",
            f"Server: {tool.server_name}",
            f"Description: {tool.description}",
            ""
        ]
        
        # Show detailed schema
        if tool.input_schema:
            lines.append("Input Schema:")
            
            properties = tool.input_schema.get("properties", {})
            required = tool.input_schema.get("required", [])
            
            for param_name, param_info in properties.items():
                param_type = param_info.get("type", "unknown")
                param_desc = param_info.get("description", "")
                is_required = " (required)" if param_name in required else " (optional)"
                
                lines.append(f"  • {param_name}: {param_type}{is_required}")
                
                if param_desc:
                    lines.append(f"    {param_desc}")
        else:
            lines.append("No input schema available.")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error getting tool help: {str(e)}"


def mcp_health_check() -> Dict[str, Any]:
    """
    Perform a health check on all MCP servers.
    
    Returns:
        Dictionary with health status
    """
    try:
        client = _get_mcp_client()
        status = client.get_status()
        
        health = {
            "healthy": status.get("initialized", False),
            "total_servers": len(status.get("servers", {})),
            "connected_servers": 0,
            "total_tools": status.get("total_tools", 0),
            "servers": {}
        }
        
        for name, info in status.get("servers", {}).items():
            is_connected = info.get("connected", False)
            
            if is_connected:
                health["connected_servers"] += 1
            
            health["servers"][name] = {
                "connected": is_connected,
                "tools_count": info.get("tools_count", 0),
                "error": info.get("error")
            }
        
        return health
        
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e)
        }


# Example usage functions for testing
def test_mcp_tools():
    """Test function to verify MCP tools are working."""
    print("=" * 50)
    print("MCP Tools Test")
    print("=" * 50)
    
    print("\n1. Listing MCP Servers:")
    print(list_mcp_servers())
    
    print("\n2. Listing All MCP Tools:")
    print(list_mcp_tools())
    
    print("\n3. Health Check:")
    health = mcp_health_check()
    print(f"Healthy: {health['healthy']}")
    print(f"Connected Servers: {health['connected_servers']}/{health['total_servers']}")
    print(f"Total Tools: {health['total_tools']}")


if __name__ == "__main__":
    test_mcp_tools()
