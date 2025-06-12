#!/usr/bin/env python3
"""
Task Relationship Manager - Project Phylogeny Engine
Tracks evolutionary relationships between tasks
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

# Base paths
TASKS_ROOT = Path("/Users/samuelatagana/Documents/Federation/Tasks")
RELATIONSHIPS_FILE = TASKS_ROOT / "relationships.json"

class BranchType(Enum):
    """Types of task relationships"""
    SPAWN = "spawn"         # Direct child implementation
    FORK = "fork"          # Alternative approach
    MERGE = "merge"        # Combining insights
    SYMBIOSIS = "symbiosis" # Mutually supportive
    MUTATION = "mutation"   # Task that pivoted
    INFLUENCE = "influence" # Cross-pollination

class TaskRelationshipManager:
    """Manages the phylogenetic relationships between tasks"""
    
    def __init__(self):
        """Initialize the relationship manager"""
        self.relationships = self._load_relationships()
    
    def _load_relationships(self) -> Dict[str, Any]:
        """Load relationships from file"""
        if RELATIONSHIPS_FILE.exists():
            with open(RELATIONSHIPS_FILE, 'r') as f:
                return json.load(f)
        else:
            # Initialize with empty structure
            relationships = {
                "version": "2.0",
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "nodes": {},  # task_id -> node info
                "edges": [],  # relationship list
                "trees": {}   # root_id -> tree structure
            }
            # Don't auto-create relationships file
            # self._save_relationships(relationships)
            return relationships
    
    def _save_relationships(self, relationships: Dict[str, Any]) -> None:
        """Save relationships to file"""
        relationships["updated"] = datetime.now().isoformat()
        with open(RELATIONSHIPS_FILE, 'w') as f:
            json.dump(relationships, f, indent=2)
    
    def create_spawn(self, parent_id: str, child_id: str, 
                    reason: Optional[str] = None) -> Dict[str, Any]:
        """Create a spawn relationship (parent -> child)"""
        try:
            # Add to nodes if not exists
            if parent_id not in self.relationships["nodes"]:
                self.relationships["nodes"][parent_id] = {
                    "id": parent_id,
                    "children": [],
                    "parents": [],
                    "created": datetime.now().isoformat()
                }
            
            if child_id not in self.relationships["nodes"]:
                self.relationships["nodes"][child_id] = {
                    "id": child_id,
                    "children": [],
                    "parents": [],
                    "created": datetime.now().isoformat()
                }
            
            # Update relationships
            self.relationships["nodes"][parent_id]["children"].append(child_id)
            self.relationships["nodes"][child_id]["parents"].append(parent_id)
            
            # Add edge
            edge = {
                "from": parent_id,
                "to": child_id,
                "type": BranchType.SPAWN.value,
                "reason": reason,
                "created": datetime.now().isoformat()
            }
            self.relationships["edges"].append(edge)
            
            # Update tree structure
            self._update_tree_structure(parent_id, child_id)
            
            self._save_relationships(self.relationships)
            
            return {
                "success": True,
                "relationship": edge,
                "message": f"Created spawn relationship: {parent_id} -> {child_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create spawn relationship: {e}"
            }
    
    def create_fork(self, origin_id: str, fork_id: str, 
                   reason: str) -> Dict[str, Any]:
        """Create a fork relationship (alternative approach)"""
        try:
            # Forks share the same parent but diverge
            parent_ids = self.get_parents(origin_id)
            
            # Add fork to nodes
            if fork_id not in self.relationships["nodes"]:
                self.relationships["nodes"][fork_id] = {
                    "id": fork_id,
                    "children": [],
                    "parents": parent_ids,
                    "fork_of": origin_id,
                    "created": datetime.now().isoformat()
                }
            
            # Add edge
            edge = {
                "from": origin_id,
                "to": fork_id,
                "type": BranchType.FORK.value,
                "reason": reason,
                "created": datetime.now().isoformat()
            }
            self.relationships["edges"].append(edge)
            
            self._save_relationships(self.relationships)
            
            return {
                "success": True,
                "relationship": edge,
                "message": f"Created fork: {origin_id} -> {fork_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create fork: {e}"
            }
    
    def create_symbiosis(self, task_a: str, task_b: str,
                        description: Optional[str] = None) -> Dict[str, Any]:
        """Create symbiotic relationship between tasks"""
        try:
            # Ensure both nodes exist
            for task_id in [task_a, task_b]:
                if task_id not in self.relationships["nodes"]:
                    self.relationships["nodes"][task_id] = {
                        "id": task_id,
                        "children": [],
                        "parents": [],
                        "symbiotic_with": [],
                        "created": datetime.now().isoformat()
                    }
            
            # Add symbiotic relationship
            if "symbiotic_with" not in self.relationships["nodes"][task_a]:
                self.relationships["nodes"][task_a]["symbiotic_with"] = []
            if "symbiotic_with" not in self.relationships["nodes"][task_b]:
                self.relationships["nodes"][task_b]["symbiotic_with"] = []
                
            self.relationships["nodes"][task_a]["symbiotic_with"].append(task_b)
            self.relationships["nodes"][task_b]["symbiotic_with"].append(task_a)
            
            # Add bidirectional edges
            edge = {
                "from": task_a,
                "to": task_b,
                "type": BranchType.SYMBIOSIS.value,
                "description": description,
                "bidirectional": True,
                "created": datetime.now().isoformat()
            }
            self.relationships["edges"].append(edge)
            
            self._save_relationships(self.relationships)
            
            return {
                "success": True,
                "relationship": edge,
                "message": f"Created symbiosis: {task_a} <-> {task_b}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create symbiosis: {e}"
            }
    
    def track_mutation(self, task_id: str, mutation_type: str,
                      from_state: Dict[str, Any], to_state: Dict[str, Any],
                      reason: str) -> Dict[str, Any]:
        """Track how a task mutated/evolved"""
        try:
            if task_id not in self.relationships["nodes"]:
                self.relationships["nodes"][task_id] = {
                    "id": task_id,
                    "children": [],
                    "parents": [],
                    "mutations": [],
                    "created": datetime.now().isoformat()
                }
            
            mutation = {
                "type": mutation_type,
                "from_state": from_state,
                "to_state": to_state,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
            
            if "mutations" not in self.relationships["nodes"][task_id]:
                self.relationships["nodes"][task_id]["mutations"] = []
                
            self.relationships["nodes"][task_id]["mutations"].append(mutation)
            
            self._save_relationships(self.relationships)
            
            return {
                "success": True,
                "mutation": mutation,
                "message": f"Tracked mutation for task {task_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to track mutation: {e}"
            }
    
    def get_parents(self, task_id: str) -> List[str]:
        """Get parent tasks"""
        if task_id in self.relationships["nodes"]:
            return self.relationships["nodes"][task_id].get("parents", [])
        return []
    
    def get_children(self, task_id: str) -> List[str]:
        """Get child tasks"""
        if task_id in self.relationships["nodes"]:
            return self.relationships["nodes"][task_id].get("children", [])
        return []
    
    def get_ancestry(self, task_id: str) -> List[str]:
        """Get full ancestry chain"""
        ancestry = []
        current = task_id
        visited = set()
        
        while current:
            if current in visited:
                break  # Prevent cycles
            visited.add(current)
            
            parents = self.get_parents(current)
            if parents:
                ancestry.extend(parents)
                current = parents[0]  # Follow first parent
            else:
                break
                
        return ancestry
    
    def get_descendants(self, task_id: str) -> List[str]:
        """Get all descendants recursively"""
        descendants = []
        to_visit = [task_id]
        visited = set()
        
        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            children = self.get_children(current)
            descendants.extend(children)
            to_visit.extend(children)
            
        return descendants
    
    def get_tree_visualization(self, root_id: str, 
                             indent: str = "", is_last: bool = True) -> str:
        """Generate ASCII tree visualization"""
        lines = []
        
        # Get task info
        if root_id in self.relationships["nodes"]:
            node = self.relationships["nodes"][root_id]
            prefix = "└── " if is_last else "├── "
            lines.append(f"{indent}{prefix}{root_id}")
            
            # Add children
            children = self.get_children(root_id)
            for i, child in enumerate(children):
                extension = "    " if is_last else "│   "
                is_last_child = i == len(children) - 1
                child_lines = self.get_tree_visualization(
                    child, 
                    indent + extension, 
                    is_last_child
                )
                lines.append(child_lines)
        else:
            lines.append(f"{indent}└── {root_id}")
            
        return "\n".join(lines)
    
    def _update_tree_structure(self, parent_id: str, child_id: str) -> None:
        """Update tree structure cache"""
        # Find root of parent
        root = parent_id
        ancestors = self.get_ancestry(parent_id)
        if ancestors:
            root = ancestors[-1]
            
        # Update tree
        if root not in self.relationships["trees"]:
            self.relationships["trees"][root] = {
                "root": root,
                "nodes": [root],
                "updated": datetime.now().isoformat()
            }
            
        if child_id not in self.relationships["trees"][root]["nodes"]:
            self.relationships["trees"][root]["nodes"].append(child_id)
            self.relationships["trees"][root]["updated"] = datetime.now().isoformat()