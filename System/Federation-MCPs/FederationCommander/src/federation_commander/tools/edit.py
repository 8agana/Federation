"""
Smart content editor tool
Replaces: edit_block with major improvements
"""

import re
import asyncio
import difflib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import aiofiles
from datetime import datetime

from .base import BaseTool

class EditTool(BaseTool):
    """Pattern-based editing with preview and batch support"""
    
    @property
    def description(self) -> str:
        return """Smart pattern-based editor for surgical file changes.
        
        Examples:
        - edit("TODO", "DONE") - Replace in current dir files
        - edit("old_api", "new_api", files="**/*.py") - All Python files
        - edit("localhost", "127.0.0.1", files="config.json", preview=True)
        - edit(r"version = \d+", "version = 2", regex=True)
        
        Features:
        - Preview changes before applying
        - Automatic backup creation
        - Batch editing across files
        - Regex support
        - Shows diffs
        """
    
    @property 
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Pattern to search for"
                },
                "replacement": {
                    "type": "string", 
                    "description": "Replacement text"
                },
                "files": {
                    "type": "string",
                    "default": "*",
                    "description": "File pattern (glob) to search"
                },
                "preview": {
                    "type": "boolean",
                    "default": None,
                    "description": "Preview changes before applying (default from config)"
                },
                "regex": {
                    "type": "boolean",
                    "default": False,
                    "description": "Use regex matching"
                },
                "case_sensitive": {
                    "type": "boolean",
                    "default": True,
                    "description": "Case sensitive matching"
                }
            },
            "required": ["pattern", "replacement"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        pattern = arguments["pattern"]
        replacement = arguments["replacement"]
        files_pattern = arguments.get("files", "*")
        preview = arguments.get("preview")
        regex = arguments.get("regex", False)
        case_sensitive = arguments.get("case_sensitive", True)
        
        # Use config default for preview if not specified
        if preview is None:
            preview = self.config.get("preview_edits", True)
        
        # Find matching files
        matching_files = await self._find_files(files_pattern)
        
        if not matching_files:
            return {
                "status": "error",
                "error": f"No files found matching pattern: {files_pattern}"
            }
        
        # Search and prepare changes
        changes = await self._find_matches(
            matching_files, pattern, replacement, regex, case_sensitive
        )
        
        if not changes:
            return {
                "status": "success",
                "message": "No matches found",
                "files_checked": len(matching_files)
            }
        
        # Preview mode
        if preview:
            return {
                "status": "preview",
                "total_matches": sum(len(c["matches"]) for c in changes),
                "files_affected": len(changes),
                "changes": changes,
                "message": "Preview mode - no changes applied. Run with preview=False to apply."
            }
        
        # Apply changes
        results = await self._apply_changes(changes)
        
        return {
            "status": "success",
            "files_modified": len(results["success"]),
            "total_replacements": results["total_replacements"],
            "backups_created": len(results["backups"]),
            "results": results
        }
    
    async def _find_files(self, pattern: str) -> List[Path]:
        """Find files matching pattern"""
        files = []
        
        # Handle different patterns
        if pattern == "*":
            # Default to common text files in current directory
            for ext in [".py", ".js", ".ts", ".json", ".md", ".txt", ".yaml", ".yml"]:
                files.extend(Path.cwd().glob(f"*{ext}"))
        elif "/" in pattern or "*" in pattern:
            # Glob pattern
            files.extend(Path.cwd().glob(pattern))
        else:
            # Single file
            path = Path(pattern)
            if path.exists() and path.is_file():
                files.append(path)
        
        # Filter out excluded patterns
        excluded = self.config.get("excluded_patterns", [])
        ignored = self.context.get_gitignore_patterns(Path.cwd())
        all_excluded = set(excluded + ignored)
        
        filtered_files = []
        for f in files:
            if f.is_file() and not any(self._matches_pattern(f, ex) for ex in all_excluded):
                filtered_files.append(f)
        
        return filtered_files
    
    def _matches_pattern(self, path: Path, pattern: str) -> bool:
        """Check if path matches exclusion pattern"""
        import fnmatch
        return fnmatch.fnmatch(str(path), pattern) or fnmatch.fnmatch(path.name, pattern)
    
    async def _find_matches(
        self, 
        files: List[Path], 
        pattern: str, 
        replacement: str,
        regex: bool,
        case_sensitive: bool
    ) -> List[Dict[str, Any]]:
        """Find all matches in files"""
        changes = []
        
        for file_path in files:
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                # Find matches
                if regex:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    matches = list(re.finditer(pattern, content, flags))
                else:
                    # Simple string matching
                    matches = []
                    search_pattern = pattern if case_sensitive else pattern.lower()
                    search_content = content if case_sensitive else content.lower()
                    
                    start = 0
                    while True:
                        pos = search_content.find(search_pattern, start)
                        if pos == -1:
                            break
                        matches.append({
                            'start': pos,
                            'end': pos + len(pattern),
                            'text': content[pos:pos + len(pattern)]
                        })
                        start = pos + 1
                
                if matches:
                    # Create preview
                    lines = content.split('\n')
                    match_previews = []
                    
                    for match in matches[:5]:  # Show first 5 matches
                        if regex:
                            start = match.start()
                            text = match.group()
                        else:
                            start = match['start']
                            text = match['text']
                        
                        # Find line number
                        line_num = content[:start].count('\n') + 1
                        line_start = content.rfind('\n', 0, start) + 1
                        line_end = content.find('\n', start)
                        if line_end == -1:
                            line_end = len(content)
                        
                        line_content = content[line_start:line_end]
                        
                        # Create preview with highlighting
                        preview_line = line_content.replace(
                            text,
                            f"<<<{text}>>> → <<<{replacement}>>>"
                        )
                        
                        match_previews.append({
                            "line": line_num,
                            "preview": preview_line.strip()
                        })
                    
                    changes.append({
                        "file": str(file_path),
                        "matches": match_previews,
                        "total_matches": len(matches),
                        "pattern": pattern,
                        "replacement": replacement
                    })
                    
            except Exception as e:
                pass  # Skip files that can't be read
        
        return changes
    
    async def _apply_changes(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply changes to files"""
        results = {
            "success": [],
            "errors": [],
            "backups": [],
            "total_replacements": 0
        }
        
        for change in changes:
            file_path = Path(change["file"])
            
            try:
                # Read current content
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                # Create backup
                backup_path = file_path.with_suffix(
                    file_path.suffix + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                async with aiofiles.open(backup_path, 'w', encoding='utf-8') as f:
                    await f.write(content)
                results["backups"].append(str(backup_path))
                
                # Apply replacements
                pattern = change["pattern"]
                replacement = change["replacement"]
                
                if change.get("regex"):
                    new_content, count = re.subn(pattern, replacement, content)
                else:
                    new_content = content.replace(pattern, replacement)
                    count = content.count(pattern)
                
                # Write new content
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(new_content)
                
                results["success"].append({
                    "file": str(file_path),
                    "replacements": count
                })
                results["total_replacements"] += count
                
            except Exception as e:
                results["errors"].append({
                    "file": str(file_path),
                    "error": str(e)
                })
        
        return results