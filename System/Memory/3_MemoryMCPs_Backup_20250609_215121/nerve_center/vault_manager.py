"""
Obsidian Vault Manager for Nerve Center
Handles all file operations for the Obsidian vault
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

class ObsidianVaultManager:
    """Manages Obsidian vault operations"""
    
    def __init__(self):
        # CC's Nerve Center vault path
        self.vault_path = Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center")
        
        # Ensure vault exists
        if not self.vault_path.exists():
            raise ValueError(f"Nerve Center vault not found at {self.vault_path}")
    
    def create_note(self, title: str, content: str, folder: str = "🧠 Knowledge", 
                    tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Create a new note in the vault"""
        # Create folder if it doesn't exist
        folder_path = self.vault_path / folder
        folder_path.mkdir(exist_ok=True)
        
        # Sanitize title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
        filename = f"{safe_title}.md"
        filepath = folder_path / filename
        
        # Build note content with frontmatter
        frontmatter = {
            "created": datetime.now().isoformat(),
            "tags": tags or []
        }
        if metadata:
            frontmatter.update(metadata)
        
        note_content = f"---\n"
        for key, value in frontmatter.items():
            if isinstance(value, list):
                note_content += f"{key}:\n"
                for item in value:
                    note_content += f"  - {item}\n"
            else:
                note_content += f"{key}: {value}\n"
        note_content += f"---\n\n# {title}\n\n{content}"
        
        # Write the note
        filepath.write_text(note_content, encoding='utf-8')
        
        return str(filepath.relative_to(self.vault_path))
    
    def read_note(self, title: str, folder: Optional[str] = None) -> Optional[str]:
        """Read a note from the vault"""
        # Search for the note
        if folder:
            search_paths = [(self.vault_path / folder)]
        else:
            # Search common folders
            search_paths = [
                self.vault_path / "🧠 Knowledge",
                self.vault_path / "💭 Private_Thoughts",
                self.vault_path / "📚 Learning",
                self.vault_path / "🔬 Experiments"
            ]
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            # Try exact match first
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
            filepath = search_path / f"{safe_title}.md"
            
            if filepath.exists():
                return filepath.read_text(encoding='utf-8')
            
            # Try case-insensitive search
            for file in search_path.glob("*.md"):
                if file.stem.lower() == safe_title.lower():
                    return file.read_text(encoding='utf-8')
        
        return None
    
    def update_note(self, title: str, content: str, folder: Optional[str] = None) -> bool:
        """Update an existing note"""
        # Find the note first
        existing_content = self.read_note(title, folder)
        if not existing_content:
            return False
        
        # Extract frontmatter if present
        if existing_content.startswith("---"):
            parts = existing_content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                updated_content = f"---{frontmatter}---\n\n# {title}\n\n{content}"
            else:
                updated_content = f"# {title}\n\n{content}"
        else:
            updated_content = f"# {title}\n\n{content}"
        
        # Find and update the file
        if folder:
            search_paths = [(self.vault_path / folder)]
        else:
            search_paths = [
                self.vault_path / "🧠 Knowledge",
                self.vault_path / "💭 Private_Thoughts",
                self.vault_path / "📚 Learning",
                self.vault_path / "🔬 Experiments"
            ]
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
            filepath = search_path / f"{safe_title}.md"
            
            if filepath.exists():
                filepath.write_text(updated_content, encoding='utf-8')
                return True
            
            # Try case-insensitive
            for file in search_path.glob("*.md"):
                if file.stem.lower() == safe_title.lower():
                    file.write_text(updated_content, encoding='utf-8')
                    return True
        
        return False
    
    def search_notes(self, query: str, folder: Optional[str] = None) -> List[Dict[str, str]]:
        """Search for notes containing the query"""
        results = []
        
        if folder:
            search_paths = [(self.vault_path / folder)]
        else:
            # Search all folders
            search_paths = [p for p in self.vault_path.iterdir() if p.is_dir() and not p.name.startswith('.')]
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            for file in search_path.rglob("*.md"):
                try:
                    content = file.read_text(encoding='utf-8')
                    if query.lower() in content.lower() or query.lower() in file.stem.lower():
                        # Extract preview
                        lines = content.split('\n')
                        preview_lines = []
                        for line in lines:
                            if query.lower() in line.lower():
                                preview_lines.append(line.strip())
                                if len(preview_lines) >= 2:
                                    break
                        
                        preview = " ... ".join(preview_lines) if preview_lines else lines[0][:100] + "..."
                        
                        results.append({
                            'title': file.stem,
                            'folder': file.parent.name,
                            'preview': preview,
                            'path': str(file.relative_to(self.vault_path))
                        })
                except Exception:
                    continue
        
        return results[:20]  # Limit results
    
    def create_daily_note(self, summary: str, events: List[Dict[str, str]] = None) -> str:
        """Create or update today's daily note"""
        today = datetime.now()
        date_str = today.strftime("%Y-%m-%d")
        title = f"{date_str}_Personal"
        
        # Build content
        content = f"## Summary\n{summary}\n\n"
        
        if events:
            content += "## Events\n"
            for event in events:
                time = event.get('time', '')
                desc = event.get('description', '')
                details = event.get('details', '')
                
                content += f"- **{time}**: {desc}\n"
                if details:
                    content += f"  - {details}\n"
        
        # Check if daily note already exists
        existing = self.read_note(title, "📅 Daily_Notes")
        
        if existing:
            # Append to existing
            return self.update_note(title, existing + "\n\n" + content, "📅 Daily_Notes")
        else:
            # Create new
            return self.create_note(
                title=title,
                content=content,
                folder="📅 Daily_Notes",
                tags=["daily-note", "personal"]
            )