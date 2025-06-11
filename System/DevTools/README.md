# DevTools MCP Server

Unified interface for GitHub and Docker operations through Model Context Protocol (MCP).

## Features

### Docker Tools (8 tools)
- `docker_list_containers` - List all Docker containers with status info
- `docker_create_container` - Create and start new containers
- `docker_stop_container` - Stop running containers  
- `docker_remove_container` - Remove containers
- `docker_container_logs` - View container logs
- `docker_exec_command` - Execute commands in containers
- `docker_list_images` - List available Docker images
- `docker_pull_image` - Pull images from registry

### GitHub Tools (7 tools)
- `github_search_code` - Search code across repositories
- `github_get_repo` - Get repository information
- `github_list_repos` - List user/org repositories
- `github_get_file` - Read file contents from repos
- `github_create_issue` - Create new issues
- `github_list_issues` - List repository issues
- `github_create_pr` - Create pull requests

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set GitHub token:
```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="your-token-here"
```

3. Ensure Docker is running

## Configuration

Add to DT's config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "devtools": {
      "command": "python3",
      "args": [
        "/Users/samuelatagana/Documents/Federation/System/DevTools/run_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-github-pat"
      }
    }
  }
}
```

## Usage Examples

### Docker
- List containers: `docker_list_containers {"all": true}`
- Create container: `docker_create_container {"image": "nginx:latest", "name": "webserver", "ports": {"80": "8080"}}`
- View logs: `docker_container_logs {"container": "webserver", "tail": 50}`

### GitHub  
- Search code: `github_search_code {"query": "federation", "language": "python"}`
- Get repo: `github_get_repo {"repo": "anthropics/claude-code"}`
- Create issue: `github_create_issue {"repo": "owner/repo", "title": "Bug report", "body": "Description"}`

## Architecture

```
DevTools/
├── devtools_mcp.py      # Main MCP server
├── run_server.py        # Server runner
├── handlers/
│   ├── docker_handler.py # Docker operations
│   └── github_handler.py # GitHub operations
└── requirements.txt     # Dependencies
```

## Error Handling

- Docker daemon connection errors
- GitHub authentication failures  
- Resource not found errors
- API rate limiting

All errors return descriptive messages to help troubleshoot.

## Security

- GitHub PAT stored as environment variable
- Docker operations require daemon access
- No credentials stored in code

## Development

Created by CC as part of the Federation DevTools initiative.