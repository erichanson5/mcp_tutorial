# MCP Client Examples

This directory contains examples of how to create MCP clients that can interact with the tutorial servers programmatically.

## Available Examples

### `basic_client.py`
A comprehensive example showing how to:
- Connect to MCP servers via stdio
- List available tools and resources
- Call tools with parameters
- Handle responses and errors
- Disconnect cleanly

## Running the Examples

### Prerequisites
```bash
pip install mcp
```

### Interactive Mode
```bash
python examples/client_examples/basic_client.py
```

### Run All Demos
```bash
python examples/client_examples/basic_client.py --all
```

### Run Specific Demos
```bash
python examples/client_examples/basic_client.py --basic    # Basic server demo
python examples/client_examples/basic_client.py --tasks    # Task manager demo
python examples/client_examples/basic_client.py --weather  # Weather service demo
```

## Example Output

When you run the basic server demo, you'll see output like:

```
==================================================
Basic Server Demo
==================================================

📋 Available Tools:
  • calculate: Perform basic mathematical calculations
  • greet: Generate a personalized greeting message
  • get_server_info: Get information about the MCP server

🧮 Testing Calculator:
Result: Calculation: 15.0 add 27.0 = 42.0

👋 Testing Greeting:
Result: WOW! Hello there, Alice! So excited to chat with you! 🎉

📚 Available Resources:
  • Current Time: Get the current date and time
  • Server Status: Get current server status and statistics

🕐 Current Time:
Result: Current date and time: 2024-01-15 14:30:25
```

## Client Architecture

The client examples demonstrate:

1. **Connection Management**: How to connect to and disconnect from MCP servers
2. **Tool Discovery**: Listing available tools and their schemas
3. **Tool Execution**: Calling tools with proper parameters
4. **Resource Access**: Reading data from server resources
5. **Error Handling**: Managing connection and execution errors

## Key Components

### MCPClientExample Class
```python
class MCPClientExample:
    async def connect_to_server(self, command, args, cwd=None)
    async def list_tools(self)
    async def call_tool(self, name, arguments)
    async def list_resources(self)
    async def get_resource(self, uri)
    async def disconnect(self)
```

### Demo Functions
- `demo_basic_server()`: Tests basic math and greeting tools
- `demo_task_manager()`: Creates tasks and retrieves statistics
- `demo_weather_service()`: Fetches weather data and API info

## Building Your Own Client

To create your own MCP client:

1. **Install Dependencies**:
   ```bash
   pip install mcp
   ```

2. **Basic Structure**:
   ```python
   from mcp import ClientSession, StdioServerParameters
   from mcp.client.stdio import stdio_client

   async def my_client():
       # Set up server parameters
       server_params = StdioServerParameters(
           command="python",
           args=["-m", "your.server.module"]
       )
       
       # Connect
       stdio_transport = stdio_client(server_params)
       read_stream, write_stream = await stdio_transport.__aenter__()
       
       # Create session
       session = ClientSession(read_stream, write_stream)
       await session.initialize()
       
       # Use the session
       tools = await session.list_tools()
       result = await session.call_tool("tool_name", {"param": "value"})
       
       # Clean up
       await session.close()
   ```

3. **Error Handling**:
   ```python
   try:
       result = await session.call_tool("tool_name", arguments)
   except Exception as e:
       print(f"Tool call failed: {e}")
   ```

## Advanced Usage

### Custom Transport
You can create clients for different transport types:
- stdio (standard input/output)
- HTTP with SSE (Server-Sent Events)
- WebSocket (if supported)

### Concurrent Operations
```python
# Call multiple tools concurrently
tasks = [
    session.call_tool("tool1", args1),
    session.call_tool("tool2", args2),
    session.call_tool("tool3", args3)
]
results = await asyncio.gather(*tasks)
```

### Session Management
```python
class PersistentMCPClient:
    def __init__(self):
        self.session = None
    
    async def ensure_connected(self):
        if not self.session:
            await self.connect()
    
    async def safe_call_tool(self, name, args):
        await self.ensure_connected()
        return await self.session.call_tool(name, args)
```

## Testing Your Servers

These client examples are also useful for testing your own MCP servers:

1. **Unit Testing**: Automated testing of tool functionality
2. **Integration Testing**: End-to-end workflow testing
3. **Performance Testing**: Load and response time testing
4. **Error Testing**: Testing error handling and edge cases

## Next Steps

After exploring these examples:

1. **Modify the Examples**: Experiment with different parameters and tools
2. **Create Custom Clients**: Build clients for your specific use cases
3. **Integrate with Applications**: Use MCP clients in your own applications
4. **Explore Advanced Features**: Look into streaming, notifications, and other MCP features

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure MCP SDK is installed
2. **Connection Failures**: Check server command and arguments
3. **Tool Call Errors**: Verify parameter types and required fields
4. **Timeout Issues**: Some operations may take time (weather API calls)

### Debug Mode
Enable debug logging to see detailed protocol messages:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
