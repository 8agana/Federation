#!/usr/bin/env python3
"""
TaskTracker Core Operations
Handles task creation, updates, and retrieval
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib

# Import relationship manager
try:
    from task_relationships import TaskRelationshipManager
except ImportError:
    # Fallback if not available yet
    TaskRelationshipManager = None

# Base paths
TASKS_ROOT = Path("/Users/samuelatagana/Library/MobileDocuments/iCloud~md~obsidian/Documents/SharedVault/📋 TaskTracker")
MANIFEST_PATH = TASKS_ROOT / "manifest.json"

class TaskOperations:
    """Core task management operations"""
    
    def __init__(self):
        """Initialize task operations"""
        # Disabled auto-creation of task directories and files
        # TASKS_ROOT.mkdir(parents=True, exist_ok=True)
        # (TASKS_ROOT / "Complete").mkdir(exist_ok=True)
        # (TASKS_ROOT / "Backburner").mkdir(exist_ok=True)
        
        # Don't auto-create manifest - only load if exists
        self.manifest = self._load_manifest() if MANIFEST_PATH.exists() else {"tasks": {}, "total_tasks": 0}
        
        # Initialize relationship manager if available
        self.relationships = TaskRelationshipManager() if TaskRelationshipManager else None
        
        # Initialize wake manager
        try:
            from wake_manager import WakeManager
            self.wake_manager = WakeManager()
        except ImportError:
            print("⚠️  WakeManager not available", file=sys.stderr)
            self.wake_manager = None
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load global task manifest"""
        if MANIFEST_PATH.exists():
            with open(MANIFEST_PATH, 'r') as f:
                return json.load(f)
        else:
            # Don't auto-create manifest file
            return {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "tasks": {},
                "total_tasks": 0
            }
    
    def _save_manifest(self, manifest: Dict[str, Any]) -> None:
        """Save global task manifest"""
        with open(MANIFEST_PATH, 'w') as f:
            json.dump(manifest, f, indent=2)
    
    def _generate_task_id(self, title: str) -> str:
        """Generate timestamped task ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        # Clean title for directory name
        clean_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
        clean_title = clean_title.replace(" ", "_")[:50]  # Limit length
        return f"{timestamp}_{clean_title}"
    
    def create_task(self, title: str, description: str, 
                   participants: Optional[List[str]] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   parent_task: Optional[str] = None,
                   branch_type: str = "spawn") -> Dict[str, Any]:
        """
        Create a new task with foundation entry
        
        Returns:
            Task creation result with task_id
        """
        try:
            # Generate task ID
            task_id = self._generate_task_id(title)
            task_dir = TASKS_ROOT / task_id
            
            # Create task directory
            task_dir.mkdir(parents=True, exist_ok=True)
            
            # Create foundation entry
            timestamp = datetime.now()
            foundation_entry = {
                "type": "foundation",
                "task_id": task_id,
                "timestamp": timestamp.isoformat(),
                "title": title,
                "description": description,
                "status": "foundation",
                "phase": "planning",
                "participants": participants or ["CC"],
                "conversation_links": [],
                "related_tasks": [],
                "related_files": [],
                "metadata": metadata or {
                    "priority": "medium",
                    "tags": [],
                },
                "content": f"Task created: {title}\\n\\n{description}"
            }
            
            # Save foundation entry
            entry_filename = f"{timestamp.strftime('%Y%m%d_%H%M')}_Foundation.json"
            entry_path = task_dir / entry_filename
            with open(entry_path, 'w') as f:
                json.dump(foundation_entry, f, indent=2)
            
            # Create task index
            task_index = {
                "task_id": task_id,
                "title": title,
                "created": timestamp.isoformat(),
                "updated": timestamp.isoformat(),
                "status": "foundation",
                "phase": "planning",
                "entries": [entry_filename],
                "participants": participants or ["CC"],
                "parent_task": parent_task,
                "branch_type": branch_type if parent_task else None
            }
            
            index_path = task_dir / "index.json"
            with open(index_path, 'w') as f:
                json.dump(task_index, f, indent=2)
            
            # Update manifest
            self.manifest["tasks"][task_id] = {
                "title": title,
                "created": timestamp.isoformat(),
                "status": "foundation",
                "phase": "planning"
            }
            self.manifest["total_tasks"] += 1
            self._save_manifest(self.manifest)
            
            # Track relationship if parent specified
            if parent_task and self.relationships:
                if branch_type == "spawn":
                    self.relationships.create_spawn(parent_task, task_id, f"Implementation of {title}")
                elif branch_type == "fork":
                    self.relationships.create_fork(parent_task, task_id, f"Alternative approach: {title}")
            
            # Send auto-wake notification
            if self.wake_manager:
                wake_message = f"New task created: {title}"
                self.wake_manager.auto_wake_for_event("create", wake_message, task_id)
            
            return {
                "success": True,
                "task_id": task_id,
                "path": str(task_dir),
                "message": f"Task '{title}' created successfully",
                "parent_task": parent_task,
                "branch_type": branch_type if parent_task else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create task: {e}"
            }
    
    def add_task_entry(self, task_id: str, entry_type: str, 
                      content: str, participants: Optional[List[str]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add an entry to existing task
        
        Entry types: discussion, implementation, progress, complete
        """
        try:
            task_dir = TASKS_ROOT / task_id
            if not task_dir.exists():
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"Task {task_id} does not exist"
                }
            
            # Load task index
            index_path = task_dir / "index.json"
            with open(index_path, 'r') as f:
                task_index = json.load(f)
            
            # Create new entry
            timestamp = datetime.now()
            entry = {
                "type": entry_type,
                "task_id": task_id,
                "timestamp": timestamp.isoformat(),
                "participants": participants or task_index.get("participants", ["CC"]),
                "metadata": metadata or {},
                "content": content
            }
            
            # Determine filename
            type_name = entry_type.capitalize()
            entry_filename = f"{timestamp.strftime('%Y%m%d_%H%M')}_{type_name}.json"
            entry_path = task_dir / entry_filename
            
            # Save entry
            with open(entry_path, 'w') as f:
                json.dump(entry, f, indent=2)
            
            # Update task index
            task_index["entries"].append(entry_filename)
            task_index["updated"] = timestamp.isoformat()
            
            # Update status based on entry type
            if entry_type == "complete":
                task_index["status"] = "complete"
                task_index["phase"] = "complete"
            elif entry_type == "implementation":
                task_index["status"] = "active"
                task_index["phase"] = "implementing"
            elif entry_type == "progress":
                task_index["status"] = "active"
            
            with open(index_path, 'w') as f:
                json.dump(task_index, f, indent=2)
            
            # Update manifest
            if task_id in self.manifest["tasks"]:
                self.manifest["tasks"][task_id]["status"] = task_index["status"]
                self.manifest["tasks"][task_id]["phase"] = task_index["phase"]
                self._save_manifest(self.manifest)
            
            return {
                "success": True,
                "entry_file": entry_filename,
                "message": f"Added {entry_type} entry to task {task_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to add entry: {e}"
            }
    
    def get_task_details(self, task_id: str) -> Dict[str, Any]:
        """Get complete task details including all entries"""
        try:
            task_dir = TASKS_ROOT / task_id
            if not task_dir.exists():
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"Task {task_id} does not exist"
                }
            
            # Load task index
            index_path = task_dir / "index.json"
            with open(index_path, 'r') as f:
                task_index = json.load(f)
            
            # Load all entries
            entries = []
            for entry_file in task_index.get("entries", []):
                entry_path = task_dir / entry_file
                if entry_path.exists():
                    with open(entry_path, 'r') as f:
                        entries.append(json.load(f))
            
            return {
                "success": True,
                "task_id": task_id,
                "index": task_index,
                "entries": entries,
                "entry_count": len(entries)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get task details: {e}"
            }
    
    def list_active_tasks(self) -> Dict[str, Any]:
        """List all active tasks"""
        try:
            active_tasks = []
            
            for task_id, task_info in self.manifest.get("tasks", {}).items():
                if task_info.get("status") not in ["complete", "cancelled"]:
                    active_tasks.append({
                        "task_id": task_id,
                        "title": task_info.get("title"),
                        "status": task_info.get("status"),
                        "phase": task_info.get("phase"),
                        "created": task_info.get("created")
                    })
            
            # Sort by creation date (newest first)
            active_tasks.sort(key=lambda x: x.get("created", ""), reverse=True)
            
            return {
                "success": True,
                "active_tasks": active_tasks,
                "count": len(active_tasks)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list active tasks: {e}"
            }
    
    def update_task_status(self, task_id: str, new_status: str, 
                          phase: Optional[str] = None) -> Dict[str, Any]:
        """Update task status and optionally phase, with automatic folder movement"""
        try:
            # Determine current location
            current_dir = None
            for location in [TASKS_ROOT, TASKS_ROOT / "Complete", TASKS_ROOT / "Backburner"]:
                if (location / task_id).exists():
                    current_dir = location / task_id
                    break
            
            if not current_dir:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"Task {task_id} does not exist"
                }
            
            # Update task index
            index_path = current_dir / "index.json"
            with open(index_path, 'r') as f:
                task_index = json.load(f)
            
            task_index["status"] = new_status
            if phase:
                task_index["phase"] = phase
            task_index["updated"] = datetime.now().isoformat()
            
            with open(index_path, 'w') as f:
                json.dump(task_index, f, indent=2)
            
            # Determine target directory based on status
            if new_status == "complete":
                target_dir = TASKS_ROOT / "Complete" / task_id
            elif new_status == "backburner":
                target_dir = TASKS_ROOT / "Backburner" / task_id
            else:
                target_dir = TASKS_ROOT / task_id
            
            # Move task if needed
            moved = False
            move_msg = ""
            if str(current_dir) != str(target_dir):
                import shutil
                shutil.move(str(current_dir), str(target_dir))
                moved = True
                move_msg = f" and moved to {target_dir.parent.name}"
            
            # Update manifest
            if task_id in self.manifest["tasks"]:
                self.manifest["tasks"][task_id]["status"] = new_status
                if phase:
                    self.manifest["tasks"][task_id]["phase"] = phase
                self._save_manifest(self.manifest)
            
            return {
                "success": True,
                "message": f"Updated task {task_id} status to {new_status}{move_msg}",
                "moved": moved,
                "location": str(target_dir.parent.name) if target_dir.parent != TASKS_ROOT else "root"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update task status: {e}"
            }
    
    def get_task_tree(self, root_id: str) -> Dict[str, Any]:
        """Get task tree visualization"""
        try:
            if not self.relationships:
                return {
                    "success": False,
                    "error": "Relationship tracking not available",
                    "message": "TaskRelationshipManager not initialized"
                }
            
            tree = self.relationships.get_tree_visualization(root_id)
            
            return {
                "success": True,
                "task_id": root_id,
                "tree": tree
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get task tree: {e}"
            }
    
    def link_tasks(self, task_a: str, task_b: str, 
                  relationship_type: str = "influence",
                  description: Optional[str] = None) -> Dict[str, Any]:
        """Create relationship between tasks"""
        try:
            if not self.relationships:
                return {
                    "success": False,
                    "error": "Relationship tracking not available",
                    "message": "TaskRelationshipManager not initialized"
                }
            
            if relationship_type == "symbiosis":
                result = self.relationships.create_symbiosis(task_a, task_b, description)
            else:
                # For now, use spawn as generic link
                result = self.relationships.create_spawn(task_a, task_b, description)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to link tasks: {e}"
            }
    
    def complete_task_with_checklist(self, task_id: str,
                                   documentation_done: bool,
                                   memory_hash: str,
                                   cleanup_done: bool,
                                   documentation_path: Optional[str] = None,
                                   tags: List[str] = None,
                                   metadata: Optional[Dict[str, Any]] = None,
                                   completion_notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete a task with mandatory checklist validation
        
        Requirements:
        - Documentation: Optional (reminder prompt)
        - Memory: Required (must provide hash)
        - Cleanup: Required (must be True)
        """
        try:
            # Validate requirements
            if not memory_hash:
                return {
                    "success": False,
                    "error": "Memory hash required",
                    "message": "Cannot complete task without creating a memory. Please create a memory and provide the hash."
                }
            
            if not cleanup_done:
                return {
                    "success": False,
                    "error": "Cleanup required",
                    "message": "Cannot complete task without cleanup. Please ensure organizational structure is tidy."
                }
            
            # Build checklist data
            checklist = {
                "documentation": {
                    "done": documentation_done,
                    "path": documentation_path if documentation_done else None
                },
                "memory": {
                    "done": True,
                    "hash": memory_hash
                },
                "cleanup": {
                    "done": cleanup_done
                },
                "tags": tags or [],
                "metadata": metadata or {}
            }
            
            # Create completion entry with checklist
            completion_content = f"Task completed with checklist validation.\n\n"
            completion_content += f"✓ Documentation: {'Yes' if documentation_done else 'No'}"
            if documentation_path:
                completion_content += f" ({documentation_path})"
            completion_content += f"\n✓ Memory: {memory_hash}\n"
            completion_content += f"✓ Cleanup: Done\n"
            if tags:
                completion_content += f"✓ Tags: {', '.join(tags)}\n"
            if completion_notes:
                completion_content += f"\n{completion_notes}"
            
            # Add completion entry
            entry_result = self.add_task_entry(
                task_id=task_id,
                entry_type="complete",
                content=completion_content,
                metadata={"checklist": checklist}
            )
            
            if not entry_result["success"]:
                return entry_result
            
            # Update status to complete (will auto-move to Complete folder)
            status_result = self.update_task_status(task_id, "complete", "complete")
            
            if status_result["success"]:
                return {
                    "success": True,
                    "message": f"Task {task_id} completed with checklist validation",
                    "checklist": checklist,
                    "moved": status_result.get("moved", False)
                }
            else:
                return status_result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to complete task: {e}"
            }