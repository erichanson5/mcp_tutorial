#!/usr/bin/env python3
"""Test script to check MCP imports and create a simple working example."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest, 
    ListToolsResult,
    Tool,
    TextContent,
)

# Create a simple server
server = Server("test-server")

@server.call_tool()
async def add_numbers(a: float, b: float) -> str:
    """Add two numbers and return the result."""
    result = a + b
    return f"The sum of {a} and {b} is {result}"

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="add_numbers",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        )
    ]

async def main():
    """Main function to test the server setup."""
    print("MCP Server imports successful!")
    print("Available tools:")
    tools = await list_tools()
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")

if __name__ == "__main__":
    asyncio.run(main())
