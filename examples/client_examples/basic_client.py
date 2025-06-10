"""
Basic MCP Client Example

This example demonstrates how to create a simple MCP client that can connect
to and interact with MCP servers programmatically.

This is useful for:
- Testing MCP servers
- Automated interactions
- Building custom integrations
- Understanding the MCP protocol
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

# Note: These imports may need to be adjusted based on the MCP SDK version
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    print("MCP SDK not available. Install with: pip install mcp")
    MCP_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPClientExample:
    """Example MCP client for interacting with servers"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
    
    async def connect_to_server(self, command: str, args: List[str], cwd: Optional[str] = None):
        """Connect to an MCP server via stdio"""
        if not MCP_AVAILABLE:
            raise RuntimeError("MCP SDK not available")
        
        logger.info(f"Connecting to server: {command} {' '.join(args)}")
        
        # Create server parameters
        server_params = StdioServerParameters(
            command=command,
            args=args,
            cwd=cwd
        )
        
        # Connect to the server
        stdio_transport = stdio_client(server_params)
        read_stream, write_stream = await stdio_transport.__aenter__()
        
        # Create client session
        self.session = ClientSession(read_stream, write_stream)
        await self.session.initialize()
        
        logger.info("Connected to MCP server successfully")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the server"""
        if not self.session:
            raise RuntimeError("Not connected to a server")
        
        response = await self.session.list_tools()
        return [tool.dict() for tool in response.tools]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool on the server"""
        if not self.session:
            raise RuntimeError("Not connected to a server")
        
        logger.info(f"Calling tool: {name} with args: {arguments}")
        
        response = await self.session.call_tool(name, arguments)
        
        # Extract text content from response
        content_parts = []
        for content in response.content:
            if hasattr(content, 'text'):
                content_parts.append(content.text)
        
        return '\n'.join(content_parts)
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources from the server"""
        if not self.session:
            raise RuntimeError("Not connected to a server")
        
        response = await self.session.list_resources()
        return [resource.dict() for resource in response.resources]
    
    async def get_resource(self, uri: str) -> str:
        """Get a resource from the server"""
        if not self.session:
            raise RuntimeError("Not connected to a server")
        
        logger.info(f"Getting resource: {uri}")
        
        response = await self.session.get_resource(uri)
        
        # Extract text content from response
        content_parts = []
        for content in response.contents:
            if hasattr(content, 'text'):
                content_parts.append(content.text)
        
        return '\n'.join(content_parts)
    
    async def disconnect(self):
        """Disconnect from the server"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Disconnected from MCP server")


async def demo_basic_server():
    """Demonstrate interaction with the basic server"""
    print("\n" + "="*50)
    print("Basic Server Demo")
    print("="*50)
    
    client = MCPClientExample()
    
    try:
        # Connect to basic server
        await client.connect_to_server("python", ["-m", "src.basic_server"])
        
        # List available tools
        print("\n📋 Available Tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  • {tool['name']}: {tool['description']}")
        
        # Test calculator tool
        print("\n🧮 Testing Calculator:")
        result = await client.call_tool("calculate", {
            "operation": "add",
            "a": 15,
            "b": 27
        })
        print(f"Result: {result}")
        
        # Test greeting tool
        print("\n👋 Testing Greeting:")
        result = await client.call_tool("greet", {
            "name": "Alice",
            "style": "enthusiastic"
        })
        print(f"Result: {result}")
        
        # List and get resources
        print("\n📚 Available Resources:")
        resources = await client.list_resources()
        for resource in resources:
            print(f"  • {resource['name']}: {resource['description']}")
        
        # Get current time resource
        print("\n🕐 Current Time:")
        time_resource = await client.get_resource("time://current")
        print(f"Result: {time_resource}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()


async def demo_task_manager():
    """Demonstrate interaction with the task manager"""
    print("\n" + "="*50)
    print("Task Manager Demo")
    print("="*50)
    
    client = MCPClientExample()
    
    try:
        # Connect to task manager
        await client.connect_to_server("python", ["-m", "src.task_manager"])
        
        # Create a task
        print("\n➕ Creating a new task:")
        result = await client.call_tool("create_task", {
            "title": "Learn MCP Protocol",
            "description": "Study the Model Context Protocol documentation and examples",
            "category": "work",
            "priority": "high",
            "due_date": "2024-12-31"
        })
        print(f"Result: {result}")
        
        # List all tasks
        print("\n📋 Listing all tasks:")
        result = await client.call_tool("list_tasks", {})
        print(f"Result: {result}")
        
        # Get task statistics
        print("\n📊 Task Statistics:")
        result = await client.call_tool("get_task_stats", {})
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()


async def demo_weather_service():
    """Demonstrate interaction with the weather service"""
    print("\n" + "="*50)
    print("Weather Service Demo")
    print("="*50)
    
    client = MCPClientExample()
    
    try:
        # Connect to weather service
        await client.connect_to_server("python", ["-m", "src.weather_service"])
        
        # Get current weather
        print("\n🌤️ Getting weather for London:")
        result = await client.call_tool("get_current_weather", {
            "location": "London,UK",
            "units": "metric"
        })
        print(f"Result: {result}")
        
        # Get weather by coordinates (New York City)
        print("\n🗽 Getting weather by coordinates (NYC):")
        result = await client.call_tool("get_weather_by_coordinates", {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "units": "imperial"
        })
        print(f"Result: {result}")
        
        # Get API information
        print("\n📡 Weather API Info:")
        api_info = await client.get_resource("weather://api-info")
        print(f"Result: {api_info}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()


async def interactive_demo():
    """Interactive demo allowing user to choose operations"""
    print("\n" + "="*60)
    print("Interactive MCP Client Demo")
    print("="*60)
    
    while True:
        print("\nChoose a demo:")
        print("1. Basic Server Demo")
        print("2. Task Manager Demo") 
        print("3. Weather Service Demo")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            await demo_basic_server()
        elif choice == "2":
            await demo_task_manager()
        elif choice == "3":
            await demo_weather_service()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-4.")


async def run_all_demos():
    """Run all demos in sequence"""
    print("🚀 Running All MCP Server Demos")
    print("="*60)
    
    await demo_basic_server()
    await demo_task_manager()
    await demo_weather_service()
    
    print("\n" + "="*60)
    print("✅ All demos completed!")
    print("="*60)


def main():
    """Main function"""
    if not MCP_AVAILABLE:
        print("❌ MCP SDK not available. Please install with: pip install mcp")
        return
    
    print("🔧 MCP Client Examples")
    print("This demonstrates how to interact with MCP servers programmatically.")
    print()
    
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            asyncio.run(run_all_demos())
        elif sys.argv[1] == "--basic":
            asyncio.run(demo_basic_server())
        elif sys.argv[1] == "--tasks":
            asyncio.run(demo_task_manager())
        elif sys.argv[1] == "--weather":
            asyncio.run(demo_weather_service())
        else:
            print("Usage: python client_example.py [--all|--basic|--tasks|--weather]")
    else:
        asyncio.run(interactive_demo())


if __name__ == "__main__":
    main()
