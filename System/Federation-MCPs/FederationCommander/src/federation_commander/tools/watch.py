"""
File system monitor tool
NEW - Not in Desktop Commander
"""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
import hashlib
import time

from .base import BaseTool

class WatchTool(BaseTool):
    """Monitor file system changes with smart notifications"""
    
    def __init__(self, config, context):
        super().__init__(config, context)
        self.watchers = {}
        self.file_hashes = {}
    
    @property
    def description(self) -> str:
        return """Watch files and directories for changes with smart filtering.
        
        Examples:
        - watch(".") - Watch current directory
        - watch("src/", pattern="*.py") - Watch Python files in src
        - watch("config.json", on_change="reload") - Watch with action
        - watch(handle="w1", stop=True) - Stop watching
        
        Features:
        - Real-time file monitoring
        - Pattern filtering
        - Change type detection (create/modify/delete)
        - Smart ignore rules (git, node_modules, etc.)
        - Debounced notifications
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to watch"
                },
                "pattern": {
                    "type": "string",
                    "description": "File pattern to watch (e.g., '*.py')"
                },
                "recursive": {
                    "type": "boolean",
                    "default": True,
                    "description": "Watch subdirectories"
                },
                "on_change": {
                    "type": "string",
                    "description": "Action to take on change"
                },
                "debounce": {
                    "type": "number",
                    "default": 1.0,
                    "description": "Debounce time in seconds"
                },
                "handle": {
                    "type": "string",
                    "description": "Watch handle for status/stop"
                },
                "stop": {
                    "type": "boolean",
                    "default": False,
                    "description": "Stop watching"
                },
                "status": {
                    "type": "boolean",
                    "default": False,
                    "description": "Get watcher status"
                }
            }
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        handle = arguments.get("handle")
        stop = arguments.get("stop", False)
        status = arguments.get("status", False)
        
        # Handle status request
        if status:
            if handle and handle in self.watchers:
                watcher = self.watchers[handle]
                return {
                    "status": "success",
                    "handle": handle,
                    "watching": watcher["path"],
                    "pattern": watcher.get("pattern"),
                    "changes": watcher["changes"],
                    "started": watcher["started"]
                }
            else:
                return {
                    "status": "success",
                    "active_watchers": list(self.watchers.keys()),
                    "count": len(self.watchers)
                }
        
        # Handle stop request
        if stop:
            if not handle:
                return {"status": "error", "error": "Handle required to stop watcher"}
            
            if handle in self.watchers:
                watcher = self.watchers[handle]
                watcher["task"].cancel()
                del self.watchers[handle]
                return {
                    "status": "success",
                    "message": f"Stopped watching {watcher['path']}"
                }
            else:
                return {"status": "error", "error": f"No watcher found with handle: {handle}"}
        
        # Start new watcher
        path = arguments.get("path")
        if not path:
            return {"status": "error", "error": "Path required to start watching"}
        
        path_obj = Path(path).expanduser().resolve()
        if not path_obj.exists():
            return {"status": "error", "error": f"Path not found: {path}"}
        
        pattern = arguments.get("pattern")
        recursive = arguments.get("recursive", True)
        on_change = arguments.get("on_change")
        debounce = arguments.get("debounce", 1.0)
        
        # Generate handle
        if not handle:
            handle = f"watch_{int(time.time())}_{path_obj.name}"
        
        # Start watcher
        watcher_info = {
            "path": str(path_obj),
            "pattern": pattern,
            "recursive": recursive,
            "on_change": on_change,
            "debounce": debounce,
            "changes": [],
            "started": datetime.now().isoformat(),
            "task": None
        }
        
        # Create watcher task
        task = asyncio.create_task(
            self._watch_directory(handle, path_obj, watcher_info)
        )
        watcher_info["task"] = task
        
        self.watchers[handle] = watcher_info
        
        return {
            "status": "success",
            "handle": handle,
            "message": f"Started watching {path_obj}",
            "pattern": pattern,
            "recursive": recursive
        }
    
    async def _watch_directory(
        self, 
        handle: str, 
        path: Path, 
        watcher_info: Dict[str, Any]
    ):
        """Watch directory for changes"""
        pattern = watcher_info["pattern"]
        recursive = watcher_info["recursive"]
        debounce = watcher_info["debounce"]
        
        # Get initial file states
        file_states = await self._get_file_states(path, pattern, recursive)
        
        # Store initial hashes
        for file_path, state in file_states.items():
            self.file_hashes[file_path] = state["hash"]
        
        last_change_time = time.time()
        pending_changes = []
        
        try:
            while handle in self.watchers:
                await asyncio.sleep(0.5)  # Poll interval
                
                # Get current states
                current_states = await self._get_file_states(path, pattern, recursive)
                
                # Detect changes
                changes = self._detect_changes(file_states, current_states)
                
                if changes:
                    pending_changes.extend(changes)
                    last_change_time = time.time()
                
                # Process pending changes after debounce
                if pending_changes and (time.time() - last_change_time) >= debounce:
                    # Consolidate changes
                    consolidated = self._consolidate_changes(pending_changes)
                    
                    # Record changes
                    watcher_info["changes"].extend(consolidated)
                    
                    # Trigger action if specified
                    if watcher_info["on_change"]:
                        await self._trigger_action(
                            watcher_info["on_change"], 
                            consolidated
                        )
                    
                    # Clear pending
                    pending_changes = []
                
                # Update file states
                file_states = current_states
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            watcher_info["error"] = str(e)
    
    async def _get_file_states(
        self, 
        path: Path, 
        pattern: Optional[str],
        recursive: bool
    ) -> Dict[str, Dict[str, Any]]:
        """Get current state of all matching files"""
        states = {}
        
        # Get gitignore patterns
        ignored = self.context.get_gitignore_patterns(path)
        
        # Always ignore certain patterns
        default_ignores = [
            "*.pyc", "__pycache__", "node_modules", ".git", ".DS_Store",
            "*.swp", "*.swo", "*~", ".idea", ".vscode"
        ]
        ignored.extend(default_ignores)
        
        if path.is_file():
            # Watch single file
            if not any(self._matches_pattern(path, ign) for ign in ignored):
                if not pattern or self._matches_pattern(path, pattern):
                    states[str(path)] = await self._get_file_state(path)
        else:
            # Watch directory
            if recursive:
                iterator = path.rglob("*")
            else:
                iterator = path.glob("*")
            
            for item in iterator:
                if item.is_file():
                    # Skip ignored files
                    if any(self._matches_pattern(item, ign) for ign in ignored):
                        continue
                    
                    # Check pattern match
                    if pattern and not self._matches_pattern(item, pattern):
                        continue
                    
                    states[str(item)] = await self._get_file_state(item)
        
        return states
    
    async def _get_file_state(self, path: Path) -> Dict[str, Any]:
        """Get file state (size, mtime, hash)"""
        try:
            stat = path.stat()
            
            # Calculate hash for small files
            file_hash = None
            if stat.st_size < 1024 * 1024:  # 1MB
                try:
                    with open(path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                except:
                    pass
            
            return {
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "hash": file_hash
            }
        except:
            return None
    
    def _detect_changes(
        self,
        old_states: Dict[str, Dict[str, Any]],
        new_states: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect file changes"""
        changes = []
        
        # Check for new and modified files
        for path, new_state in new_states.items():
            if path not in old_states:
                changes.append({
                    "type": "created",
                    "path": path,
                    "time": datetime.now().isoformat()
                })
            elif new_state != old_states[path]:
                # Check what changed
                old_state = old_states[path]
                change_type = "modified"
                
                if new_state.get("hash") and old_state.get("hash"):
                    if new_state["hash"] == old_state["hash"]:
                        # Only metadata changed
                        change_type = "touched"
                
                changes.append({
                    "type": change_type,
                    "path": path,
                    "time": datetime.now().isoformat(),
                    "size_change": new_state["size"] - old_state["size"]
                })
        
        # Check for deleted files
        for path in old_states:
            if path not in new_states:
                changes.append({
                    "type": "deleted",
                    "path": path,
                    "time": datetime.now().isoformat()
                })
        
        return changes
    
    def _consolidate_changes(self, changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolidate multiple changes to same file"""
        consolidated = {}
        
        for change in changes:
            path = change["path"]
            
            if path not in consolidated:
                consolidated[path] = change
            else:
                # Update existing change
                existing = consolidated[path]
                
                # Handle state transitions
                if existing["type"] == "created" and change["type"] == "deleted":
                    # Created then deleted - remove from consolidated
                    del consolidated[path]
                elif existing["type"] == "deleted" and change["type"] == "created":
                    # Deleted then created - mark as modified
                    consolidated[path] = {
                        "type": "modified",
                        "path": path,
                        "time": change["time"]
                    }
                else:
                    # Keep latest change
                    consolidated[path] = change
        
        return list(consolidated.values())
    
    async def _trigger_action(self, action: str, changes: List[Dict[str, Any]]):
        """Trigger action on file changes"""
        # This is a placeholder for action triggers
        # Could integrate with other tools or send notifications
        pass
    
    def _matches_pattern(self, path: Path, pattern: str) -> bool:
        """Check if path matches pattern"""
        import fnmatch
        
        # Check full path and basename
        return (fnmatch.fnmatch(str(path), pattern) or 
                fnmatch.fnmatch(path.name, pattern))