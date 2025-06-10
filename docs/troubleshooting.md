# Troubleshooting Guide

This guide helps you diagnose and fix common issues when working with the MCP tutorial servers.

## Common Issues

### 1. Server Won't Start

#### Symptoms
- Error when running `python -m src.basic_server`
- Import errors or module not found

#### Solutions

**Check Python Environment:**
```bash
# Verify Python version (3.8+ required)
python --version

# Check if you're in the right directory
pwd
ls  # Should see src/ directory

# Verify virtual environment is activated
which python
```

**Install Dependencies:**
```bash
# Install all required packages
pip install -r requirements.txt

# Or install individually
pip install mcp fastapi uvicorn aiohttp
```

**Check Module Path:**
```bash
# Try running from project root
cd /path/to/mcp_tutorial
python -m src.basic_server

# Or set PYTHONPATH
export PYTHONPATH=/path/to/mcp_tutorial:$PYTHONPATH
```

### 2. Claude Desktop Not Detecting Servers

#### Symptoms
- Servers don't appear in Claude Desktop
- No available tools when asking Claude

#### Solutions

**Check Configuration File:**
```bash
# Windows
notepad %APPDATA%\Claude\claude_desktop_config.json

# macOS
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
nano ~/.config/claude/claude_desktop_config.json
```

**Verify JSON Syntax:**
```json
{
  "mcpServers": {
    "basic-server": {
      "command": "python",
      "args": ["-m", "src.basic_server"],
      "cwd": "C:\\full\\path\\to\\mcp_tutorial"
    }
  }
}
```

**Common Fixes:**
- Use full absolute paths for `cwd`
- Ensure JSON is valid (no trailing commas)
- Use double backslashes on Windows: `"C:\\Users\\..."`
- Restart Claude Desktop after config changes

### 3. Weather Service API Errors

#### Symptoms
- "Invalid API key" errors
- "Location not found" messages
- Network timeout errors

#### Solutions

**API Key Setup:**
```bash
# Get free API key from https://openweathermap.org/api
# Set environment variable
export OPENWEATHER_API_KEY="your_actual_api_key"

# Or add to Claude Desktop config:
{
  "weather-service": {
    "command": "python",
    "args": ["-m", "src.weather_service"],
    "cwd": "/path/to/mcp_tutorial",
    "env": {
      "OPENWEATHER_API_KEY": "your_actual_api_key"
    }
  }
}
```

**Location Format:**
```bash
# Correct formats:
"London,UK"
"New York,NY,US"
"Tokyo,JP"

# Incorrect:
"London, United Kingdom"  # No spaces
"NYC"                     # Use full name
```

**Network Issues:**
```bash
# Test API manually
curl "http://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY"

# Check proxy settings if behind corporate firewall
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### 4. File Operations Permission Errors

#### Symptoms
- "Access denied" errors
- "Path not in allowed directories"
- Permission denied when reading/writing files

#### Solutions

**Check Allowed Directories:**
```python
# Default allowed directories:
# - Current working directory
# - User's Documents folder

# To see current allowed dirs:
python -c "
from src.file_operations import file_manager
print('Allowed directories:')
for d in file_manager.allowed_dirs:
    print(f'  {d}')
"
```

**File Path Issues:**
```bash
# Use absolute paths
/home/user/Documents/myfile.txt

# Or relative from allowed directory
Documents/myfile.txt

# Avoid path traversal
../../../etc/passwd  # This will be blocked
```

**File Extension Restrictions:**
```python
# Allowed extensions (safe text files):
.txt, .md, .json, .yaml, .yml, .csv, .log
.py, .js, .html, .css, .xml, .ini, .cfg

# Blocked extensions (dangerous):
.exe, .bat, .cmd, .sh, .ps1, .dll, .so
```

### 5. Task Manager Database Issues

#### Symptoms
- Tasks not persisting
- Database locked errors
- Corruption messages

#### Solutions

**Database File Location:**
```bash
# Check if database file exists
ls src/task_manager/tasks.db

