#!/usr/bin/env python3
"""Simple launcher for the basic MCP server."""

import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run the server
from __init__ import main

if __name__ == "__main__":
    main()
