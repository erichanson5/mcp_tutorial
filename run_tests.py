#!/usr/bin/env python3
"""Complete end-to-end test for MCP Tutorial servers."""

import asyncio
import json
import subprocess
import sys
import os
from pathlib import Path

def test_basic_server():
    """Test the basic server functionality."""
    print("🧪 Testing Basic Server...")
    
    server_path = Path("basic_server_simple.py")
    if not server_path.exists():
        print("❌ Basic server file not found")
        return False
    
    try:
        # Test help command
        result = subprocess.run(
            [sys.executable, str(server_path), "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "Basic MCP Server" in result.stdout:
            print("✅ Basic server help command works")
            return True
        else:
            print(f"❌ Basic server help failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Basic server test error: {e}")
        return False

def test_task_manager():
    """Test the task manager server."""
    print("🧪 Testing Task Manager Server...")
    
    server_path = Path("src/task_manager/__init__.py")
    if not server_path.exists():
        print("❌ Task manager server file not found")
        return False
    
    try:
        # Test help command  
        result = subprocess.run(
            [sys.executable, str(server_path), "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "Task Manager MCP Server" in result.stdout:
            print("✅ Task manager help command works")
            return True
        else:
            print(f"❌ Task manager help failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Task manager test error: {e}")
        return False

def check_documentation():
    """Check if documentation files exist."""
    print("📚 Checking Documentation...")
    
    docs = [
        "README.md",
        "docs/concepts.md", 
        "docs/troubleshooting.md",
        "docs/api_reference.md",
        "requirements.txt"
    ]
    
    all_exist = True
    for doc in docs:
        if Path(doc).exists():
            print(f"✅ {doc}")
        else:
            print(f"❌ {doc} missing")
            all_exist = False
    
    return all_exist

def check_examples():
    """Check if example files exist."""
    print("📁 Checking Examples...")
    
    examples = [
        "examples/client_examples/basic_client.py",
        "examples/configurations/claude_desktop_config.json",
        "examples/configurations/README.md"
    ]
    
    all_exist = True
    for example in examples:
        if Path(example).exists():
            print(f"✅ {example}")
        else:
            print(f"❌ {example} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run the complete test suite."""
    print("🚀 MCP Tutorial Test Suite")
    print("=" * 50)
    
    os.chdir(Path(__file__).parent)
    
    tests = [
        ("Documentation", check_documentation),
        ("Examples", check_examples), 
        ("Basic Server", test_basic_server),
        ("Task Manager", test_task_manager)
    ]
    
    results = {}
    for name, test_func in tests:
        print(f"\n{name}:")
        results[name] = test_func()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! The MCP tutorial is ready to use.")
        print("\nNext steps:")
        print("1. Review the README.md for setup instructions")
        print("2. Test with Claude Desktop using the configuration examples")
        print("3. Try the client examples to interact with servers programmatically")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
