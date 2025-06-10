"""
Check what types and functions are available in the current MCP version.
"""

import mcp.types
import mcp.server
from mcp.types import *
from mcp.server import *

# Print available types
print("Available types:")
print("===============")
for name in dir(mcp.types):
    if not name.startswith('_'):
        obj = getattr(mcp.types, name)
        if hasattr(obj, '__doc__'):
            print(f"- {name}: {type(obj)}")

print("\nAvailable server components:")
print("============================")
for name in dir(mcp.server):
    if not name.startswith('_'):
        obj = getattr(mcp.server, name)
        if hasattr(obj, '__doc__'):
            print(f"- {name}: {type(obj)}")
