#!/usr/bin/env python3
"""Basic MCP Server - Simplified Version"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Sequence

# Set up logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Entry point for the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Basic MCP Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Import MCP components here to handle import errors better
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import TextContent, Tool, Resource
        
        async def serve():
            """Main server function."""
            server = Server("basic-mcp-server")

            @server.list_tools()
            async def list_tools() -> list[Tool]:
                """List available tools."""
                return [
                    Tool(
                        name="calculate",
                        description="Perform basic arithmetic calculations",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "operation": {
                                    "type": "string",
                                    "enum": ["add", "subtract", "multiply", "divide"],
                                    "description": "The arithmetic operation to perform"
                                },
                                "a": {
                                    "type": "number",
                                    "description": "First number"
                                },
                                "b": {
                                    "type": "number",
                                    "description": "Second number"
                                }
                            },
                            "required": ["operation", "a", "b"]
                        }
                    ),
                    Tool(
                        name="greet",
                        description="Generate a personalized greeting",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Name of the person to greet"
                                },
                                "style": {
                                    "type": "string",
                                    "enum": ["formal", "casual", "friendly"],
                                    "description": "Style of greeting",
                                    "default": "friendly"
                                }
                            },
                            "required": ["name"]
                        }
                    ),
                    Tool(
                        name="get_server_info",
                        description="Get information about the server",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "additionalProperties": False
                        }
                    )
                ]

            @server.call_tool()
            async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
                """Handle tool calls."""
                try:
                    if name == "calculate":
                        operation = arguments.get("operation")
                        a = float(arguments.get("a"))
                        b = float(arguments.get("b"))

                        if operation == "add":
                            result = a + b
                        elif operation == "subtract":
                            result = a - b
                        elif operation == "multiply":
                            result = a * b
                        elif operation == "divide":
                            if b == 0:
                                raise ValueError("Division by zero is not allowed")
                            result = a / b
                        else:
                            raise ValueError(f"Unknown operation: {operation}")

                        return [TextContent(
                            type="text",
                            text=f"Result: {a} {operation} {b} = {result}"
                        )]
                        
                    elif name == "greet":
                        name_arg = arguments.get("name", "").strip()
                        if not name_arg:
                            raise ValueError("Name is required for greeting")

                        style = arguments.get("style", "friendly")
                        
                        if style == "formal":
                            greeting = f"Good day, {name_arg}. I hope you are well."
                        elif style == "casual":
                            greeting = f"Hey {name_arg}! What's up?"
                        else:  # friendly
                            greeting = f"Hello {name_arg}! Nice to meet you!"

                        return [TextContent(type="text", text=greeting)]
                        
                    elif name == "get_server_info":
                        info = {
                            "server_name": "Basic MCP Server",
                            "description": "A simple example MCP server demonstrating basic functionality",
                            "version": "1.0.0",
                            "capabilities": ["tools", "resources"],
                            "tools_count": 3,
                            "resources_count": 2,
                            "uptime": "N/A",
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        return [TextContent(
                            type="text",
                            text=json.dumps(info, indent=2)
                        )]
                    else:
                        raise ValueError(f"Unknown tool: {name}")
                except Exception as e:
                    logger.error(f"Error in tool {name}: {e}")
                    return [TextContent(type="text", text=f"Error: {str(e)}")]

            @server.list_resources()
            async def list_resources() -> list[Resource]:
                """List available resources."""
                return [
                    Resource(
                        uri="time://current",
                        name="Current Time",
                        description="Current server time",
                        mimeType="text/plain"
                    ),
                    Resource(
                        uri="server://status",
                        name="Server Status",
                        description="Current server status and information",
                        mimeType="application/json"
                    )
                ]

            @server.read_resource()
            async def read_resource(uri: str) -> str:
                """Read a resource by URI."""
                if uri == "time://current":
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    return f"Current server time: {current_time}"
                elif uri == "server://status":
                    status = {
                        "server_name": "Basic MCP Server",
                        "status": "running",
                        "uptime": "N/A",
                        "version": "1.0.0",
                        "timestamp": datetime.now().isoformat()
                    }
                    return json.dumps(status, indent=2)
                else:
                    raise ValueError(f"Unknown resource: {uri}")

            # Start the server
            options = server.create_initialization_options()
            async with stdio_server() as (read_stream, write_stream):
                await server.run(read_stream, write_stream, options)
        
        asyncio.run(serve())
        
    except ImportError as e:
        logger.error(f"MCP import error: {e}")
        logger.error("Make sure the MCP SDK is installed: pip install mcp")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
