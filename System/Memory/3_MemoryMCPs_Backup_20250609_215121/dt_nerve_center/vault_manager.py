"""
Obsidian Vault Manager for DT Nerve Center
Handles all file operations for DT's Obsidian vault
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

class ObsidianVaultManager:
    """Manages Obsidian vault operations for DT"""
    
    def __init__(self, vault_path: Optional[str] = None):
        # DT's Nerve Center vault path
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center")
        
        # Ensure vault exists
        if not self.vault_path.exists():
            raise ValueError(f"DT Nerve Center vault not found at {self.vault_path}")
    
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
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(note_content)
        
        return f"{folder}/{filename}"
    
    def read_note(self, title: str, folder: Optional[str] = None) -> Optional[str]:
        """Read a note's content"""
        if folder:
            # Search in specific folder
            folder_path = self.vault_path / folder
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
            filepath = folder_path / f"{safe_title}.md"
            
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
        else:
            # Search across all folders
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
            for folder_path in self.vault_path.iterdir():
                if folder_path.is_dir() and not folder_path.name.startswith('.'):
                    filepath = folder_path / f"{safe_title}.md"
                    if filepath.exists():
                        with open(filepath, 'r', encoding='utf-8') as f:
                            return f.read()
        
        return None
    
    def update_note(self, title: str, content: str, folder: Optional[str] = None) -> bool:
        """Update an existing note"""
        # Find the note
        if folder:
            folder_path = self.vault_path / folder
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
            filepath = folder_path / f"{safe_title}.md"
        else:
            # Search for the note
            safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
            filepath = None
            for folder_path in self.vault_path.iterdir():
                if folder_path.is_dir() and not folder_path.name.startswith('.'):
                    potential_path = folder_path / f"{safe_title}.md"
                    if potential_path.exists():
                        filepath = potential_path
                        break
        
        if filepath and filepath.exists():
            # Read existing content to preserve frontmatter
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Extract frontmatter
            if existing_content.startswith('---'):
                parts = existing_content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    # Update with new content
                    updated_content = f"---{frontmatter}---\n\n# {title}\n\n{content}"
                else:
                    updated_content = f"# {title}\n\n{content}"
            else:
                updated_content = f"# {title}\n\n{content}"
            
            # Write updated content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            return True
        
        return False
    
    def search_notes(self, query: str, folder: Optional[str] = None) -> List[Dict[str, str]]:
        """Search for notes containing the query"""
        results = []
        query_lower = query.lower()
        
        search_folders = []
        if folder:
            folder_path = self.vault_path / folder
            if folder_path.exists():
                search_folders.append(folder_path)
        else:
            # Search all folders
            for folder_path in self.vault_path.iterdir():
                if folder_path.is_dir() and not folder_path.name.startswith('.'):
                    search_folders.append(folder_path)
        
        for folder_path in search_folders:
            for file_path in folder_path.glob('*.md'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if query_lower in content.lower() or query_lower in file_path.stem.lower():
                            # Extract preview
                            lines = content.split('\n')
                            preview_lines = []
                            for line in lines:
                                if line.strip() and not line.startswith('#') and not line.startswith('---'):
                                    preview_lines.append(line.strip())
                                    if len(' '.join(preview_lines)) > 100:
                                        break
                            
                            preview = ' '.join(preview_lines)[:150]
                            if len(preview) == 150:
                                preview += '...'
                            
                            results.append({
                                'title': file_path.stem,
                                'folder': folder_path.name,
                                'preview': preview,
                                'path': str(file_path.relative_to(self.vault_path))
                            })
                except Exception as e:
                    # Skip files that can't be read
                    continue
        
        return results
    
    def move_note(self, title: str, from_folder: str, to_folder: str) -> bool:
        """Move a note from one folder to another"""
        # Source path
        from_path = self.vault_path / from_folder
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
        source_file = from_path / f"{safe_title}.md"
        
        if not source_file.exists():
            return False
        
        # Destination path
        to_path = self.vault_path / to_folder
        to_path.mkdir(exist_ok=True)
        dest_file = to_path / f"{safe_title}.md"
        
        # Read content
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Write to new location
        with open(dest_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Note: Not deleting source to avoid data loss
        # User can manually delete after verifying
        
        return True
    
    def create_daily_note(self, summary: str, events: List[Dict[str, str]] = None) -> bool:
        """Create or update today's daily note"""
        today = datetime.now()
        title = today.strftime("%Y-%m-%d")
        
        content = f"## Summary\n{summary}\n\n"
        
        if events:
            content += "## Events\n"
            for event in events:
                content += f"### {event.get('time', 'Unknown time')}\n"
                content += f"**{event.get('description', 'No description')}**\n"
                if event.get('details'):
                    content += f"{event['details']}\n"
                content += "\n"
        
        # Add to daily notes folder
        folder_path = self.vault_path / "📅 Daily_Notes"
        folder_path.mkdir(exist_ok=True)
        
        # Check if note already exists
        filepath = folder_path / f"{title}.md"
        if filepath.exists():
            # Append to existing
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(f"\n\n---\n\n## Update: {datetime.now().strftime('%H:%M')}\n\n{content}")
        else:
            # Create new
            self.create_note(
                title=title,
                content=content,
                folder="📅 Daily_Notes",
                tags=["daily-note"]
            )
        
        return True