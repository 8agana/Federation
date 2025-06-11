"""
Obsidian Vault Manager for Nerve Center
Handles note creation, reading, updating, and organization
"""
import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class ObsidianVaultManager:
    """Manages Obsidian vault operations for the Nerve Center"""
    
    def __init__(self, vault_path: str = None):
        """Initialize vault manager with path to Nerve Center"""
        if vault_path is None:
            vault_path = "/Users/samuelatagana/Documents/Federation/Documents/CC_DOCS/Nerve_Center"
        
        self.vault_path = Path(vault_path)
        self.ensure_structure()
    
    def ensure_structure(self):
        """Ensure all required folders exist"""
        folders = [
            "📅 Daily_Notes",
            "🧠 Knowledge", 
            "🎯 Projects",
            "💡 Ideas",
            "🔧 Code_Patterns",
            "📊 Decisions",
            "🤝 Conversations",
            "📥 Sam_Inbox",
            "🔄 Active_Tracking"
        ]
        
        for folder in folders:
            folder_path = self.vault_path / folder
            folder_path.mkdir(exist_ok=True)
    
    def create_note(self, title: str, content: str, folder: str = "🧠 Knowledge", 
                   tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Create a new note in specified folder"""
        # Clean title for filename
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
        
        # Determine folder path
        folder_path = self.vault_path / folder
        folder_path.mkdir(exist_ok=True)
        
        # Create note path
        note_path = folder_path / f"{safe_title}.md"
        
        # Add frontmatter
        frontmatter = {
            "created": datetime.now().isoformat(),
            "tags": tags or [],
            "type": folder.strip("📅🧠🎯💡🔧📊🤝📥🔄 ").lower()
        }
        
        if metadata:
            frontmatter.update(metadata)
        
        # Build note content
        full_content = "---\n"
        for key, value in frontmatter.items():
            if isinstance(value, list):
                full_content += f"{key}:\n"
                for item in value:
                    full_content += f"  - {item}\n"
            else:
                full_content += f"{key}: {value}\n"
        full_content += "---\n\n"
        full_content += content
        
        # Write note
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return str(note_path)
    
    def read_note(self, title: str, folder: Optional[str] = None) -> Optional[str]:
        """Read a note by title, optionally from specific folder"""
        # Search in specific folder or all folders
        search_folders = [folder] if folder else [
            f.name for f in self.vault_path.iterdir() if f.is_dir()
        ]
        
        for search_folder in search_folders:
            folder_path = self.vault_path / search_folder
            if not folder_path.exists():
                continue
                
            # Try exact match first
            note_path = folder_path / f"{title}.md"
            if note_path.exists():
                with open(note_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Try fuzzy match
            for file in folder_path.glob("*.md"):
                if title.lower() in file.stem.lower():
                    with open(file, 'r', encoding='utf-8') as f:
                        return f.read()
        
        return None
    
    def update_note(self, title: str, content: str, folder: Optional[str] = None) -> bool:
        """Update existing note content"""
        # Find the note
        note_content = self.read_note(title, folder)
        if not note_content:
            return False
        
        # Extract frontmatter
        if note_content.startswith("---"):
            parts = note_content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                new_content = f"---{frontmatter}---\n\n{content}"
            else:
                new_content = content
        else:
            new_content = content
        
        # Find and update the file
        search_folders = [folder] if folder else [
            f.name for f in self.vault_path.iterdir() if f.is_dir()
        ]
        
        for search_folder in search_folders:
            folder_path = self.vault_path / search_folder
            note_path = folder_path / f"{title}.md"
            if note_path.exists():
                with open(note_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
        
        return False
    
    def create_daily_note(self, summary: str, events: List[Dict[str, str]] = None) -> str:
        """Create or update today's daily note"""
        today = datetime.now().strftime("%Y-%m-%d")
        title = f"{today} Daily Summary"
        
        # Build content
        content = f"# {title}\n\n"
        content += f"## Summary\n{summary}\n\n"
        
        if events:
            content += "## Key Events\n"
            for event in events:
                content += f"- **{event.get('time', 'Unknown')}**: {event.get('description', '')}\n"
                if 'details' in event:
                    content += f"  - {event['details']}\n"
            content += "\n"
        
        content += "## Reflections\n_Auto-generated from today's work_\n"
        
        return self.create_note(title, content, "📅 Daily_Notes", ["daily", "auto-generated"])
    
    def search_notes(self, query: str, folder: Optional[str] = None) -> List[Dict[str, str]]:
        """Search notes by content or title"""
        results = []
        
        search_folders = [folder] if folder else [
            f.name for f in self.vault_path.iterdir() if f.is_dir()
        ]
        
        for search_folder in search_folders:
            folder_path = self.vault_path / search_folder
            if not folder_path.exists():
                continue
            
            for file in folder_path.glob("*.md"):
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if query.lower() in file.stem.lower() or query.lower() in content.lower():
                    results.append({
                        "title": file.stem,
                        "path": str(file),
                        "folder": search_folder,
                        "preview": content[:200] + "..." if len(content) > 200 else content
                    })
        
        return results
    
    def create_link(self, target_title: str, display_text: Optional[str] = None) -> str:
        """Create wiki-style link to another note"""
        if display_text:
            return f"[[{target_title}|{display_text}]]"
        return f"[[{target_title}]]"
    
    def extract_links(self, content: str) -> List[str]:
        """Extract all wiki-style links from content"""
        pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
        matches = re.findall(pattern, content)
        return matches