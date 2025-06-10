#!/usr/bin/env python3
"""Debug the basic server import issue."""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import basic_server
    print("Module imported successfully")
    print("Available attributes:", [attr for attr in dir(basic_server) if not attr.startswith('_')])
    
    # Try to access the actual module content
    import basic_server.__init__ as init_module
    print("Init module attributes:", [attr for attr in dir(init_module) if not attr.startswith('_')])
    
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
