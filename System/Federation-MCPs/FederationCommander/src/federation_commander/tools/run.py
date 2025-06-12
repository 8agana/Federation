"""
Universal command executor tool
Replaces: execute_command, read_output, force_terminate, list_sessions
"""

import asyncio
import os
import signal
import time
from pathlib import Path
from typing import Any, Dict, Optional
import subprocess

from .base import BaseTool

class RunTool(BaseTool):
    """Execute terminal commands with smart defaults"""
    
    def __init__(self, config, context):
        super().__init__(config, context)
        self.running_processes = {}
    
    @property
    def description(self) -> str:
        return """Execute terminal commands with streaming output and background support.
        
        Features:
        - Auto-detects appropriate shell
        - Shows git context when in repo  
        - Streaming output for long commands
        - Background execution with handle
        - Automatic timeout handling
        
        Examples:
        - run("git status")
        - run("npm install", timeout=60)
        - run("python server.py", background=True)
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "cmd": {
                    "type": "string",
                    "description": "Command to execute"
                },
                "timeout": {
                    "type": "integer", 
                    "description": "Timeout in seconds (default: 30)",
                    "default": 30
                },
                "background": {
                    "type": "boolean",
                    "description": "Run in background and return handle",
                    "default": False
                },
                "shell": {
                    "type": "string",
                    "description": "Shell to use (default: auto-detect)",
                    "default": "auto"
                }
            },
            "required": ["cmd"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        cmd = arguments["cmd"]
        timeout = arguments.get("timeout", self.config.get("default_timeout", 30))
        background = arguments.get("background", False)
        shell = arguments.get("shell", "auto")
        
        # Auto-detect shell if needed
        if shell == "auto":
            shell = self.config.get("shell", os.environ.get("SHELL", "/bin/bash"))
        
        # Add git context if in repo
        cwd = Path.cwd()
        git_info = self.context.get_git_info(cwd)
        
        result = {
            "command": cmd,
            "cwd": str(cwd),
            "shell": shell
        }
        
        if git_info:
            result["git"] = git_info
        
        try:
            if background:
                # Start background process
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    shell=True,
                    executable=shell,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd
                )
                
                handle = f"proc_{int(time.time())}_{process.pid}"
                self.running_processes[handle] = process
                
                result.update({
                    "status": "running",
                    "handle": handle,
                    "pid": process.pid,
                    "message": f"Process started in background. Use handle '{handle}' to check status."
                })
                
            else:
                # Run with timeout
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    shell=True,
                    executable=shell,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout
                    )
                    
                    result.update({
                        "status": "completed",
                        "exit_code": process.returncode,
                        "stdout": stdout.decode('utf-8', errors='replace'),
                        "stderr": stderr.decode('utf-8', errors='replace')
                    })
                    
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    
                    result.update({
                        "status": "timeout",
                        "message": f"Command timed out after {timeout} seconds",
                        "partial_output": await self._get_partial_output(process)
                    })
                    
        except Exception as e:
            result.update({
                "status": "error",
                "error": str(e)
            })
        
        return result
    
    async def _get_partial_output(self, process) -> Dict[str, str]:
        """Get any partial output from a process"""
        output = {}
        
        try:
            if process.stdout:
                output["stdout"] = await process.stdout.read()
                output["stdout"] = output["stdout"].decode('utf-8', errors='replace')
        except:
            pass
            
        try:
            if process.stderr:
                output["stderr"] = await process.stderr.read() 
                output["stderr"] = output["stderr"].decode('utf-8', errors='replace')
        except:
            pass
            
        return output