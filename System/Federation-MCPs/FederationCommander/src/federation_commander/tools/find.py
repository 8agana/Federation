"""
Intelligent search tool
Replaces: search_files, search_code, list_directory, get_file_info
"""

import asyncio
import re
import os
import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import subprocess

from .base import BaseTool

class FindTool(BaseTool):
    """Intelligent file and content search with Federation awareness"""
    
    @property
    def description(self) -> str:
        return """Smart search for files, code, and content across the Federation.
        
        Examples:
        - find("ChromaDB") - Search everything for ChromaDB mentions
        - find("*.py", type="files") - Find all Python files
        - find("TODO", in="*.js") - Find TODO in JavaScript files
        - find("class.*Handler", regex=True) - Regex search
        - find(path="/Users/sam/Documents") - List directory contents
        
        Features:
        - Content and filename search
        - Regex support
        - Federation-aware (knows key paths)
        - Git-aware (respects .gitignore)
        - Fast with ripgrep fallback
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (text, pattern, or directory path)"
                },
                "type": {
                    "type": "string",
                    "enum": ["auto", "content", "files", "info"],
                    "default": "auto",
                    "description": "Search type (auto-detected by default)"
                },
                "in": {
                    "type": "string",
                    "description": "File pattern to search within (e.g., '*.py')"
                },
                "path": {
                    "type": "string",
                    "description": "Starting path (default: current directory)"
                },
                "regex": {
                    "type": "boolean",
                    "default": False,
                    "description": "Use regex matching"
                },
                "case_sensitive": {
                    "type": "boolean",
                    "default": True,
                    "description": "Case sensitive search"
                },
                "max_results": {
                    "type": "integer",
                    "default": 50,
                    "description": "Maximum results to return"
                },
                "context_lines": {
                    "type": "integer",
                    "default": 2,
                    "description": "Context lines for content search"
                },
                "include_hidden": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include hidden files"
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        query = arguments["query"]
        search_type = arguments.get("type", "auto")
        file_pattern = arguments.get("in")
        start_path = arguments.get("path", ".")
        regex = arguments.get("regex", False)
        case_sensitive = arguments.get("case_sensitive", True)
        max_results = arguments.get("max_results", 50)
        context_lines = arguments.get("context_lines", 2)
        include_hidden = arguments.get("include_hidden", False)
        
        # Resolve path
        path = Path(start_path).expanduser().resolve()
        
        # Auto-detect search type
        if search_type == "auto":
            if path.exists() and path.is_dir() and query == str(path):
                search_type = "info"
            elif self._looks_like_file_pattern(query):
                search_type = "files"
            else:
                search_type = "content"
        
        # Execute appropriate search
        if search_type == "info":
            return await self._get_directory_info(path)
        elif search_type == "files":
            return await self._search_files(query, path, max_results, include_hidden)
        elif search_type == "content":
            return await self._search_content(
                query, path, file_pattern, regex, case_sensitive, 
                max_results, context_lines, include_hidden
            )
        else:
            return {"status": "error", "error": f"Unknown search type: {search_type}"}
    
    def _looks_like_file_pattern(self, query: str) -> bool:
        """Check if query looks like a file pattern"""
        return any(char in query for char in ['*', '?', '[', ']']) or query.startswith('.')
    
    async def _get_directory_info(self, path: Path) -> Dict[str, Any]:
        """Get detailed directory listing and info"""
        if not path.exists():
            return {"status": "error", "error": f"Path not found: {path}"}
        
        if path.is_file():
            # Single file info
            return await self._get_file_info(path)
        
        # Directory listing
        items = []
        total_size = 0
        file_count = 0
        dir_count = 0
        
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith('.') and not self.config.get("show_hidden", False):
                    continue
                
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(item)
                }
                
                if item.is_file():
                    stat = item.stat()
                    item_info.update({
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                    total_size += stat.st_size
                    file_count += 1
                else:
                    dir_count += 1
                
                items.append(item_info)
            
            # Add git info if in repo
            git_info = self.context.get_git_info(path)
            
            result = {
                "status": "success",
                "path": str(path),
                "type": "directory",
                "contents": items,
                "summary": {
                    "files": file_count,
                    "directories": dir_count,
                    "total_size": total_size
                }
            }
            
            if git_info:
                result["git"] = git_info
            
            return result
            
        except PermissionError:
            return {"status": "error", "error": f"Permission denied: {path}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _get_file_info(self, path: Path) -> Dict[str, Any]:
        """Get detailed file information"""
        try:
            stat = path.stat()
            
            info = {
                "status": "success",
                "path": str(path),
                "type": "file",
                "name": path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:]
            }
            
            # Add line count for text files
            if path.suffix in ['.py', '.js', '.ts', '.json', '.md', '.txt', '.yaml', '.yml']:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        line_count = sum(1 for _ in f)
                    info["lines"] = line_count
                except:
                    pass
            
            return info
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _search_files(
        self, 
        pattern: str, 
        path: Path, 
        max_results: int,
        include_hidden: bool
    ) -> Dict[str, Any]:
        """Search for files by name pattern"""
        matches = []
        searched = 0
        
        # Get gitignore patterns
        ignored = self.context.get_gitignore_patterns(path)
        
        try:
            for root, dirs, files in os.walk(path):
                root_path = Path(root)
                
                # Filter directories
                if not include_hidden:
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # Skip ignored directories
                dirs[:] = [d for d in dirs if not any(
                    fnmatch.fnmatch(d, ign) for ign in ignored
                )]
                
                # Search files
                for file in files:
                    if not include_hidden and file.startswith('.'):
                        continue
                    
                    file_path = root_path / file
                    
                    # Skip ignored files
                    if any(fnmatch.fnmatch(str(file_path), ign) for ign in ignored):
                        continue
                    
                    searched += 1
                    
                    # Check pattern match
                    if fnmatch.fnmatch(file, pattern):
                        matches.append({
                            "path": str(file_path),
                            "name": file,
                            "directory": str(root_path)
                        })
                        
                        if len(matches) >= max_results:
                            break
                
                if len(matches) >= max_results:
                    break
            
            return {
                "status": "success",
                "pattern": pattern,
                "matches": len(matches),
                "searched": searched,
                "results": matches
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _search_content(
        self,
        query: str,
        path: Path,
        file_pattern: Optional[str],
        regex: bool,
        case_sensitive: bool,
        max_results: int,
        context_lines: int,
        include_hidden: bool
    ) -> Dict[str, Any]:
        """Search file contents with fallback handling"""
        # Try ripgrep first for speed
        if self._has_ripgrep():
            result = await self._ripgrep_search(
                query, path, file_pattern, regex, case_sensitive,
                max_results, context_lines, include_hidden
            )
            # If ripgrep times out or fails, fallback to Python search
            if result.get("status") in ["timeout", "error"]:
                return await self._python_search(
                    query, path, file_pattern, regex, case_sensitive,
                    max_results, context_lines, include_hidden
                )
            return result
        
        # Fallback to Python implementation
        return await self._python_search(
            query, path, file_pattern, regex, case_sensitive,
            max_results, context_lines, include_hidden
        )
    
    def _has_ripgrep(self) -> bool:
        """Check if ripgrep is available"""
        try:
            subprocess.run(["rg", "--version"], capture_output=True, check=True)
            return True
        except:
            return False
    
    async def _ripgrep_search(
        self,
        query: str,
        path: Path,
        file_pattern: Optional[str],
        regex: bool,
        case_sensitive: bool,
        max_results: int,
        context_lines: int,
        include_hidden: bool
    ) -> Dict[str, Any]:
        """Use ripgrep for fast searching with timeout protection"""
        args = ["rg", "--json"]
        
        # Add options
        if not regex:
            args.append("--fixed-strings")
        if not case_sensitive:
            args.append("--ignore-case")
        if include_hidden:
            args.append("--hidden")
        if context_lines > 0:
            args.extend(["-C", str(context_lines)])
        if max_results:
            args.extend(["-m", str(max_results)])
        if file_pattern:
            args.extend(["-g", file_pattern])
        
        args.extend([query, str(path)])
        
        try:
            # Add timeout to prevent hanging
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024*1024  # 1MB buffer limit
            )
            
            # Wait with timeout (10 seconds max)
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                # Kill the process and fallback
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
                return {"status": "timeout", "error": "Search timed out, falling back to Python search"}
            
            if process.returncode not in [0, 1]:  # 1 means no matches
                error_msg = stderr.decode() if stderr else "Unknown ripgrep error"
                return {"status": "error", "error": error_msg}
            
            # Parse JSON output with size limit
            output_text = stdout.decode()
            if len(output_text) > 5*1024*1024:  # 5MB limit
                return {"status": "error", "error": "Output too large, try narrowing search scope"}
            
            matches = []
            for line in output_text.strip().split('\n'):
                if not line:
                    continue
                try:
                    import json
                    data = json.loads(line)
                    if data.get("type") == "match":
                        match_data = data["data"]
                        matches.append({
                            "file": match_data["path"]["text"],
                            "line": match_data["line_number"],
                            "column": match_data.get("column", 1),
                            "text": match_data["lines"]["text"].strip(),
                            "context": self._extract_context(data)
                        })
                except:
                    continue
            
            return {
                "status": "success",
                "query": query,
                "matches": len(matches),
                "results": matches[:max_results]
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _python_search(
        self,
        query: str,
        path: Path,
        file_pattern: Optional[str],
        regex: bool,
        case_sensitive: bool,
        max_results: int,
        context_lines: int,
        include_hidden: bool
    ) -> Dict[str, Any]:
        """Python fallback for content search with timeout protection"""
        matches = []
        files_searched = 0
        start_time = asyncio.get_event_loop().time()
        max_search_time = 30.0  # 30 second timeout
        
        # Compile pattern
        if regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                pattern = re.compile(query, flags)
            except re.error as e:
                return {"status": "error", "error": f"Invalid regex: {e}"}
        else:
            if not case_sensitive:
                query = query.lower()
        
        # Get files to search with reasonable limits
        search_files = []
        if file_pattern:
            search_files = list(path.glob(file_pattern))[:1000]  # Limit to 1000 files
        else:
            # Search common text files with limits
            for ext in ['.py', '.js', '.ts', '.json', '.md', '.txt', '.yaml', '.yml', '.sh']:
                found_files = list(path.rglob(f'*{ext}'))[:200]  # 200 per extension
                search_files.extend(found_files)
                if len(search_files) >= 1000:  # Total limit
                    break
        
        # Filter ignored files
        try:
            ignored = self.context.get_gitignore_patterns(path)
            search_files = [f for f in search_files if not any(
                fnmatch.fnmatch(str(f), ign) for ign in ignored
            )]
        except:
            pass  # Continue without gitignore filtering if it fails
        
        # Search files with timeout checking
        for file_path in search_files:
            # Check timeout every 10 files
            if files_searched % 10 == 0:
                current_time = asyncio.get_event_loop().time()
                if current_time - start_time > max_search_time:
                    return {
                        "status": "timeout",
                        "query": query,
                        "files_searched": files_searched,
                        "matches": len(matches),
                        "results": matches,
                        "error": "Search timed out - consider narrowing search scope"
                    }
            
            if not include_hidden and file_path.name.startswith('.'):
                continue
            
            if len(matches) >= max_results:
                break
            
            files_searched += 1
            
            try:
                # Skip very large files
                if file_path.stat().st_size > 10*1024*1024:  # 10MB limit
                    continue
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Skip files with too many lines
                if len(lines) > 50000:
                    continue
                
                for i, line in enumerate(lines):
                    if regex:
                        if pattern.search(line):
                            matches.append(self._create_match(
                                file_path, i + 1, line, lines, i, context_lines
                            ))
                    else:
                        search_line = line if case_sensitive else line.lower()
                        if query in search_line:
                            matches.append(self._create_match(
                                file_path, i + 1, line, lines, i, context_lines
                            ))
                    
                    if len(matches) >= max_results:
                        break
                        
            except Exception:
                continue
        
        return {
            "status": "success",
            "query": query,
            "files_searched": files_searched,
            "matches": len(matches),
            "results": matches
        }
    
    def _create_match(
        self, 
        file_path: Path, 
        line_num: int, 
        line: str,
        all_lines: List[str],
        line_idx: int,
        context_lines: int
    ) -> Dict[str, Any]:
        """Create match result with context"""
        match = {
            "file": str(file_path),
            "line": line_num,
            "text": line.strip()
        }
        
        if context_lines > 0:
            context = []
            start = max(0, line_idx - context_lines)
            end = min(len(all_lines), line_idx + context_lines + 1)
            
            for i in range(start, end):
                context.append({
                    "line": i + 1,
                    "text": all_lines[i].rstrip(),
                    "is_match": i == line_idx
                })
            
            match["context"] = context
        
        return match
    
    def _extract_context(self, rg_data: Dict) -> List[Dict]:
        """Extract context from ripgrep JSON output"""
        context = []
        # ripgrep JSON format includes context in a specific structure
        # This is a simplified extraction
        return context