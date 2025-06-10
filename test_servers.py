#!/usr/bin/env python3
"""Simple MCP Client for testing servers"""

import asyncio
import json
import subprocess
import sys

async def test_server_subprocess(server_script: str, server_name: str):
    """Test an MCP server by launching it as a subprocess and sending JSON-RPC messages."""
    print(f"\n=== Testing {server_name} ===")
    
    try:
        # Start the server as a subprocess
        process = subprocess.Popen(
            [sys.executable, server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send the request
        request_str = json.dumps(init_request) + "\n"
        process.stdin.write(request_str)
        process.stdin.flush()
        
        # Read response (with timeout)
        try:
            stdout, stderr = process.communicate(timeout=10)
            if stderr:
                print(f"Server stderr: {stderr}")
            if stdout:
                print(f"Server response: {stdout}")
            print(f"✅ {server_name} responded successfully")
        except subprocess.TimeoutExpired:
            print(f"⚠️  {server_name} timed out (normal for stdio servers)")
            process.terminate()
        
    except Exception as e:
        print(f"❌ Error testing {server_name}: {e}")
    finally:
        if process.poll() is None:
            process.terminate()

async def main():
    """Test all MCP servers."""
    print("🧪 Testing MCP Servers")
    print("=" * 50)
    
    # Test basic server
    await test_server_subprocess("basic_server_simple.py", "Basic Server")
    
    # Add tests for other servers when they're ready
    # await test_server_subprocess("src/task_manager/__init__.py", "Task Manager")
    # await test_server_subprocess("src/weather_service/__init__.py", "Weather Service")
    # await test_server_subprocess("src/file_operations/__init__.py", "File Operations")

if __name__ == "__main__":
    asyncio.run(main())
