# API Reference

This document provides a comprehensive reference for all the tools, resources, and capabilities provided by the MCP servers in this tutorial.

## Basic Server API

### Tools

#### `calculate`
Perform basic mathematical calculations.

**Parameters:**
- `operation` (string, required): One of "add", "subtract", "multiply", "divide"
- `a` (number, required): First number
- `b` (number, required): Second number

**Returns:**
Text response with the calculation result.

**Example:**
```json
{
  "operation": "multiply",
  "a": 6,
  "b": 7
}
```
→ "Calculation: 6.0 multiply 7.0 = 42.0"

#### `greet`
Generate a personalized greeting message.

**Parameters:**
- `name` (string, required): Name of the person to greet
- `style` (string, optional): One of "formal", "casual", "enthusiastic" (default: "casual")

**Returns:**
Text response with personalized greeting.

**Example:**
```json
{
  "name": "Bob",
  "style": "formal"
}
```
→ "Good day, Bob. It is a pleasure to make your acquaintance."

#### `get_server_info`
Get information about the MCP server.

**Parameters:**
None

**Returns:**
JSON object with server metadata.

### Resources

#### `time://current`
Get the current date and time.

**Content Type:** text/plain

#### `server://status`
Get current server status and statistics.

**Content Type:** application/json

---

## Task Manager API

### Tools

#### `create_task`
Create a new task.

**Parameters:**
- `title` (string, required): Task title
- `description` (string, optional): Task description
- `category` (string, optional): One of "work", "personal", "shopping", "health", "general"
- `priority` (string, optional): One of "low", "medium", "high", "urgent"
- `due_date` (string, optional): Due date in YYYY-MM-DD format

**Returns:**
JSON object with created task details.

#### `get_task`
Get a specific task by ID.

**Parameters:**
- `task_id` (string, required): Task ID

**Returns:**
JSON object with task details or error message.

#### `list_tasks`
List all tasks with optional filtering.

**Parameters:**
- `category` (string, optional): Filter by category
- `completed` (boolean, optional): Filter by completion status

**Returns:**
JSON array of task objects.

#### `update_task`
Update an existing task.

**Parameters:**
- `task_id` (string, required): Task ID
- `title` (string, optional): New title
- `description` (string, optional): New description
- `category` (string, optional): New category
- `priority` (string, optional): New priority
- `due_date` (string, optional): New due date
- `completed` (boolean, optional): New completion status

**Returns:**
JSON object with updated task details.

#### `delete_task`
Delete a task.

**Parameters:**
- `task_id` (string, required): Task ID

**Returns:**
Confirmation message or error.

#### `search_tasks`
Search tasks by title or description.

**Parameters:**
- `query` (string, required): Search query

**Returns:**
JSON array of matching tasks.

#### `get_task_stats`
Get task statistics and summary.

**Parameters:**
None

**Returns:**
JSON object with statistics including:
- Total tasks
- Completed/pending counts
- Category breakdown
- Priority distribution
- Completion rate

### Resources

#### `tasks://all`
Complete list of all tasks in JSON format.

**Content Type:** application/json

#### `tasks://summary`
Summary of task statistics and status.

**Content Type:** text/plain

---

## Weather Service API

### Tools

#### `get_current_weather`
Get current weather conditions for a specific location.

**Parameters:**
- `location` (string, required): City name, state/country (e.g., "London,UK")
- `units` (string, optional): One of "metric", "imperial", "kelvin" (default: "metric")

**Returns:**
Formatted weather report including temperature, conditions, humidity, wind, etc.

#### `get_weather_by_coordinates`
Get current weather by latitude and longitude.

**Parameters:**
- `latitude` (number, required): Latitude (-90 to 90)
- `longitude` (number, required): Longitude (-180 to 180)
- `units` (string, optional): Temperature units

**Returns:**
Formatted weather report.

#### `get_weather_forecast`
Get 5-day weather forecast for a location.

**Parameters:**
- `location` (string, required): City name, state/country
- `units` (string, optional): Temperature units

**Returns:**
Formatted 5-day forecast with daily summaries and hourly details.

#### `get_forecast_by_coordinates`
Get 5-day weather forecast by coordinates.

**Parameters:**
- `latitude` (number, required): Latitude
- `longitude` (number, required): Longitude
- `units` (string, optional): Temperature units

**Returns:**
Formatted forecast data.

#### `parse_weather_data`
Parse and format raw weather data into human-readable format.

**Parameters:**
- `weather_data` (object, required): Raw weather data from API

**Returns:**
Formatted weather information.

