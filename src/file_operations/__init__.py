"""
File Operations MCP Server

This server demonstrates secure file system operations with:
- Read/write file operations
- Directory listing and navigation
- File search capabilities
- Security restrictions and sandboxing
- Content type detection
- File metadata access

Security Features:
- Configurable allowed directories
- Path traversal protection
- File size limits
- Content type validation
- Permission checks
"""

import asyncio
import json
import logging
import mimetypes
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import hashlib
import stat

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    GetResourceResult,
    ListResourcesResult,
    ListToolsResult,
    Resource,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
ALLOWED_EXTENSIONS = {
    '.txt', '.md', '.json', '.yaml', '.yml', '.csv', '.log', 
    '.py', '.js', '.html', '.css', '.xml', '.ini', '.cfg'
}
DANGEROUS_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.sh', '.ps1', '.dll', '.so'
}

# Default allowed directories (can be configured)
DEFAULT_ALLOWED_DIRS = {
    str(Path.home() / "Documents"),
    str(Path.cwd()),
}

# MCP Server
server = Server("file-operations-mcp-server")


class SecureFileManager:
    """Secure file operations manager with sandboxing"""
    
    def __init__(self, allowed_dirs: Optional[Set[str]] = None):
        self.allowed_dirs = set(allowed_dirs) if allowed_dirs else DEFAULT_ALLOWED_DIRS
        # Resolve and normalize paths
        self.allowed_dirs = {str(Path(d).resolve()) for d in self.allowed_dirs}
        logger.info(f"Initialized with allowed directories: {self.allowed_dirs}")
    
    def _is_path_allowed(self, file_path: Path) -> bool:
        """Check if the file path is within allowed directories"""
        try:
            resolved_path = file_path.resolve()
            for allowed_dir in self.allowed_dirs:
                if str(resolved_path).startswith(allowed_dir):
                    return True
            return False
        except Exception:
            return False
    
    def _is_extension_allowed(self, file_path: Path) -> bool:
        """Check if file extension is allowed"""
        extension = file_path.suffix.lower()
        if extension in DANGEROUS_EXTENSIONS:
            return False
        # If ALLOWED_EXTENSIONS is set, only allow those
        if ALLOWED_EXTENSIONS and extension not in ALLOWED_EXTENSIONS:
            return False
        return True
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file metadata"""
        try:
            stat_info = file_path.stat()
            return {
                "name": file_path.name,
                "path": str(file_path),
                "size": stat_info.st_size,
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "is_file": file_path.is_file(),
                "is_dir": file_path.is_dir(),
                "permissions": oct(stat_info.st_mode)[-3:],
                "mime_type": mimetypes.guess_type(str(file_path))[0],
                "extension": file_path.suffix.lower()
            }
        except Exception as e:
            return {"error": f"Cannot access file info: {str(e)}"}
    
    async def read_file(self, file_path: str, max_size: Optional[int] = None) -> Dict[str, Any]:
        """Safely read a file"""
        try:
            path = Path(file_path)
            
            if not self._is_path_allowed(path):
                return {"error": f"Access denied: Path not in allowed directories"}
            
            if not path.exists():
                return {"error": f"File not found: {file_path}"}
            
            if not path.is_file():
                return {"error": f"Not a file: {file_path}"}
            
            if not self._is_extension_allowed(path):
                return {"error": f"File type not allowed: {path.suffix}"}
            
            file_size = path.stat().st_size
            size_limit = max_size or MAX_FILE_SIZE
            
            if file_size > size_limit:
                return {"error": f"File too large: {file_size} bytes (limit: {size_limit})"}
            
            # Try to read as text first, then as binary
            try:
                content = path.read_text(encoding='utf-8')
                content_type = "text"
            except UnicodeDecodeError:
                content = path.read_bytes()
                content = f"<binary data: {len(content)} bytes>"
                content_type = "binary"
            
            return {
                "content": content,
                "content_type": content_type,
                "size": file_size,
                "encoding": "utf-8" if content_type == "text" else "binary",
                "file_info": self._get_file_info(path)
            }
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {"error": f"Failed to read file: {str(e)}"}
    
    async def write_file(self, file_path: str, content: str, create_dirs: bool = False) -> Dict[str, Any]:
        """Safely write to a file"""
        try:
            path = Path(file_path)
            
            if not self._is_path_allowed(path):
                return {"error": f"Access denied: Path not in allowed directories"}
            
            if not self._is_extension_allowed(path):
                return {"error": f"File type not allowed: {path.suffix}"}
            
            if len(content.encode('utf-8')) > MAX_FILE_SIZE:
                return {"error": f"Content too large (limit: {MAX_FILE_SIZE} bytes)"}
            
            # Create parent directories if requested
            if create_dirs and not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if parent directory exists
            if not path.parent.exists():
                return {"error": f"Parent directory does not exist: {path.parent}"}
            
            # Write the file
            path.write_text(content, encoding='utf-8')
            
            return {
                "success": True,
                "message": f"File written successfully: {file_path}",
                "size": len(content.encode('utf-8')),
                "file_info": self._get_file_info(path)
            }
            
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return {"error": f"Failed to write file: {str(e)}"}
    
    async def list_directory(self, dir_path: str, include_hidden: bool = False) -> Dict[str, Any]:
        """List directory contents"""
        try:
            path = Path(dir_path)
            
            if not self._is_path_allowed(path):
                return {"error": f"Access denied: Path not in allowed directories"}
            
            if not path.exists():
                return {"error": f"Directory not found: {dir_path}"}
            
            if not path.is_dir():
                return {"error": f"Not a directory: {dir_path}"}
            
            items = []
            for item in path.iterdir():
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                item_info = self._get_file_info(item)
                items.append(item_info)
            
            # Sort by name
            items.sort(key=lambda x: x.get('name', '').lower())
            
            return {
                "directory": str(path),
                "items": items,
                "total_items": len(items),
                "files": len([i for i in items if i.get('is_file')]),
                "directories": len([i for i in items if i.get('is_dir')])
            }
            
        except Exception as e:
            logger.error(f"Error listing directory {dir_path}: {e}")
            return {"error": f"Failed to list directory: {str(e)}"}
    
    async def search_files(self, search_dir: str, pattern: str, include_content: bool = False) -> Dict[str, Any]:
        """Search for files by name and optionally content"""
        try:
            path = Path(search_dir)
            
            if not self._is_path_allowed(path):
                return {"error": f"Access denied: Path not in allowed directories"}
            
            if not path.exists() or not path.is_dir():
                return {"error": f"Invalid search directory: {search_dir}"}
            
            matches = []
            
            # Search recursively
            for item in path.rglob('*'):
                if not self._is_path_allowed(item):
                    continue
                
                # Check filename match
                if pattern.lower() in item.name.lower():
                    match_info = self._get_file_info(item)
                    match_info["match_type"] = "filename"
                    
                    # Optionally search content
                    if include_content and item.is_file() and self._is_extension_allowed(item):
                        try:
                            if item.stat().st_size <= MAX_FILE_SIZE:
                                content = item.read_text(encoding='utf-8')
                                if pattern.lower() in content.lower():
                                    match_info["match_type"] = "content"
                                    # Find line numbers with matches
                                    lines = content.split('\n')
                                    matching_lines = []
                                    for i, line in enumerate(lines, 1):
                                        if pattern.lower() in line.lower():
                                            matching_lines.append({"line": i, "text": line.strip()})
                                    match_info["matching_lines"] = matching_lines[:10]  # Limit to 10
                        except (UnicodeDecodeError, PermissionError):
                            pass  # Skip files that can't be read
                    
                    matches.append(match_info)
            
            return {
                "search_directory": str(path),
                "pattern": pattern,
                "matches": matches,
                "total_matches": len(matches)
            }
            
        except Exception as e:
            logger.error(f"Error searching files in {search_dir}: {e}")
            return {"error": f"Failed to search files: {str(e)}"}
    
    async def get_file_hash(self, file_path: str) -> Dict[str, Any]:
        """Get file hash for integrity checking"""
        try:
            path = Path(file_path)
            
            if not self._is_path_allowed(path):
                return {"error": f"Access denied: Path not in allowed directories"}
            
            if not path.exists() or not path.is_file():
                return {"error": f"File not found: {file_path}"}
            
            if path.stat().st_size > MAX_FILE_SIZE:
                return {"error": f"File too large for hashing"}
            
            # Calculate multiple hashes
            content = path.read_bytes()
            
            return {
                "file": str(path),
                "size": len(content),
                "md5": hashlib.md5(content).hexdigest(),
                "sha1": hashlib.sha1(content).hexdigest(),
                "sha256": hashlib.sha256(content).hexdigest()
            }
            
        except Exception as e:
            logger.error(f"Error hashing file {file_path}: {e}")
            return {"error": f"Failed to hash file: {str(e)}"}


# Initialize file manager
file_manager = SecureFileManager()


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available file operation tools"""
    tools = [
        Tool(
            name="read_file",
            description="Read the contents of a text file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    },
                    "max_size": {
                        "type": "integer",
                        "description": "Maximum file size to read (bytes)",
                        "default": MAX_FILE_SIZE
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="write_file",
            description="Write content to a text file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    },
                    "create_dirs": {
                        "type": "boolean",
                        "description": "Create parent directories if they don't exist",
                        "default": False
                    }
                },
                "required": ["file_path", "content"]
            }
        ),
        Tool(
            name="list_directory",
            description="List the contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory to list"
                    },
                    "include_hidden": {
                        "type": "boolean",
                        "description": "Include hidden files and directories",
                        "default": False
                    }
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="search_files",
            description="Search for files by name and optionally content",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_directory": {
                        "type": "string",
                        "description": "Directory to search in (searches recursively)"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Search pattern (case-insensitive)"
                    },
                    "include_content": {
                        "type": "boolean",
                        "description": "Also search within file contents",
                        "default": False
                    }
                },
                "required": ["search_directory", "pattern"]
            }
        ),
        Tool(
            name="get_file_info",
            description="Get detailed information about a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file or directory"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="get_file_hash",
            description="Get cryptographic hashes of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to hash"
                    }
                },
                "required": ["file_path"]
            }
        )
    ]
    
    return ListToolsResult(tools=tools)


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool execution"""
    try:
        if name == "read_file":
            return await handle_read_file(arguments)
        elif name == "write_file":
            return await handle_write_file(arguments)
        elif name == "list_directory":
            return await handle_list_directory(arguments)
        elif name == "search_files":
            return await handle_search_files(arguments)
        elif name == "get_file_info":
            return await handle_get_file_info(arguments)
        elif name == "get_file_hash":
            return await handle_get_file_hash(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            isError=True
        )


async def handle_read_file(arguments: Dict[str, Any]) -> CallToolResult:
    """Read a file"""
    file_path = arguments["file_path"]
    max_size = arguments.get("max_size")
    
    result = await file_manager.read_file(file_path, max_size)
    
    if "error" in result:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error reading file: {result['error']}")],
            isError=True
        )
    
    # Format the response
    response = f"📄 File: {file_path}\n"
    response += f"📊 Size: {result['size']} bytes\n"
    response += f"🔤 Type: {result['content_type']}\n"
    response += f"📅 Modified: {result['file_info']['modified']}\n\n"
    response += "📖 Content:\n"
    response += "=" * 50 + "\n"
    response += result['content']
    
    return CallToolResult(
        content=[TextContent(type="text", text=response)]
    )


async def handle_write_file(arguments: Dict[str, Any]) -> CallToolResult:
    """Write to a file"""
    file_path = arguments["file_path"]
    content = arguments["content"]
    create_dirs = arguments.get("create_dirs", False)
    
    result = await file_manager.write_file(file_path, content, create_dirs)
    
    if "error" in result:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error writing file: {result['error']}")],
            isError=True
        )
    
    response = f"✅ {result['message']}\n"
    response += f"📊 Size: {result['size']} bytes\n"
    response += f"📅 Modified: {result['file_info']['modified']}"
    
    return CallToolResult(
        content=[TextContent(type="text", text=response)]
    )


async def handle_list_directory(arguments: Dict[str, Any]) -> CallToolResult:
    """List directory contents"""
    directory_path = arguments["directory_path"]
    include_hidden = arguments.get("include_hidden", False)
    
    result = await file_manager.list_directory(directory_path, include_hidden)
    
    if "error" in result:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error listing directory: {result['error']}")],
            isError=True
        )
    
    response = f"📁 Directory: {result['directory']}\n"
    response += f"📊 Total items: {result['total_items']} ({result['files']} files, {result['directories']} directories)\n\n"
    
    for item in result['items']:
        icon = "📁" if item.get('is_dir') else "📄"
        size = f" ({item['size']} bytes)" if item.get('is_file') else ""
        response += f"{icon} {item['name']}{size}\n"
    
    return CallToolResult(
        content=[TextContent(type="text", text=response)]
    )


async def handle_search_files(arguments: Dict[str, Any]) -> CallToolResult:
    """Search for files"""
    search_directory = arguments["search_directory"]
    pattern = arguments["pattern"]
    include_content = arguments.get("include_content", False)
    
    result = await file_manager.search_files(search_directory, pattern, include_content)
    
    if "error" in result:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error searching files: {result['error']}")],
            isError=True
        )
    
    response = f"🔍 Search Results\n"
    response += f"📁 Directory: {result['search_directory']}\n"
    response += f"🎯 Pattern: '{result['pattern']}'\n"
    response += f"📊 Found: {result['total_matches']} matches\n\n"
    
    for match in result['matches']:
        icon = "📁" if match.get('is_dir') else "📄"
        response += f"{icon} {match['path']} ({match['match_type']} match)\n"
        
        if match.get('matching_lines'):
            response += "   Content matches:\n"
            for line_info in match['matching_lines'][:3]:  # Show first 3 lines
                response += f"   Line {line_info['line']}: {line_info['text'][:80]}...\n"
    
    return CallToolResult(
        content=[TextContent(type="text", text=response)]
    )


async def handle_get_file_info(arguments: Dict[str, Any]) -> CallToolResult:
    """Get file information"""
    file_path = arguments["file_path"]
    
    try:
        path = Path(file_path)
        
        if not file_manager._is_path_allowed(path):
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Access denied - path not in allowed directories")],
                isError=True
            )
        
        if not path.exists():
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: File not found: {file_path}")],
                isError=True
            )
        
        info = file_manager._get_file_info(path)
        
        if "error" in info:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting file info: {info['error']}")],
                isError=True
            )
        
        response = f"📄 File Information\n"
        response += "=" * 30 + "\n"
        response += f"📛 Name: {info['name']}\n"
        response += f"📁 Path: {info['path']}\n"
        response += f"📊 Size: {info['size']} bytes\n"
        response += f"📅 Modified: {info['modified']}\n"
        response += f"📅 Created: {info['created']}\n"
        response += f"🔒 Permissions: {info['permissions']}\n"
        response += f"📎 MIME Type: {info.get('mime_type', 'Unknown')}\n"
        response += f"🏷️ Extension: {info['extension']}\n"
        response += f"📂 Type: {'File' if info['is_file'] else 'Directory'}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=response)]
        )
        
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            isError=True
        )


async def handle_get_file_hash(arguments: Dict[str, Any]) -> CallToolResult:
    """Get file hash"""
    file_path = arguments["file_path"]
    
    result = await file_manager.get_file_hash(file_path)
    
    if "error" in result:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error hashing file: {result['error']}")],
            isError=True
        )
    
    response = f"🔐 File Hash Information\n"
    response += "=" * 30 + "\n"
    response += f"📄 File: {result['file']}\n"
    response += f"📊 Size: {result['size']} bytes\n\n"
    response += f"MD5:    {result['md5']}\n"
    response += f"SHA1:   {result['sha1']}\n"
    response += f"SHA256: {result['sha256']}"
    
    return CallToolResult(
        content=[TextContent(type="text", text=response)]
    )


@server.list_resources()
async def handle_list_resources() -> ListResourcesResult:
    """List available file resources"""
    resources = [
        Resource(
            uri="file://security-config",
            name="Security Configuration",
            description="Current security settings and allowed directories",
            mimeType="application/json"
        ),
        Resource(
            uri="file://allowed-dirs",
            name="Allowed Directories",
            description="List of directories accessible to the file server",
            mimeType="text/plain"
        )
    ]
    
    return ListResourcesResult(resources=resources)


@server.get_resource()
async def handle_get_resource(uri: str) -> GetResourceResult:
    """Handle resource requests"""
    try:
        if uri == "file://security-config":
            config = {
                "max_file_size": MAX_FILE_SIZE,
                "allowed_extensions": list(ALLOWED_EXTENSIONS),
                "dangerous_extensions": list(DANGEROUS_EXTENSIONS),
                "allowed_directories": list(file_manager.allowed_dirs),
                "security_features": [
                    "Path traversal protection",
                    "File size limits",
                    "Extension filtering",
                    "Directory sandboxing",
                    "Permission validation"
                ]
            }
            
            return GetResourceResult(
                contents=[
                    TextContent(type="text", text=json.dumps(config, indent=2))
                ]
            )
            
        elif uri == "file://allowed-dirs":
            info = f"""Allowed Directories
==================

The file operations server is restricted to the following directories:

"""
            for i, dir_path in enumerate(sorted(file_manager.allowed_dirs), 1):
                info += f"{i}. {dir_path}\n"
            
            info += f"""
Security Notes:
- All file operations are sandboxed to these directories
- Path traversal attacks (../) are prevented
- Only safe file extensions are allowed
- File size is limited to {MAX_FILE_SIZE // (1024*1024)} MB
- Dangerous file types are blocked

To modify allowed directories, restart the server with different configuration.
"""
            
            return GetResourceResult(
                contents=[
                    TextContent(type="text", text=info)
                ]
            )
            
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
            
    except Exception as e:
        logger.error(f"Error getting resource {uri}: {e}")
        raise


async def main():
    """Main server function"""
    logger.info("Starting File Operations MCP Server")
    logger.info(f"Allowed directories: {file_manager.allowed_dirs}")
    logger.info(f"Security: Max file size {MAX_FILE_SIZE} bytes")
    
    async with stdio_server() as streams:
        await server.run(
            streams[0], streams[1],
            InitializationOptions(
                server_name="file-operations-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
