"""
SharedVault Manager for TaskTracker MCP
Handles Obsidian operations for the SharedVault
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

class SharedVaultManager:
    """Manages SharedVault Obsidian operations"""
    
    def __init__(self):
        # SharedVault path
        self.vault_path = Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault")
        
        # Ensure vault exists
        if not self.vault_path.exists():
            raise ValueError(f"SharedVault not found at {self.vault_path}")
    
    def create_note(self, title: str, content: str, folder: str = "📋 TaskTracker", 
                    tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Create a new note in the SharedVault"""
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
            # Search all folders - use rglob for recursive search
            try:
                # Get all directories in vault, handle Unicode properly
                for folder_path in self.vault_path.iterdir():
                    if folder_path.is_dir() and not folder_path.name.startswith('.'):
                        search_folders.append(folder_path)
            except Exception as e:
                print(f"Error listing vault directories: {e}")
                return results
        
        for folder_path in search_folders:
            try:
                # Use rglob for recursive search to find all .md files
                for file_path in folder_path.rglob('*.md'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Check if query matches in content or filename
                        if query_lower in content.lower() or query_lower in file_path.stem.lower():
                            # Extract preview text
                            lines = content.split('\n')
                            preview_lines = []
                            
                            # Skip frontmatter and headers for preview
                            in_frontmatter = False
                            for line in lines:
                                line_stripped = line.strip()
                                
                                # Handle frontmatter
                                if line_stripped == '---':
                                    in_frontmatter = not in_frontmatter
                                    continue
                                if in_frontmatter:
                                    continue
                                
                                # Skip headers and empty lines for preview
                                if line_stripped and not line_stripped.startswith('#'):
                                    preview_lines.append(line_stripped)
                                    if len(' '.join(preview_lines)) > 100:
                                        break
                            
                            preview = ' '.join(preview_lines)[:150]
                            if len(preview) == 150:
                                preview += '...'
                            
                            # Get relative folder path
                            relative_folder = str(file_path.parent.relative_to(self.vault_path))
                            
                            results.append({
                                'title': file_path.stem,
                                'folder': relative_folder,
                                'preview': preview,
                                'path': str(file_path.relative_to(self.vault_path))
                            })
                            
                    except UnicodeDecodeError:
                        # Skip binary files
                        continue
                    except Exception as e:
                        # Skip files that can't be read
                        print(f"Error reading file {file_path}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error searching folder {folder_path}: {e}")
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
        
        # Delete source file
        source_file.unlink()
        
        return True
    
    def update_checkbox(self, title: str, checkbox_text: str, checked: bool, folder: Optional[str] = None) -> bool:
        """Toggle a checkbox in a note"""
        # Find the note
        content = self.read_note(title, folder)
        if not content:
            return False
        
        # Find and update the checkbox
        lines = content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if checkbox_text.lower() in line.lower() and ('- [ ]' in line or '- [x]' in line):
                if checked:
                    lines[i] = line.replace('- [ ]', '- [x]')
                else:
                    lines[i] = line.replace('- [x]', '- [ ]')
                updated = True
                break
        
        if updated:
            updated_content = '\n'.join(lines)
            return self.update_note(title, updated_content.split('\n\n', 1)[1] if '\n\n' in updated_content else updated_content, folder)
        
        return False