# If corrupted, delete and restart:
rm src/task_manager/tasks.db
python -m src.task_manager  # Will recreate
```

**Permission Issues:**
```bash
# Ensure write permissions
chmod 755 src/task_manager/
chmod 644 src/task_manager/tasks.db  # If exists
```

**Multiple Instances:**
- Only run one task manager server at a time
- Close other instances before starting new ones

### 6. Import and Dependency Errors

#### Symptoms
- `ImportError: No module named 'mcp'`
- `ModuleNotFoundError: No module named 'fastapi'`

#### Solutions

**Check Installation:**
```bash
# List installed packages
pip list | grep -E "(mcp|fastapi|aiohttp|uvicorn)"

# Install missing packages
pip install mcp
pip install fastapi uvicorn
pip install aiohttp
```

**Virtual Environment Issues:**
```bash
# Create new virtual environment
python -m venv mcp_tutorial_env
source mcp_tutorial_env/bin/activate  # Linux/Mac
# or
mcp_tutorial_env\Scripts\activate     # Windows

pip install -r requirements.txt
```

**Package Version Conflicts:**
```bash
# Check for conflicts
pip check

# Upgrade packages
pip install --upgrade mcp fastapi uvicorn
```

## Debugging Techniques

### 1. Enable Verbose Logging

Add to your server code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Test Servers Manually

```bash
# Run server directly to see error messages
python -m src.basic_server

# Test with simple input
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python -m src.basic_server
```

### 3. Use Client Examples

```bash
# Test with provided client
python examples/client_examples/basic_client.py --basic
```

### 4. Check Claude Desktop Logs

**Windows:**
```
%LOCALAPPDATA%\Anthropic\Claude\logs\
```

**macOS:**
```
~/Library/Logs/Claude/
```

**Linux:**
```
~/.local/share/Claude/logs/
```

### 5. Network Diagnostics

```bash
# Test external connectivity
ping api.openweathermap.org

# Check DNS resolution
nslookup api.openweathermap.org

# Test HTTP connectivity
curl -I http://api.openweathermap.org
```

## Performance Issues

### 1. Slow Weather API Responses

**Solutions:**
- Use caching (enabled by default, 10-minute cache)
- Check internet connection speed
- Verify API key hasn't hit rate limits

### 2. Large File Operations

**Solutions:**
- Increase file size limits in code if needed
- Use streaming for very large files
- Consider chunked reading/writing

### 3. Database Performance

**Solutions:**
- Regularly check database size
- Consider cleanup of old completed tasks
- Use indexes for large datasets

## Security Warnings

### File Operations Safety
- Never disable path validation
- Don't add system directories to allowed paths
- Be cautious with executable file extensions

### API Key Security
- Don't commit API keys to version control
- Use environment variables
- Rotate keys regularly

### Network Security
- Be aware of data sent to external APIs
- Use HTTPS where possible
- Consider proxy settings in corporate environments

## Getting Help

### 1. Check Documentation
- Review API reference for parameter formats
- Check concepts documentation for MCP basics

### 2. Enable Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. Test Components Individually
- Start with basic server
- Add complexity gradually
- Isolate problematic components

### 4. Common Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Server won't start | Check dependencies: `pip install -r requirements.txt` |
| Claude can't see server | Verify config path and restart Claude Desktop |
| Weather API fails | Set `OPENWEATHER_API_KEY` environment variable |
| File access denied | Check if path is in allowed directories |
| Import errors | Activate virtual environment and install packages |
| Database issues | Delete `tasks.db` file and restart server |
| JSON config invalid | Validate JSON syntax and use absolute paths |
| Permission errors | Check file/directory permissions |

### 5. Still Need Help?

If you're still experiencing issues:

1. **Check the logs** for specific error messages
2. **Try the basic server first** to ensure MCP is working
3. **Test with client examples** to isolate the problem
4. **Verify your environment** matches the requirements
5. **Create a minimal reproduction** of the issue

Remember: Most issues are related to:
- Incorrect file paths
- Missing dependencies
- Configuration syntax errors
- Permission problems
- Network connectivity
