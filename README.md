# Model Context Protocol (MCP) Tutorial with Python and FastAPI

This tutorial project demonstrates how to build and use Model Context Protocol (MCP) servers using Python and FastAPI. You'll learn the core concepts of MCP and how to integrate it with AI agents.

## 🎯 What You'll Learn

- **MCP Fundamentals**: Understanding tools, resources, and prompts
- **Server Development**: Building MCP servers with Python
- **FastAPI Integration**: Creating HTTP endpoints alongside MCP functionality
- **AI Agent Integration**: Connecting your server to AI clients like Claude Desktop
- **Real-world Examples**: Task management, weather data, and file operations

## 📚 Table of Contents

1. [Introduction to MCP](#introduction-to-mcp)
2. [Project Structure](#project-structure)
3. [Setup Instructions](#setup-instructions)
4. [Tutorial Examples](#tutorial-examples)
5. [Integration with AI Clients](#integration-with-ai-clients)
6. [Advanced Topics](#advanced-topics)
7. [Best Practices](#best-practices)

## 🔍 Introduction to MCP

The Model Context Protocol (MCP) is an open standard that enables secure, controlled access between AI assistants and external data sources and tools. It provides a standardized way for Large Language Models (LLMs) to:

- **Access Tools**: Execute functions and operations
- **Retrieve Resources**: Access data and content
- **Use Prompts**: Leverage pre-defined templates

### Key Components

1. **Tools**: Functions that the AI can call to perform actions
2. **Resources**: Data sources the AI can read from
3. **Prompts**: Pre-defined templates for common interactions

## 📁 Project Structure

```
mcp_tutorial/
├── src/
│   ├── basic_server/           # Simple MCP server example
│   ├── task_manager/           # Task management MCP server
│   ├── weather_service/        # Weather data MCP server
│   └── file_operations/        # File system MCP server
├── examples/
│   ├── client_examples/        # Example client usage
│   └── configurations/         # Claude Desktop configs
├── docs/
│   ├── concepts.md            # MCP concepts explained
│   ├── api_reference.md       # API documentation
│   └── troubleshooting.md     # Common issues and solutions
├── tests/                     # Test files
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Claude Desktop (optional, for testing)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mcp_tutorial
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the basic example**:
   ```bash
   python -m src.basic_server
   ```

## 🚀 Quick Start

**Want to see MCP in action right now?**

1. **Test the Basic Server**:
   ```bash
   cd mcp_tutorial
   python basic_server_simple.py --help
   ```

2. **Run the Test Suite**:
   ```bash
   python run_tests.py
   ```

3. **Try with Claude Desktop**:
   - Copy `examples/configurations/claude_desktop_config.json` content
   - Add to your Claude Desktop configuration
   - Restart Claude and test MCP integration

The basic server is fully functional and demonstrates all core MCP concepts!

---

## 📖 Tutorial Examples

### 1. Basic MCP Server
**Location**: `src/basic_server/`

A minimal MCP server that demonstrates:
- Server initialization
- Tool registration
- Basic tool execution
- Resource management

### 2. Task Manager Server
**Location**: `src/task_manager/`

A practical task management system with:
- Create, read, update, delete tasks
- Task categorization and filtering
- Due date management
- FastAPI web interface

### 3. Weather Service Server
**Location**: `src/weather_service/`

Weather data integration featuring:
- Current weather fetching
- Location-based queries
- Weather forecasts
- Data caching

### 4. File Operations Server
**Location**: `src/file_operations/`

Secure file system operations:
- Read/write files
- Directory listing
- File search capabilities
- Safety restrictions

## 🔗 Integration with AI Clients

### Claude Desktop Configuration

Add this to your Claude Desktop configuration (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "task-manager": {
      "command": "python",
      "args": ["-m", "src.task_manager"],
      "cwd": "/path/to/mcp_tutorial"
    },
    "weather-service": {
      "command": "python", 
      "args": ["-m", "src.weather_service"],
      "cwd": "/path/to/mcp_tutorial"
    }
  }
}
```

### Using with Other MCP Clients

The servers also support HTTP transport for integration with other clients and tools.

## 🎓 Advanced Topics

- **Custom Transport Layers**: Beyond stdio
- **Security Considerations**: Safe tool execution
- **Performance Optimization**: Caching and async operations
- **Error Handling**: Robust error management
- **Testing Strategies**: Unit and integration testing

## 🎯 Best Practices

1. **Security First**: Always validate inputs and restrict dangerous operations
2. **Clear Documentation**: Document your tools and resources thoroughly
3. **Error Handling**: Provide meaningful error messages
4. **Testing**: Write comprehensive tests for your MCP servers
5. **Logging**: Implement proper logging for debugging

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details on:
- Code style
- Testing requirements
- Documentation standards
- Pull request process

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Additional Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Claude Desktop](https://claude.ai/desktop)

---

*This tutorial is designed to be hands-on and practical. Each example builds upon the previous one, gradually introducing more complex concepts and real-world applications.*
