"""
Task Manager MCP Server Entry Point

Run with:
  python -m src.task_manager          # MCP server mode
  python -m src.task_manager --web    # Web server mode
"""

from . import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
