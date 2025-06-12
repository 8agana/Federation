"""
GitHub Handler for DevTools MCP
Manages GitHub operations using PyGithub library
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import base64

try:
    from github import Github, GithubException
    from github.GithubException import UnknownObjectException, BadCredentialsException
except ImportError:
    raise ImportError("PyGithub package not installed. Install with: pip install PyGithub")

logger = logging.getLogger("devtools.github")


class GitHubHandler:
    """Handle GitHub operations"""
    
    def __init__(self):
        """Initialize GitHub client"""
        # Get token from environment
        token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
        if not token:
            raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN not set in environment")
        
        try:
            self.client = Github(token)
            # Test authentication
            self.user = self.client.get_user()
            logger.info(f"GitHub client initialized for user: {self.user.login}")
        except BadCredentialsException:
            raise ValueError("Invalid GitHub token")
        except Exception as e:
            logger.error(f"Failed to initialize GitHub client: {e}")
            raise
    
    async def search_code(self, query: str, repo: Optional[str] = None, 
                         language: Optional[str] = None, max_results: int = 10) -> str:
        """Search for code across GitHub"""
        try:
            # Build search query
            search_query = query
            if repo:
                search_query += f" repo:{repo}"
            if language:
                search_query += f" language:{language}"
            
            # Search code
            results = await asyncio.to_thread(
                self.client.search_code,
                query=search_query
            )
            
            items = []
            for i, code in enumerate(results):
                if i >= max_results:
                    break
                    
                item = {
                    "repository": code.repository.full_name,
                    "path": code.path,
                    "url": code.html_url,
                    "sha": code.sha,
                    "score": code.score
                }
                items.append(item)
            
            return json.dumps({
                "total_count": results.totalCount,
                "items": items
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error searching code: {e}")
            return f"Error searching code: {str(e)}"
    
    async def get_repository(self, repo_name: str) -> str:
        """Get repository information"""
        try:
            repo = await asyncio.to_thread(self.client.get_repo, repo_name)
            
            info = {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "owner": repo.owner.login,
                "private": repo.private,
                "fork": repo.fork,
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "pushed_at": repo.pushed_at.isoformat() if repo.pushed_at else None,
                "size": repo.size,
                "stargazers_count": repo.stargazers_count,
                "watchers_count": repo.watchers_count,
                "language": repo.language,
                "forks_count": repo.forks_count,
                "open_issues_count": repo.open_issues_count,
                "default_branch": repo.default_branch,
                "topics": repo.get_topics(),
                "html_url": repo.html_url,
                "clone_url": repo.clone_url
            }
            
            return json.dumps(info, indent=2)
            
        except UnknownObjectException:
            return f"Repository {repo_name} not found"
        except Exception as e:
            logger.error(f"Error getting repository: {e}")
            return f"Error getting repository: {str(e)}"
    
    async def list_repositories(self, owner: str, type: str = "all", sort: str = "updated") -> str:
        """List repositories for user/org"""
        try:
            # Determine if owner is user or org
            try:
                user = await asyncio.to_thread(self.client.get_user, owner)
                repos = await asyncio.to_thread(user.get_repos, type=type, sort=sort)
            except UnknownObjectException:
                # Try as organization
                org = await asyncio.to_thread(self.client.get_organization, owner)
                repos = await asyncio.to_thread(org.get_repos, type=type, sort=sort)
            
            result = []
            for repo in repos[:30]:  # Limit to 30 repos
                info = {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "private": repo.private,
                    "fork": repo.fork,
                    "language": repo.language,
                    "updated_at": repo.updated_at.isoformat(),
                    "stargazers_count": repo.stargazers_count,
                    "html_url": repo.html_url
                }
                result.append(info)
            
            return json.dumps(result, indent=2)
            
        except UnknownObjectException:
            return f"User/Organization {owner} not found"
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            return f"Error listing repositories: {str(e)}"
    
    async def get_file(self, repo_name: str, file_path: str, ref: Optional[str] = None) -> str:
        """Get file contents from repository"""
        try:
            repo = await asyncio.to_thread(self.client.get_repo, repo_name)
            
            # Get file contents
            contents = await asyncio.to_thread(
                repo.get_contents,
                file_path,
                ref=ref
            )
            
            if contents.type != "file":
                return f"Path {file_path} is not a file"
            
            # Decode content
            content = base64.b64decode(contents.content).decode('utf-8')
            
            result = {
                "path": contents.path,
                "name": contents.name,
                "sha": contents.sha,
                "size": contents.size,
                "content": content,
                "download_url": contents.download_url
            }
            
            return json.dumps(result, indent=2)
            
        except UnknownObjectException as e:
            return f"File or repository not found: {str(e)}"
        except Exception as e:
            logger.error(f"Error getting file: {e}")
            return f"Error getting file: {str(e)}"
    
    async def create_issue(self, repo_name: str, title: str, body: str = "", 
                          labels: List[str] = None) -> str:
        """Create a new issue"""
        try:
            repo = await asyncio.to_thread(self.client.get_repo, repo_name)
            
            # Create issue
            issue = await asyncio.to_thread(
                repo.create_issue,
                title=title,
                body=body,
                labels=labels or []
            )
            
            result = {
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "html_url": issue.html_url,
                "created_at": issue.created_at.isoformat(),
                "user": issue.user.login
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            return f"Error creating issue: {str(e)}"
    
    async def list_issues(self, repo_name: str, state: str = "open", 
                         labels: Optional[List[str]] = None, max_results: int = 20) -> str:
        """List repository issues"""
        try:
            repo = await asyncio.to_thread(self.client.get_repo, repo_name)
            
            # Get issues
            issues = await asyncio.to_thread(
                repo.get_issues,
                state=state,
                labels=labels or []
            )
            
            result = []
            for i, issue in enumerate(issues):
                if i >= max_results:
                    break
                    
                # Skip pull requests
                if issue.pull_request:
                    continue
                    
                info = {
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "user": issue.user.login,
                    "assignee": issue.assignee.login if issue.assignee else None,
                    "labels": [label.name for label in issue.labels],
                    "comments": issue.comments,
                    "html_url": issue.html_url
                }
                result.append(info)
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error listing issues: {e}")
            return f"Error listing issues: {str(e)}"
    
    async def create_pull_request(self, repo_name: str, title: str, head: str, 
                                 base: str = "main", body: str = "") -> str:
        """Create a pull request"""
        try:
            repo = await asyncio.to_thread(self.client.get_repo, repo_name)
            
            # Create PR
            pr = await asyncio.to_thread(
                repo.create_pull,
                title=title,
                body=body,
                head=head,
                base=base
            )
            
            result = {
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "html_url": pr.html_url,
                "created_at": pr.created_at.isoformat(),
                "user": pr.user.login,
                "head": pr.head.ref,
                "base": pr.base.ref,
                "mergeable": pr.mergeable
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error creating pull request: {e}")
            return f"Error creating pull request: {str(e)}"