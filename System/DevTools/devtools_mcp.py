#!/usr/bin/env python3
"""
DevTools MCP Server
Unified interface for GitHub and Docker operations

Provides developer tools for:
- Docker container management
- GitHub repository operations  
- Integrated DevOps workflows
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import json
import logging
import os
from datetime import datetime

# Import MCP SDK
try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
except ImportError:
    print("ERROR: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("devtools_mcp")

# Initialize MCP server
server = Server("devtools")

# Import handlers
from handlers.docker_handler import DockerHandler

# Initialize handlers
docker = DockerHandler()

# Try to initialize GitHub handler
github = None
try:
    from handlers.github_handler import GitHubHandler
    github = GitHubHandler()
    logger.info("GitHub handler initialized successfully")
except ValueError as e:
    logger.warning(f"GitHub handler not available: {e}")
except Exception as e:
    logger.error(f"Failed to initialize GitHub handler: {e}")


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available DevTools"""
    tools = [
        # Docker Tools
        types.Tool(
            name="docker_list_containers",
            description="List all Docker containers with their status, names, and basic info",
            inputSchema={
                "type": "object",
                "properties": {
                    "all": {
                        "type": "boolean", 
                        "description": "Show all containers (default shows just running)",
                        "default": False
                    }
                },
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="docker_create_container",
            description="Create and start a new Docker container from an image",
            inputSchema={
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "description": "Docker image name (e.g., 'nginx:latest', 'python:3.11')"
                    },
                    "name": {
                        "type": "string",
                        "description": "Container name (optional, Docker will generate if not provided)"
                    },
                    "ports": {
                        "type": "object",
                        "description": "Port mappings as {container_port: host_port}",
                        "additionalProperties": {"type": "string"}
                    },
                    "environment": {
                        "type": "object",
                        "description": "Environment variables as key-value pairs",
                        "additionalProperties": {"type": "string"}
                    },
                    "volumes": {
                        "type": "array",
                        "description": "Volume mappings as ['host_path:container_path']",
                        "items": {"type": "string"}
                    },
                    "command": {
                        "type": "string",
                        "description": "Command to run in container (overrides default)"
                    }
                },
                "required": ["image"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="docker_stop_container",
            description="Stop a running Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container": {
                        "type": "string",
                        "description": "Container name or ID"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Seconds to wait before killing (default: 10)",
                        "default": 10
                    }
                },
                "required": ["container"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="docker_remove_container",
            description="Remove a stopped Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container": {
                        "type": "string",
                        "description": "Container name or ID"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force removal of running container",
                        "default": False
                    }
                },
                "required": ["container"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="docker_container_logs",
            description="Get logs from a Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container": {
                        "type": "string",
                        "description": "Container name or ID"
                    },
                    "tail": {
                        "type": "integer",
                        "description": "Number of lines to show from end (default: 100)",
                        "default": 100
                    },
                    "follow": {
                        "type": "boolean",
                        "description": "Follow log output (will timeout after 5s)",
                        "default": False
                    }
                },
                "required": ["container"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="docker_exec_command",
            description="Execute a command inside a running Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container": {
                        "type": "string",
                        "description": "Container name or ID"
                    },
                    "command": {
                        "type": "string",
                        "description": "Command to execute (e.g., 'ls -la', 'python --version')"
                    },
                    "workdir": {
                        "type": "string",
                        "description": "Working directory inside container"
                    }
                },
                "required": ["container", "command"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="docker_list_images",
            description="List Docker images available locally",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "description": "Filter images by name"
                    }
                },
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="docker_pull_image",
            description="Pull a Docker image from registry",
            inputSchema={
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "description": "Image name with optional tag (e.g., 'ubuntu:22.04')"
                    }
                },
                "required": ["image"],
                "additionalProperties": False
            }
        )
    ]
    
    # Add GitHub tools if handler is available
    if github:
        tools.extend([
            types.Tool(
            name="github_search_code",
            description="Search for code across GitHub repositories",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (supports GitHub search syntax)"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Limit to specific repo (owner/name)"
                    },
                    "language": {
                        "type": "string",
                        "description": "Filter by programming language"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="github_get_repo",
            description="Get information about a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/name'"
                    }
                },
                "required": ["repo"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="github_list_repos",
            description="List repositories for a user or organization",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "GitHub username or organization"
                    },
                    "type": {
                        "type": "string",
                        "description": "Filter by type: all, owner, member",
                        "enum": ["all", "owner", "member"],
                        "default": "all"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort by: created, updated, pushed, name",
                        "enum": ["created", "updated", "pushed", "name"],
                        "default": "updated"
                    }
                },
                "required": ["owner"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="github_get_file",
            description="Get contents of a file from a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/name'"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to file in repository"
                    },
                    "ref": {
                        "type": "string",
                        "description": "Branch, tag, or commit SHA (default: main branch)"
                    }
                },
                "required": ["repo", "path"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="github_create_issue",
            description="Create a new issue in a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/name'"
                    },
                    "title": {
                        "type": "string",
                        "description": "Issue title"
                    },
                    "body": {
                        "type": "string",
                        "description": "Issue description (supports Markdown)"
                    },
                    "labels": {
                        "type": "array",
                        "description": "Labels to apply",
                        "items": {"type": "string"}
                    }
                },
                "required": ["repo", "title"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="github_list_issues",
            description="List issues in a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/name'"
                    },
                    "state": {
                        "type": "string",
                        "description": "Filter by state",
                        "enum": ["open", "closed", "all"],
                        "default": "open"
                    },
                    "labels": {
                        "type": "array",
                        "description": "Filter by labels",
                        "items": {"type": "string"}
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results (default: 20)",
                        "default": 20
                    }
                },
                "required": ["repo"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="github_create_pr",
            description="Create a pull request in a GitHub repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository in format 'owner/name'"
                    },
                    "title": {
                        "type": "string",
                        "description": "PR title"
                    },
                    "body": {
                        "type": "string",
                        "description": "PR description (supports Markdown)"
                    },
                    "head": {
                        "type": "string",
                        "description": "Branch containing changes"
                    },
                    "base": {
                        "type": "string",
                        "description": "Branch to merge into (default: main)",
                        "default": "main"
                    }
                },
                "required": ["repo", "title", "head"],
                "additionalProperties": False
            }
        )
        ])
    
    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
    """Route tool calls to appropriate handlers"""
    try:
        # Docker tools
        if name.startswith("docker_"):
            if name == "docker_list_containers":
                result = await docker.list_containers(arguments.get("all", False))
            elif name == "docker_create_container":
                result = await docker.create_container(arguments)
            elif name == "docker_stop_container":
                result = await docker.stop_container(
                    arguments["container"],
                    arguments.get("timeout", 10)
                )
            elif name == "docker_remove_container":
                result = await docker.remove_container(
                    arguments["container"],
                    arguments.get("force", False)
                )
            elif name == "docker_container_logs":
                result = await docker.get_logs(
                    arguments["container"],
                    arguments.get("tail", 100),
                    arguments.get("follow", False)
                )
            elif name == "docker_exec_command":
                result = await docker.exec_command(
                    arguments["container"],
                    arguments["command"],
                    arguments.get("workdir")
                )
            elif name == "docker_list_images":
                result = await docker.list_images(arguments.get("filter"))
            elif name == "docker_pull_image":
                result = await docker.pull_image(arguments["image"])
            else:
                raise ValueError(f"Unknown Docker tool: {name}")
                
        # GitHub tools
        elif name.startswith("github_"):
            if not github:
                raise ValueError("GitHub tools not available. Set GITHUB_PERSONAL_ACCESS_TOKEN environment variable.")
            
            if name == "github_search_code":
                result = await github.search_code(
                    arguments["query"],
                    arguments.get("repo"),
                    arguments.get("language"),
                    arguments.get("max_results", 10)
                )
            elif name == "github_get_repo":
                result = await github.get_repository(arguments["repo"])
            elif name == "github_list_repos":
                result = await github.list_repositories(
                    arguments["owner"],
                    arguments.get("type", "all"),
                    arguments.get("sort", "updated")
                )
            elif name == "github_get_file":
                result = await github.get_file(
                    arguments["repo"],
                    arguments["path"],
                    arguments.get("ref")
                )
            elif name == "github_create_issue":
                result = await github.create_issue(
                    arguments["repo"],
                    arguments["title"],
                    arguments.get("body", ""),
                    arguments.get("labels", [])
                )
            elif name == "github_list_issues":
                result = await github.list_issues(
                    arguments["repo"],
                    arguments.get("state", "open"),
                    arguments.get("labels"),
                    arguments.get("max_results", 20)
                )
            elif name == "github_create_pr":
                result = await github.create_pull_request(
                    arguments["repo"],
                    arguments["title"],
                    arguments["head"],
                    arguments.get("base", "main"),
                    arguments.get("body", "")
                )
            else:
                raise ValueError(f"Unknown GitHub tool: {name}")
        else:
            raise ValueError(f"Unknown tool: {name}")
            
        # Convert result to TextContent
        return [types.TextContent(type="text", text=str(result))]
        
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Run the DevTools MCP server"""
    logger.info("Starting DevTools MCP server...")
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="devtools",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(tools_changed=True),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())