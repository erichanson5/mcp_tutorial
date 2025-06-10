# MCP Core Concepts

This document explains the fundamental concepts of the Model Context Protocol (MCP) and how they work together to enable AI agents to interact with external systems.

## Overview

The Model Context Protocol is a standardized way for Large Language Models (LLMs) to securely access and interact with external data sources and tools. Think of it as a "bridge" that allows AI assistants to extend their capabilities beyond their training data.

## Core Components

### 1. Tools 🔧

Tools are functions that an AI can call to perform actions or computations. They represent executable operations that can change state or produce results.

**Examples:**
- Send an email
- Create a calendar event
- Execute a database query
- Perform a calculation
- Make an API call

**Tool Structure:**
```python
{
    "name": "create_task",
    "description": "Create a new task in the task manager",
    "inputSchema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "due_date": {"type": "string", "format": "date"}
        },
        "required": ["title"]
    }
}
```

### 2. Resources 📚

Resources are sources of information that an AI can read from. They provide access to data without modifying it.

**Examples:**
- File contents
- Database records
- API responses
- Configuration data
- Documentation

**Resource Structure:**
```python
{
    "uri": "file:///path/to/document.txt",
    "name": "Project Documentation",
    "description": "Main project documentation file",
    "mimeType": "text/plain"
}
```

### 3. Prompts 💬

Prompts are pre-defined templates that help structure interactions between the AI and the user or system.

**Examples:**
- Code review templates
- Report generation formats
- Question-answering patterns
- Task planning structures

**Prompt Structure:**
```python
{
    "name": "code_review",
    "description": "Template for reviewing code changes",
    "arguments": [
        {
            "name": "language",
            "description": "Programming language",
            "required": True
        },
        {
            "name": "complexity",
            "description": "Code complexity level",
            "required": False
        }
    ]
}
```

## MCP Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Client     │    │   MCP Server    │    │ External System │
│   (Claude)      │◄──►│   (Your Code)   │◄──►│ (API/DB/Files)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Communication Flow

1. **Initialization**: Client connects to MCP server
2. **Discovery**: Client queries available tools, resources, and prompts
3. **Interaction**: Client makes requests for tools/resources
4. **Execution**: Server processes requests and returns results
5. **Response**: Client receives and processes the response

## Transport Layers

MCP supports different ways for clients and servers to communicate:

### 1. Standard I/O (stdio)
- Uses stdin/stdout for communication
- Simple and widely supported
- Default for many integrations

### 2. HTTP with Server-Sent Events (SSE)
- Web-based communication
- Supports real-time updates
- Good for web applications

### 3. Streamable HTTP
- Modern HTTP-based transport
- Efficient for large data transfers
- Supports streaming responses

## Security Model

MCP implements several security features:

### 1. Sandboxing
- Servers run in isolated environments
- Limited access to system resources
- Controlled execution permissions

### 2. Input Validation
- All inputs are validated against schemas
- Type checking and constraint enforcement
- Prevents injection attacks

### 3. Access Control
- Fine-grained permissions for tools and resources
- User-configurable security policies
- Audit logging capabilities

## Best Practices

### 1. Tool Design
- Keep tools focused and single-purpose
- Provide clear, descriptive names
- Include comprehensive input validation
- Return structured, consistent outputs

### 2. Resource Management
- Use appropriate MIME types
- Implement efficient caching strategies
- Handle large datasets carefully
- Provide meaningful metadata

### 3. Error Handling
- Return informative error messages
- Use appropriate HTTP status codes
- Log errors for debugging
- Gracefully handle edge cases

### 4. Performance
- Implement async operations where possible
- Use connection pooling for external APIs
- Cache frequently accessed data
- Monitor resource usage

## Example: Task Management Tool

Here's how the concepts work together in a practical example:

```python
# Tool Definition
async def create_task(title: str, description: str = "", priority: str = "medium"):
    """Create a new task"""
    task = {
        "id": generate_id(),
        "title": title,
        "description": description,
        "priority": priority,
        "created_at": datetime.now(),
        "completed": False
    }
    await save_task(task)
    return {"success": True, "task_id": task["id"]}

# Resource Access
async def get_tasks_resource():
    """Get all tasks as a resource"""
    tasks = await load_all_tasks()
    return {
        "uri": "tasks://all",
        "name": "All Tasks",
        "description": "Complete list of all tasks",
        "mimeType": "application/json",
        "text": json.dumps(tasks, indent=2)
    }

# Prompt Template
async def get_task_summary_prompt(filter_by: str = "all"):
    """Generate a task summary prompt"""
    return {
        "name": "task_summary",
        "description": "Summarize tasks based on filter",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Please provide a summary of tasks filtered by: {filter_by}"
                }
            }
        ]
    }
```

## Integration Patterns

### 1. Direct Integration
- AI client connects directly to MCP server
- Simple setup and configuration
- Good for single-user scenarios

### 2. Proxy Pattern
- Multiple MCP servers behind a proxy
- Centralized authentication and routing
- Scalable for enterprise use

### 3. Service Mesh
- Multiple interconnected MCP servers
- Complex workflows and data flows
- Advanced orchestration capabilities

## Next Steps

Now that you understand the core concepts, you can:

1. Explore the basic server example
2. Build your own MCP tools
3. Integrate with external APIs
4. Create resource providers
5. Design custom prompts

Each tutorial example in this project demonstrates these concepts in action with real, working code.
