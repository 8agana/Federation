"""
Direct memory access tool
NEW - Direct integration with Federation memory systems
"""

import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from .base import BaseTool

class MemoryTool(BaseTool):
    """Direct access to Federation memory systems"""
    
    @property
    def description(self) -> str:
        return """Direct memory system access for quick storage and retrieval.
        
        Examples:
        - memory("Remember that the API key is in .env")
        - memory("What did we decide about the database schema?")
        - memory("tag:important", search=True)
        - memory("update:mem-123", content="New information")
        
        Features:
        - Natural language storage and retrieval
        - Tag-based organization
        - Memory updates
        - Cross-system search
        - Automatic context detection
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Memory content or search query"
                },
                "action": {
                    "type": "string",
                    "enum": ["auto", "store", "search", "update", "stats"],
                    "default": "auto",
                    "description": "Action to perform (auto-detected by default)"
                },
                "tags": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "string"}}
                    ],
                    "description": "Tags for the memory"
                },
                "title": {
                    "type": "string",
                    "description": "Optional title for the memory"
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata"
                },
                "memory_id": {
                    "type": "string",
                    "description": "Memory ID for updates"
                },
                "n_results": {
                    "type": "integer",
                    "default": 5,
                    "description": "Number of search results"
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        query = arguments["query"]
        action = arguments.get("action", "auto")
        
        # Auto-detect action
        if action == "auto":
            if query.lower().startswith(("remember", "store", "save")):
                action = "store"
                # Extract actual content
                for prefix in ["remember that", "remember", "store", "save"]:
                    if query.lower().startswith(prefix):
                        query = query[len(prefix):].strip()
                        break
            elif query.lower().startswith(("update:", "update ")):
                action = "update"
            elif query.lower() in ["stats", "statistics", "info"]:
                action = "stats"
            else:
                action = "search"
        
        # Execute action
        if action == "store":
            return await self._store_memory(query, arguments)
        elif action == "search":
            return await self._search_memory(query, arguments)
        elif action == "update":
            return await self._update_memory(query, arguments)
        elif action == "stats":
            return await self._get_stats()
        else:
            return {"status": "error", "error": f"Unknown action: {action}"}
    
    async def _store_memory(self, content: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Store a new memory"""
        # Extract or generate metadata
        tags = arguments.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        
        title = arguments.get("title")
        metadata = arguments.get("metadata", {})
        
        # Add context metadata
        metadata["source"] = "federation_commander"
        metadata["timestamp"] = datetime.now().isoformat()
        
        # Add git context if available
        git_info = self.context.get_git_info()
        if git_info:
            metadata["git_context"] = git_info
        
        # Detect memory type
        memory_type = self._detect_memory_type(content, tags)
        metadata["type"] = memory_type
        
        # Check if this is MCP-based storage
        try:
            # Try using MCP memory tool if available
            from mcp import ClientSession
            # This would integrate with actual MCP client
            # For now, we'll use direct storage
        except:
            pass
        
        # Direct storage fallback
        memory_data = {
            "id": f"mem-{int(datetime.now().timestamp())}",
            "content": content,
            "title": title or content[:50] + "..." if len(content) > 50 else content,
            "tags": tags,
            "metadata": metadata,
            "created": datetime.now().isoformat()
        }
        
        # Store to local cache for quick access
        cache_path = Path.home() / ".federation" / "memory_cache.json"
        cache_path.parent.mkdir(exist_ok=True)
        
        # Load existing cache
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                cache = json.load(f)
        else:
            cache = {"memories": []}
        
        # Add new memory
        cache["memories"].append(memory_data)
        
        # Keep only recent memories in cache
        cache["memories"] = cache["memories"][-100:]
        
        # Save cache
        with open(cache_path, 'w') as f:
            json.dump(cache, f, indent=2)
        
        return {
            "status": "success",
            "message": "Memory stored successfully",
            "memory": memory_data
        }
    
    async def _search_memory(self, query: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search memories"""
        n_results = arguments.get("n_results", 5)
        
        # Check for tag search
        if query.startswith("tag:"):
            tag = query[4:].strip()
            return await self._search_by_tag(tag, n_results)
        
        # Check for time-based search
        time_keywords = ["today", "yesterday", "this week", "last week", "recent"]
        for keyword in time_keywords:
            if keyword in query.lower():
                return await self._search_by_time(keyword, query, n_results)
        
        # Regular search
        results = []
        
        # Search local cache first
        cache_path = Path.home() / ".federation" / "memory_cache.json"
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                cache = json.load(f)
            
            # Simple text search
            query_lower = query.lower()
            for memory in cache.get("memories", []):
                score = 0
                
                # Check content
                if query_lower in memory["content"].lower():
                    score += 10
                
                # Check title
                if memory.get("title") and query_lower in memory["title"].lower():
                    score += 5
                
                # Check tags
                for tag in memory.get("tags", []):
                    if query_lower in tag.lower():
                        score += 3
                
                if score > 0:
                    results.append({
                        "memory": memory,
                        "score": score
                    })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Format results
        formatted_results = []
        for r in results[:n_results]:
            memory = r["memory"]
            formatted_results.append({
                "id": memory["id"],
                "content": memory["content"],
                "title": memory.get("title"),
                "tags": memory.get("tags", []),
                "created": memory.get("created"),
                "score": r["score"]
            })
        
        return {
            "status": "success",
            "query": query,
            "count": len(formatted_results),
            "results": formatted_results
        }
    
    async def _update_memory(self, query: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing memory"""
        # Extract memory ID
        memory_id = arguments.get("memory_id")
        if not memory_id and query.startswith("update:"):
            memory_id = query[7:].strip()
        
        if not memory_id:
            return {"status": "error", "error": "Memory ID required for update"}
        
        content = arguments.get("content", query)
        
        # Load cache
        cache_path = Path.home() / ".federation" / "memory_cache.json"
        if not cache_path.exists():
            return {"status": "error", "error": "No memory cache found"}
        
        with open(cache_path, 'r') as f:
            cache = json.load(f)
        
        # Find and update memory
        updated = False
        for memory in cache.get("memories", []):
            if memory["id"] == memory_id:
                # Update content
                memory["content"] = content
                memory["updated"] = datetime.now().isoformat()
                
                # Update metadata
                if "metadata" not in memory:
                    memory["metadata"] = {}
                memory["metadata"]["last_updated"] = datetime.now().isoformat()
                
                updated = True
                break
        
        if not updated:
            return {"status": "error", "error": f"Memory not found: {memory_id}"}
        
        # Save cache
        with open(cache_path, 'w') as f:
            json.dump(cache, f, indent=2)
        
        return {
            "status": "success",
            "message": f"Memory {memory_id} updated successfully"
        }
    
    async def _get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        stats = {
            "total_memories": 0,
            "cache_memories": 0,
            "tags": {},
            "memory_types": {},
            "recent_memories": []
        }
        
        # Check local cache
        cache_path = Path.home() / ".federation" / "memory_cache.json"
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                cache = json.load(f)
            
            memories = cache.get("memories", [])
            stats["cache_memories"] = len(memories)
            
            # Analyze memories
            for memory in memories:
                # Count tags
                for tag in memory.get("tags", []):
                    stats["tags"][tag] = stats["tags"].get(tag, 0) + 1
                
                # Count types
                mem_type = memory.get("metadata", {}).get("type", "general")
                stats["memory_types"][mem_type] = stats["memory_types"].get(mem_type, 0) + 1
            
            # Get recent memories
            stats["recent_memories"] = [
                {
                    "id": m["id"],
                    "title": m.get("title", m["content"][:50] + "..."),
                    "created": m.get("created")
                }
                for m in memories[-5:]
            ]
        
        return {
            "status": "success",
            "stats": stats
        }
    
    async def _search_by_tag(self, tag: str, n_results: int) -> Dict[str, Any]:
        """Search memories by tag"""
        results = []
        
        cache_path = Path.home() / ".federation" / "memory_cache.json"
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                cache = json.load(f)
            
            for memory in cache.get("memories", []):
                if tag in memory.get("tags", []):
                    results.append(memory)
        
        # Sort by creation date
        results.sort(key=lambda x: x.get("created", ""), reverse=True)
        
        return {
            "status": "success",
            "tag": tag,
            "count": len(results),
            "results": results[:n_results]
        }
    
    async def _search_by_time(self, time_keyword: str, query: str, n_results: int) -> Dict[str, Any]:
        """Search memories by time range"""
        # This is simplified - would need proper time parsing
        from datetime import timedelta
        
        now = datetime.now()
        
        # Determine time range
        if time_keyword == "today":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_keyword == "yesterday":
            start_time = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_keyword == "this week":
            start_time = now - timedelta(days=now.weekday())
        elif time_keyword == "last week":
            start_time = now - timedelta(days=now.weekday() + 7)
            end_time = now - timedelta(days=now.weekday())
        else:  # recent
            start_time = now - timedelta(days=7)
        
        # Default end time
        if 'end_time' not in locals():
            end_time = now
        
        # Search within time range
        results = []
        
        cache_path = Path.home() / ".federation" / "memory_cache.json"
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                cache = json.load(f)
            
            for memory in cache.get("memories", []):
                try:
                    created = datetime.fromisoformat(memory.get("created", ""))
                    if start_time <= created <= end_time:
                        # Also check if query matches
                        if not query or time_keyword == query.lower() or query.lower() in memory["content"].lower():
                            results.append(memory)
                except:
                    continue
        
        return {
            "status": "success",
            "time_range": f"{time_keyword} ({start_time.date()} to {end_time.date()})",
            "count": len(results),
            "results": results[:n_results]
        }
    
    def _detect_memory_type(self, content: str, tags: List[str]) -> str:
        """Detect the type of memory"""
        content_lower = content.lower()
        
        # Check tags first
        if "task" in tags or "todo" in tags:
            return "task"
        elif "decision" in tags:
            return "decision"
        elif "reference" in tags:
            return "reference"
        
        # Check content patterns
        if any(word in content_lower for word in ["decided", "decision", "agreed", "conclusion"]):
            return "decision"
        elif any(word in content_lower for word in ["todo", "task", "need to", "should", "must"]):
            return "task"
        elif any(word in content_lower for word in ["api", "key", "password", "token", "config"]):
            return "credential"
        elif any(word in content_lower for word in ["how to", "guide", "process", "steps"]):
            return "procedure"
        
        return "general"