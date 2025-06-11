"""
Integration between ChromaDB memories and Obsidian notes
Handles syncing, auto-summaries, and cross-referencing
"""
import re
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from .auto_summary import AutoSummaryEngine
from .hooks import MessageFlowHooks

class MemoryNoteIntegration:
    """Integrates ChromaDB memories with Obsidian notes"""
    
    def __init__(self, vault_manager, memory_collection):
        """Initialize with vault manager and ChromaDB collection"""
        self.vault = vault_manager
        self.memory = memory_collection
        self.conversation_buffer = []
        self.last_summary_time = datetime.now()
        self.summary_engine = AutoSummaryEngine()
        self.hooks = MessageFlowHooks(self)
    
    def memory_to_note(self, memory_id: str, folder: str = "🧠 Knowledge") -> Optional[str]:
        """Convert a ChromaDB memory to an Obsidian note"""
        # Get memory from ChromaDB
        result = self.memory.get(ids=[memory_id], include=["documents", "metadatas"])
        
        if not result['documents']:
            return None
        
        content = result['documents'][0]
        metadata = result['metadatas'][0] if result['metadatas'] else {}
        
        # Create title from content or metadata
        title = metadata.get('title', '')
        if not title:
            # Extract first line or first 50 chars
            first_line = content.split('\n')[0]
            title = first_line[:50] + "..." if len(first_line) > 50 else first_line
        
        # Build note content
        note_content = f"# {title}\n\n"
        note_content += f"**Memory ID**: {memory_id}\n"
        note_content += f"**Created**: {metadata.get('created_at', 'Unknown')}\n\n"
        note_content += "## Content\n"
        note_content += content + "\n\n"
        
        # Add metadata section
        if metadata:
            note_content += "## Metadata\n"
            for key, value in metadata.items():
                if key not in ['title', 'created_at']:
                    note_content += f"- **{key}**: {value}\n"
        
        # Extract tags from metadata
        tags = []
        if 'tags' in metadata:
            tag_string = metadata['tags']
            if isinstance(tag_string, str):
                tags = [t.strip() for t in tag_string.split(',')]
        tags.append('from-memory')
        
        # Create note
        return self.vault.create_note(title, note_content, folder, tags, {"memory_id": memory_id})
    
    def note_to_memory(self, note_title: str, folder: Optional[str] = None) -> Optional[str]:
        """Convert an Obsidian note to a ChromaDB memory"""
        # Read note
        content = self.vault.read_note(note_title, folder)
        if not content:
            return None
        
        # Extract content without frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        
        # Create memory
        memory_id = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(note_title) % 10000:04d}"
        
        metadata = {
            "source": "obsidian_note",
            "note_title": note_title,
            "folder": folder or "unknown",
            "imported_at": datetime.now().isoformat(),
            "domain": "operational",
            "category": "note",
            "schema_version": "v5.0"
        }
        
        # Extract tags from content
        tag_pattern = r'#(\w+)'
        tags = re.findall(tag_pattern, content)
        if tags:
            metadata['tags'] = ','.join(tags)
        
        # Store in ChromaDB
        self.memory.add(
            documents=[content],
            ids=[memory_id],
            metadatas=[metadata]
        )
        
        return memory_id
    
    def sync_to_obsidian(self, query: str = "tag:important", n_results: int = 10):
        """Sync important memories to Obsidian"""
        # Search memories
        results = self.memory.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        synced = []
        for i, doc in enumerate(results['documents'][0]):
            memory_id = results['ids'][0][i] if 'ids' in results else f"unknown_{i}"
            metadata = results['metadatas'][0][i] if results['metadatas'] else {}
            
            # Skip if already synced
            if metadata.get('synced_to_obsidian'):
                continue
            
            # Create note
            note_path = self.memory_to_note(memory_id)
            if note_path:
                # Update memory metadata
                metadata['synced_to_obsidian'] = True
                metadata['obsidian_path'] = note_path
                # Would update in ChromaDB here
                synced.append(note_path)
        
        return synced
    
    def buffer_conversation(self, message: str, role: str = "user"):
        """Buffer conversation messages for auto-summary"""
        self.conversation_buffer.append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": message
        })
        
        # Check if we should create summary
        if self._should_summarize():
            self.create_auto_summary()
    
    def _should_summarize(self) -> bool:
        """Determine if it's time to create a summary"""
        # Time-based: every 30 minutes
        if datetime.now() - self.last_summary_time > timedelta(minutes=30):
            return True
        
        # Message count: every 30 messages
        if len(self.conversation_buffer) >= 30:
            return True
        
        # Check for completion markers
        last_messages = [msg['content'].lower() for msg in self.conversation_buffer[-5:]]
        completion_markers = ['task complete', 'done', 'finished', 'nap', 'goodbye']
        if any(marker in msg for msg in last_messages for marker in completion_markers):
            return True
        
        return False
    
    def create_auto_summary(self) -> Optional[str]:
        """Create auto-summary from conversation buffer"""
        if not self.conversation_buffer:
            return None
        
        # Use intelligent summary engine
        summary_result = self.summary_engine.generate_summary(self.conversation_buffer)
        
        # Build final summary
        summary = f"# Auto-Summary: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        summary += summary_result['summary']
        
        # Save as memory with auto_summary tag
        memory_id = f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Merge metadata from summary engine
        metadata = summary_result['metadata']
        metadata.update({
            "tags": ','.join(summary_result['tags']),
            "message_count": len(self.conversation_buffer),
            "domain": "session",
            "category": "summary",
            "schema_version": "v5.0",
            "is_essential": summary_result['metadata'].get('has_breakthroughs', False),
            "federation_visible": True
        })
        
        self.memory.add(
            documents=[summary],
            ids=[memory_id],
            metadatas=[metadata]
        )
        
        # Clear buffer and reset timer
        self.conversation_buffer = []
        self.last_summary_time = datetime.now()
        
        # Also create daily note
        self.update_daily_note(summary)
        
        return memory_id
    
    def update_daily_note(self, content: str):
        """Add content to today's daily note"""
        today = datetime.now().strftime("%Y-%m-%d")
        title = f"{today} Daily Summary"
        
        # Check if note exists
        existing = self.vault.read_note(title, "📅 Daily_Notes")
        
        if existing:
            # Append to existing
            new_content = existing + f"\n\n---\n\n## Update {datetime.now().strftime('%H:%M')}\n{content}"
            self.vault.update_note(title, new_content, "📅 Daily_Notes")
        else:
            # Create new
            self.vault.create_daily_note(content)