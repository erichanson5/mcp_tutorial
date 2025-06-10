"""
Simple test script to verify MCP installation and basic functionality.
"""

def test_basic_import():
    """Test if we can import basic MCP components."""
    try:
        import mcp
        print("✓ MCP core module imported successfully")
        
        from mcp.types import Tool, TextContent, ListToolsRequest
        print("✓ MCP types imported successfully")
        
        # Test creating a basic tool
        tool = Tool(
            name="test_tool",
            description="A test tool",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
        print(f"✓ Created tool: {tool.name}")
        
        return True
    except Exception as e:
        print(f"✗ Error importing MCP: {e}")
        return False

def test_server_imports():
    """Test if we can import server components."""
    try:
        from mcp.server import Server
        print("✓ MCP Server imported successfully")
        
        # Create a basic server instance
        server = Server("test-server")
        print(f"✓ Created server: {server.name}")
        
        return True
    except Exception as e:
        print(f"✗ Error importing MCP server: {e}")
        return False

if __name__ == "__main__":
    print("Testing MCP installation...")
    print("-" * 40)
    
    basic_ok = test_basic_import()
    print()
    
    server_ok = test_server_imports()
    print()
    
    if basic_ok and server_ok:
        print("✓ All tests passed! MCP is properly installed.")
    else:
        print("✗ Some tests failed. There may be compatibility issues.")
