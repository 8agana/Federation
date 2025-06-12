"""
Native Git operations tool
NEW - Not in Desktop Commander
"""

import subprocess
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional, List

from .base import BaseTool

class GitTool(BaseTool):
    """Native Git operations for seamless version control"""
    
    @property
    def description(self) -> str:
        return """Native Git operations - status, commit, sync, branch management.
        
        Common operations:
        - git("status") - See current state
        - git("commit", "feat: new feature") - Stage all & commit
        - git("sync") - Add all, commit, push (federation-sync.sh in one command!)
        - git("branch", "feature-x") - Create/switch branches
        - git("push") - Push to remote
        - git("pull") - Pull from remote
        
        Features:
        - Automatic staging for commits
        - Smart commit messages
        - Federation-aware operations
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "commit", "sync", "branch", "push", "pull", "log", "diff"],
                    "description": "Git action to perform"
                },
                "message": {
                    "type": "string",
                    "description": "Commit message (for commit/sync actions)"
                },
                "branch": {
                    "type": "string",
                    "description": "Branch name (for branch action)"
                },
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Additional git options"
                }
            },
            "required": ["action"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        action = arguments["action"]
        message = arguments.get("message")
        branch = arguments.get("branch")
        options = arguments.get("options", [])
        
        # Check if in git repo
        if not self.context.is_git_repo():
            return {
                "status": "error",
                "error": "Not in a git repository"
            }
        
        # Get current git info
        git_info = self.context.get_git_info()
        
        # Execute action
        if action == "status":
            return await self._git_status()
        elif action == "commit":
            return await self._git_commit(message)
        elif action == "sync":
            return await self._git_sync(message)
        elif action == "branch":
            return await self._git_branch(branch)
        elif action == "push":
            return await self._git_push(options)
        elif action == "pull":
            return await self._git_pull(options)
        elif action == "log":
            return await self._git_log(options)
        elif action == "diff":
            return await self._git_diff(options)
        else:
            return {"status": "error", "error": f"Unknown action: {action}"}
    
    async def _run_git_command(self, args: List[str]) -> Dict[str, Any]:
        """Run a git command and return result"""
        try:
            process = await asyncio.create_subprocess_exec(
                "git", *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "status": "success" if process.returncode == 0 else "error",
                "exit_code": process.returncode,
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace')
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _git_status(self) -> Dict[str, Any]:
        """Get git status with helpful summary"""
        # Get regular status
        result = await self._run_git_command(["status", "-sb"])
        
        if result["status"] != "success":
            return result
        
        # Get more detailed info
        lines = result["stdout"].strip().split('\n')
        branch_info = lines[0] if lines else ""
        changes = lines[1:] if len(lines) > 1 else []
        
        # Count different types of changes
        staged = sum(1 for c in changes if c.startswith(('A ', 'M ', 'D ', 'R ')))
        modified = sum(1 for c in changes if c.startswith(' M') or c.startswith('MM'))
        untracked = sum(1 for c in changes if c.startswith('??'))
        
        # Get unpushed commits
        unpushed = await self._run_git_command(["log", "@{u}..", "--oneline"])
        unpushed_count = len(unpushed["stdout"].strip().split('\n')) if unpushed["stdout"].strip() else 0
        
        return {
            "status": "success",
            "branch": branch_info.replace("## ", ""),
            "summary": {
                "staged": staged,
                "modified": modified,
                "untracked": untracked,
                "unpushed": unpushed_count
            },
            "changes": changes,
            "clean": len(changes) == 0
        }
    
    async def _git_commit(self, message: Optional[str]) -> Dict[str, Any]:
        """Stage all changes and commit"""
        if not message:
            # Generate default message with timestamp
            from datetime import datetime
            message = f"Federation update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Stage all changes
        stage_result = await self._run_git_command(["add", "-A"])
        if stage_result["status"] != "success":
            return {
                "status": "error",
                "error": "Failed to stage changes",
                "details": stage_result
            }
        
        # Commit
        commit_result = await self._run_git_command(["commit", "-m", message])
        
        if commit_result["status"] == "success":
            # Get commit info
            info = await self._run_git_command(["log", "-1", "--oneline"])
            return {
                "status": "success",
                "message": "Changes committed successfully",
                "commit": info["stdout"].strip()
            }
        else:
            # Check if nothing to commit
            if "nothing to commit" in commit_result["stdout"]:
                return {
                    "status": "success",
                    "message": "Nothing to commit, working tree clean"
                }
            return {
                "status": "error",
                "error": "Commit failed",
                "details": commit_result
            }
    
    async def _git_sync(self, message: Optional[str]) -> Dict[str, Any]:
        """Federation sync - add, commit, push in one go"""
        # First pull to avoid conflicts
        pull_result = await self._git_pull([])
        if pull_result["status"] != "success" and "Already up to date" not in pull_result.get("stdout", ""):
            return {
                "status": "error", 
                "error": "Pull failed, resolve conflicts first",
                "details": pull_result
            }
        
        # Commit changes
        commit_result = await self._git_commit(message)
        if commit_result["status"] != "success":
            return commit_result
        
        # Push to remote
        push_result = await self._git_push([])
        
        if push_result["status"] == "success":
            return {
                "status": "success",
                "message": "Federation sync complete!",
                "operations": {
                    "pull": "success",
                    "commit": commit_result.get("commit", "no changes"),
                    "push": "success"
                }
            }
        else:
            return {
                "status": "error",
                "error": "Push failed",
                "details": push_result,
                "note": "Changes are committed locally"
            }
    
    async def _git_branch(self, branch_name: Optional[str]) -> Dict[str, Any]:
        """Create or switch branches"""
        if not branch_name:
            # List branches
            result = await self._run_git_command(["branch", "-a"])
            return result
        
        # Check if branch exists
        check = await self._run_git_command(["show-ref", "--verify", f"refs/heads/{branch_name}"])
        
        if check["status"] == "success":
            # Switch to existing branch
            result = await self._run_git_command(["checkout", branch_name])
        else:
            # Create and switch to new branch
            result = await self._run_git_command(["checkout", "-b", branch_name])
        
        return result
    
    async def _git_push(self, options: List[str]) -> Dict[str, Any]:
        """Push to remote"""
        args = ["push"] + options
        
        # Add upstream if first push on branch
        current_branch = self.context.get_git_info().get("branch", "main")
        check_upstream = await self._run_git_command(["config", f"branch.{current_branch}.remote"])
        
        if check_upstream["status"] != "success":
            args.extend(["-u", "origin", current_branch])
        
        return await self._run_git_command(args)
    
    async def _git_pull(self, options: List[str]) -> Dict[str, Any]:
        """Pull from remote"""
        return await self._run_git_command(["pull"] + options)
    
    async def _git_log(self, options: List[str]) -> Dict[str, Any]:
        """Show git log"""
        args = ["log", "--oneline", "-10"] + options
        return await self._run_git_command(args)
    
    async def _git_diff(self, options: List[str]) -> Dict[str, Any]:
        """Show git diff"""
        return await self._run_git_command(["diff"] + options)