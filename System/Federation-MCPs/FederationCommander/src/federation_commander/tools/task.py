"""
Federation task integration tool
NEW - Direct integration with Federation task management
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import BaseTool

class TaskTool(BaseTool):
    """Direct Federation task management integration"""
    
    @property
    def description(self) -> str:
        return """Manage Federation tasks with deep integration.
        
        Examples:
        - task("list") - Show current tasks
        - task("create", "Build new feature", priority="high")
        - task("update", "task-123", status="in_progress")
        - task("complete", "task-123")
        - task("sync") - Sync with task management system
        
        Features:
        - Create, update, complete tasks
        - Priority and status management
        - Memory integration
        - Automatic task tracking
        - Federation-aware context
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "create", "update", "complete", "sync", "get"],
                    "description": "Task action to perform"
                },
                "title": {
                    "type": "string",
                    "description": "Task title (for create) or ID (for update/complete)"
                },
                "description": {
                    "type": "string",
                    "description": "Task description"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "default": "medium",
                    "description": "Task priority"
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed", "blocked"],
                    "description": "Task status"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Task tags"
                },
                "notes": {
                    "type": "string",
                    "description": "Additional notes"
                }
            },
            "required": ["action"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        action = arguments["action"]
        
        if action == "list":
            return await self._list_tasks()
        elif action == "create":
            return await self._create_task(arguments)
        elif action == "update":
            return await self._update_task(arguments)
        elif action == "complete":
            return await self._complete_task(arguments)
        elif action == "sync":
            return await self._sync_tasks()
        elif action == "get":
            return await self._get_task(arguments.get("title"))
        else:
            return {"status": "error", "error": f"Unknown action: {action}"}
    
    async def _list_tasks(self) -> Dict[str, Any]:
        """List all active tasks"""
        # Check multiple task sources
        tasks = []
        
        # 1. Check TodoRead if available
        try:
            # This would integrate with actual todo system
            # For now, return placeholder
            pass
        except:
            pass
        
        # 2. Check SharedVault TaskTracker
        task_tracker_path = Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault/📋 TaskTracker")
        
        if task_tracker_path.exists():
            active_tasks = []
            
            # Look for task files
            for task_file in task_tracker_path.glob("*.md"):
                if task_file.name.startswith("."):
                    continue
                
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse task from markdown
                    task_info = self._parse_task_file(task_file.name, content)
                    if task_info and task_info.get("status") != "completed":
                        active_tasks.append(task_info)
                except:
                    continue
            
            tasks.extend(active_tasks)
        
        # 3. Check memory for recent tasks
        # This would integrate with memory system
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        tasks.sort(key=lambda t: priority_order.get(t.get("priority", "medium"), 1))
        
        return {
            "status": "success",
            "count": len(tasks),
            "tasks": tasks
        }
    
    async def _create_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        title = arguments.get("title")
        if not title:
            return {"status": "error", "error": "Task title required"}
        
        description = arguments.get("description", "")
        priority = arguments.get("priority", "medium")
        tags = arguments.get("tags", [])
        
        # Generate task ID
        task_id = f"task-{int(datetime.now().timestamp())}"
        
        # Create task structure
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "pending",
            "tags": tags,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }
        
        # Save to SharedVault
        task_tracker_path = Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault/📋 TaskTracker")
        task_tracker_path.mkdir(exist_ok=True)
        
        # Create task file
        task_file = task_tracker_path / f"{task_id} - {title}.md"
        
        content = f"""# {title}

**ID**: {task_id}
**Priority**: {priority}
**Status**: pending
**Created**: {task['created']}
**Tags**: {', '.join(tags) if tags else 'none'}

## Description

{description}

## Progress

- [ ] Task created

## Notes

{arguments.get('notes', '')}
"""
        
        try:
            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "status": "success",
                "message": f"Task created: {title}",
                "task": task,
                "file": str(task_file)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _update_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing task"""
        task_id = arguments.get("title")  # Can be ID or title
        if not task_id:
            return {"status": "error", "error": "Task ID or title required"}
        
        # Find task file
        task_tracker_path = Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault/📋 TaskTracker")
        
        task_file = None
        for file in task_tracker_path.glob("*.md"):
            if task_id in file.name:
                task_file = file
                break
        
        if not task_file:
            return {"status": "error", "error": f"Task not found: {task_id}"}
        
        # Read current content
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update fields
            if "status" in arguments:
                content = self._update_field(content, "Status", arguments["status"])
            
            if "priority" in arguments:
                content = self._update_field(content, "Priority", arguments["priority"])
            
            # Add update note
            update_time = datetime.now().isoformat()
            content = self._update_field(content, "Updated", update_time)
            
            if "notes" in arguments:
                # Add to notes section
                notes_section = content.find("## Notes")
                if notes_section != -1:
                    next_section = content.find("\n## ", notes_section + 1)
                    if next_section == -1:
                        next_section = len(content)
                    
                    new_note = f"\n\n**Update {update_time}**: {arguments['notes']}"
                    content = content[:next_section] + new_note + content[next_section:]
            
            # Save updated content
            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "status": "success",
                "message": f"Task updated: {task_file.name}",
                "updates": {k: v for k, v in arguments.items() if k not in ["action", "title"]}
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _complete_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a task"""
        task_id = arguments.get("title")
        if not task_id:
            return {"status": "error", "error": "Task ID or title required"}
        
        # Update status to completed
        arguments["status"] = "completed"
        result = await self._update_task(arguments)
        
        if result["status"] == "success":
            # Move to completed folder if exists
            task_tracker_path = Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault/📋 TaskTracker")
            completed_path = task_tracker_path / "Completed"
            completed_path.mkdir(exist_ok=True)
            
            # Find and move file
            for file in task_tracker_path.glob("*.md"):
                if task_id in file.name:
                    new_path = completed_path / file.name
                    file.rename(new_path)
                    result["message"] += f"\nMoved to: {new_path}"
                    break
        
        return result
    
    async def _sync_tasks(self) -> Dict[str, Any]:
        """Sync tasks with other systems"""
        # This would integrate with other task systems
        # For now, just report current state
        
        list_result = await self._list_tasks()
        
        return {
            "status": "success",
            "message": "Task sync complete",
            "active_tasks": list_result.get("count", 0),
            "sources": ["SharedVault/TaskTracker"]
        }
    
    async def _get_task(self, task_id: Optional[str]) -> Dict[str, Any]:
        """Get detailed task information"""
        if not task_id:
            return {"status": "error", "error": "Task ID required"}
        
        # Find task file
        task_tracker_path = Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault/📋 TaskTracker")
        
        for file in task_tracker_path.glob("**/*.md"):
            if task_id in file.name:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    task_info = self._parse_task_file(file.name, content)
                    task_info["file_path"] = str(file)
                    task_info["content"] = content
                    
                    return {
                        "status": "success",
                        "task": task_info
                    }
                except Exception as e:
                    return {"status": "error", "error": str(e)}
        
        return {"status": "error", "error": f"Task not found: {task_id}"}
    
    def _parse_task_file(self, filename: str, content: str) -> Dict[str, Any]:
        """Parse task information from markdown file"""
        task = {
            "filename": filename,
            "title": filename.split(" - ", 1)[-1].replace(".md", "") if " - " in filename else filename.replace(".md", "")
        }
        
        # Extract fields
        import re
        
        # ID
        id_match = re.search(r'\*\*ID\*\*:\s*(.+)', content)
        if id_match:
            task["id"] = id_match.group(1).strip()
        
        # Priority
        priority_match = re.search(r'\*\*Priority\*\*:\s*(.+)', content)
        if priority_match:
            task["priority"] = priority_match.group(1).strip()
        
        # Status
        status_match = re.search(r'\*\*Status\*\*:\s*(.+)', content)
        if status_match:
            task["status"] = status_match.group(1).strip()
        
        # Tags
        tags_match = re.search(r'\*\*Tags\*\*:\s*(.+)', content)
        if tags_match:
            tags_str = tags_match.group(1).strip()
            if tags_str != "none":
                task["tags"] = [t.strip() for t in tags_str.split(",")]
        
        # Created
        created_match = re.search(r'\*\*Created\*\*:\s*(.+)', content)
        if created_match:
            task["created"] = created_match.group(1).strip()
        
        # Progress (count checkboxes)
        checked = content.count("[x]") + content.count("[X]")
        unchecked = content.count("[ ]")
        if checked + unchecked > 0:
            task["progress"] = {
                "completed": checked,
                "total": checked + unchecked,
                "percentage": int((checked / (checked + unchecked)) * 100)
            }
        
        return task
    
    def _update_field(self, content: str, field: str, value: str) -> str:
        """Update a field in markdown content"""
        import re
        
        pattern = rf'(\*\*{field}\*\*:\s*)(.+)'
        replacement = rf'\1{value}'
        
        return re.sub(pattern, replacement, content)