### Resources

#### `weather://cache`
Information about cached weather data.

**Content Type:** application/json

Contains cache statistics, entry count, and validity information.

#### `weather://api-info`
Information about the weather API service.

**Content Type:** text/plain

Contains API details, endpoints, features, and configuration info.

---

## File Operations API

### Tools

#### `read_file`
Read the contents of a text file.

**Parameters:**
- `file_path` (string, required): Path to the file to read
- `max_size` (integer, optional): Maximum file size in bytes

**Returns:**
File content with metadata including size, type, and modification date.

**Security Notes:**
- Only allowed file extensions can be read
- File must be within allowed directories
- Size limits apply

#### `write_file`
Write content to a text file.

**Parameters:**
- `file_path` (string, required): Path to the file to write
- `content` (string, required): Content to write
- `create_dirs` (boolean, optional): Create parent directories if needed

**Returns:**
Success message with file metadata.

**Security Notes:**
- Only safe file extensions allowed
- Must be within allowed directories
- Content size limits apply

#### `list_directory`
List the contents of a directory.

**Parameters:**
- `directory_path` (string, required): Path to directory
- `include_hidden` (boolean, optional): Include hidden files/directories

**Returns:**
Directory listing with file/folder details including:
- Names and types
- Sizes and dates
- Permissions
- MIME types

#### `search_files`
Search for files by name and optionally content.

**Parameters:**
- `search_directory` (string, required): Directory to search (recursive)
- `pattern` (string, required): Search pattern (case-insensitive)
- `include_content` (boolean, optional): Also search within file contents

**Returns:**
List of matching files with match type and line numbers for content matches.

#### `get_file_info`
Get detailed information about a file or directory.

**Parameters:**
- `file_path` (string, required): Path to file or directory

**Returns:**
Detailed metadata including:
- Name, path, size
- Creation and modification dates
- Permissions
- MIME type
- File extension

#### `get_file_hash`
Get cryptographic hashes of a file.

**Parameters:**
- `file_path` (string, required): Path to file

**Returns:**
File hashes including MD5, SHA1, and SHA256.

### Resources

#### `file://security-config`
Current security settings and allowed directories.

**Content Type:** application/json

#### `file://allowed-dirs`
List of directories accessible to the file server.

**Content Type:** text/plain

---

## Error Handling

All tools return error responses in case of failures:

```json
{
  "error": "Description of what went wrong"
}
```

Common error types:
- **Validation errors**: Invalid parameters or missing required fields
- **Permission errors**: Access denied, path not allowed
- **Resource errors**: File not found, network unreachable
- **System errors**: Internal server errors, unexpected exceptions

---

## Data Types

### Task Object
```json
{
  "id": "uuid-string",
  "title": "string",
  "description": "string",
  "category": "work|personal|shopping|health|general",
  "priority": "low|medium|high|urgent",
  "due_date": "YYYY-MM-DD",
  "completed": true|false,
  "created_at": "ISO-8601-datetime",
  "updated_at": "ISO-8601-datetime"
}
```

### Weather Units
- **metric**: Celsius, meters/second, kilometers
- **imperial**: Fahrenheit, miles/hour, miles
- **kelvin**: Kelvin, meters/second, kilometers

### File Information Object
```json
{
  "name": "filename.ext",
  "path": "/full/path/to/file",
  "size": 1024,
  "modified": "ISO-8601-datetime",
  "created": "ISO-8601-datetime",
  "is_file": true|false,
  "is_dir": true|false,
  "permissions": "755",
  "mime_type": "text/plain",
  "extension": ".txt"
}
```

---

## Rate Limits and Quotas

### Weather Service
- API calls are cached for 10 minutes
- External API rate limits may apply (depends on your OpenWeatherMap plan)

### File Operations
- Maximum file size: 10MB
- No rate limits on local file operations

### Task Manager
- No built-in rate limits
- Database operations are typically fast

---

## Configuration

### Environment Variables

#### Weather Service
- `OPENWEATHER_API_KEY`: Your OpenWeatherMap API key

### Security Settings

#### File Operations
- Allowed directories are configured at server startup
- File extension filtering can be customized
- Maximum file size can be adjusted

---

## Best Practices

1. **Error Handling**: Always check for error fields in responses
2. **Parameter Validation**: Ensure parameters match the required types and formats
3. **Resource Management**: Close connections properly when done
4. **Security**: Use appropriate file paths and avoid sensitive directories
5. **Performance**: Use caching where available (weather service)
6. **Logging**: Enable appropriate logging levels for debugging
