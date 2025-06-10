"""
File Operations MCP Server Entry Point

Usage:
  python -m src.file_operations

Configuration:
  Set allowed directories in the source code or via environment variables.
  Default allowed directories: current working directory and user Documents folder.
"""

from . import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
