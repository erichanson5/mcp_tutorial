# Claude Desktop Configuration Guide

This guide explains how to configure Claude Desktop to use the MCP servers in this tutorial.

## Configuration File Location

The Claude Desktop configuration file is located at:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

## Basic Configuration

Copy the configuration from `claude_desktop_config.json` and modify the paths:

```json
{
  "mcpServers": {
    "basic-server": {
      "command": "python",
      "args": ["-m", "src.basic_server"],
      "cwd": "C:\\Users\\YourUsername\\path\\to\\mcp_tutorial"
    }
  }
}
```

## Individual Server Configurations

### Basic Server
```json
"basic-server": {
  "command": "python",
  "args": ["-m", "src.basic_server"],
  "cwd": "/path/to/mcp_tutorial"
}
```

### Task Manager
```json
"task-manager": {
  "command": "python",
  "args": ["-m", "src.task_manager"],
  "cwd": "/path/to/mcp_tutorial"
}
```

### Weather Service
```json
"weather-service": {
  "command": "python",
  "args": ["-m", "src.weather_service"],
  "cwd": "/path/to/mcp_tutorial",
  "env": {
    "OPENWEATHER_API_KEY": "your_actual_api_key_here"
  }
}
```

### File Operations
```json
"file-operations": {
  "command": "python",
  "args": ["-m", "src.file_operations"],
  "cwd": "/path/to/mcp_tutorial"
}
```

## Environment Variables

Some servers require environment variables:

### Weather Service
- `OPENWEATHER_API_KEY`: Get your free API key from [OpenWeatherMap](https://openweathermap.org/api)

## Testing the Configuration

1. Save your configuration file
2. Restart Claude Desktop
3. Start a new conversation
4. Try commands like:
   - "Calculate 15 + 27"
   - "Create a task to buy groceries"
   - "What's the weather in London?"
   - "List files in my Documents folder"

## Troubleshooting

### Common Issues

1. **Server not found**: Check that the `cwd` path is correct
2. **Python not found**: Ensure Python is in your PATH
3. **Dependencies missing**: Run `pip install -r requirements.txt`
4. **Permission errors**: Check that the specified directories are accessible

### Debugging

To debug server issues:

1. Try running the server manually:
   ```bash
   cd /path/to/mcp_tutorial
   python -m src.basic_server
   ```

2. Check the Claude Desktop logs
3. Verify your configuration JSON syntax

### Server Status

You can check if servers are working by:
- Looking for them in Claude's available tools
- Asking Claude to list available functions
- Testing basic operations

## Advanced Configuration

### Custom Working Directory
```json
"custom-server": {
  "command": "python",
  "args": ["-m", "src.task_manager"],
  "cwd": "/custom/path",
  "env": {
    "CUSTOM_VAR": "value"
  }
}
```

### Multiple Environments
You can configure different servers for different purposes:

```json
{
  "mcpServers": {
    "dev-tasks": {
      "command": "python",
      "args": ["-m", "src.task_manager"],
      "cwd": "/dev/projects/mcp_tutorial"
    },
    "prod-tasks": {
      "command": "python", 
      "args": ["-m", "src.task_manager"],
      "cwd": "/prod/projects/mcp_tutorial"
    }
  }
}
```

## Security Considerations

1. **File Operations**: The file server is sandboxed to specific directories
2. **API Keys**: Store API keys securely, don't commit them to version control
3. **Network Access**: Weather service makes external API calls
4. **Permissions**: Servers run with your user permissions

## Next Steps

Once configured, you can:
1. Experiment with the different servers
2. Build your own MCP servers
3. Integrate with other tools and services
4. Explore advanced MCP features
