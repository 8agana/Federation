"""
Unified file operations tool
Replaces: read_file, read_multiple_files, write_file, create_directory, move_file
"""

import os
import shutil
import aiofiles
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Union, Optional
import json
import base64
from urllib.request import urlopen
from urllib.parse import urlparse

from .base import BaseTool

class FileTool(BaseTool):
    """Unified file operations with smart mode detection"""
    
    @property
    def description(self) -> str:
        return """Universal file operations - read, write, create, move, batch operations.
        
        Smart mode detection:
        - Read: file("config.json")
        - Write: file("config.json", content)
        - Batch read: file(["*.py", "*.md"])
        - Create dir: file("new_folder/", create_dir=True)
        - Move: file("old.txt", move_to="new.txt")
        
        Features:
        - URL support for reading
        - Image display support
        - Automatic encoding detection
        - Batch operations on multiple files
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "oneOf": [
                        {"type": "string", "description": "File/directory path or URL"},
                        {"type": "array", "items": {"type": "string"}, "description": "Multiple paths for batch operations"}
                    ]
                },
                "content": {
                    "type": "string",
                    "description": "Content to write (if provided, writes to file)"
                },
                "mode": {
                    "type": "string",
                    "enum": ["auto", "read", "write", "append"],
                    "default": "auto",
                    "description": "Operation mode (auto-detected by default)"
                },
                "encoding": {
                    "type": "string",
                    "default": "utf-8",
                    "description": "File encoding"
                },
                "create_dir": {
                    "type": "boolean",
                    "default": False,
                    "description": "Create directory"
                },
                "move_to": {
                    "type": "string",
                    "description": "Destination path for move operation"
                }
            },
            "required": ["path"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        path_arg = arguments["path"]
        content = arguments.get("content")
        mode = arguments.get("mode", "auto")
        encoding = arguments.get("encoding", "utf-8")
        create_dir = arguments.get("create_dir", False)
        move_to = arguments.get("move_to")
        
        # Handle batch operations
        if isinstance(path_arg, list):
            return await self._batch_operation(path_arg, encoding)
        
        # Single file operation
        path = path_arg
        
        # Check if URL
        if self._is_url(path):
            return await self._read_url(path)
        
        path_obj = Path(path).expanduser()
        
        # Auto-detect mode
        if mode == "auto":
            if content is not None:
                mode = "write"
            elif move_to:
                mode = "move"
            elif create_dir or path.endswith('/'):
                mode = "create_dir"
            else:
                mode = "read"
        
        # Execute operation
        if mode == "create_dir":
            return await self._create_directory(path_obj)
        elif mode == "move":
            return await self._move_file(path_obj, Path(move_to).expanduser())
        elif mode == "read":
            return await self._read_file(path_obj, encoding)
        elif mode in ["write", "append"]:
            return await self._write_file(path_obj, content, mode, encoding)
        else:
            return {"status": "error", "error": f"Unknown mode: {mode}"}
    
    async def _batch_operation(self, patterns: List[str], encoding: str) -> Dict[str, Any]:
        """Handle batch file operations"""
        results = {}
        
        for pattern in patterns:
            # Expand glob patterns
            if '*' in pattern or '?' in pattern:
                matches = list(Path().glob(pattern))
                for match in matches:
                    if match.is_file():
                        results[str(match)] = await self._read_file(match, encoding)
            else:
                path = Path(pattern).expanduser()
                if path.exists() and path.is_file():
                    results[str(path)] = await self._read_file(path, encoding)
        
        return {
            "status": "success",
            "files_read": len(results),
            "data": results
        }
    
    async def _read_file(self, path: Path, encoding: str) -> Dict[str, Any]:
        """Read a single file"""
        if not path.exists():
            return {"status": "error", "error": f"File not found: {path}"}
        
        if not path.is_file():
            return {"status": "error", "error": f"Not a file: {path}"}
        
        # Check file size
        size = path.stat().st_size
        max_size = self.config.get("max_file_size", 10 * 1024 * 1024)
        
        if size > max_size:
            return {
                "status": "error",
                "error": f"File too large: {size} bytes (max: {max_size})"
            }
        
        # Check if image
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
        if path.suffix.lower() in image_extensions:
            return await self._read_image(path)
        
        # Read text file
        try:
            async with aiofiles.open(path, 'r', encoding=encoding) as f:
                content = await f.read()
            
            return {
                "status": "success",
                "path": str(path),
                "size": size,
                "content": content
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _read_image(self, path: Path) -> Dict[str, Any]:
        """Read image file and return base64 for display"""
        try:
            async with aiofiles.open(path, 'rb') as f:
                image_data = await f.read()
            
            base64_data = base64.b64encode(image_data).decode('utf-8')
            mime_type = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg', 
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.bmp': 'image/bmp'
            }.get(path.suffix.lower(), 'image/png')
            
            return {
                "status": "success",
                "path": str(path),
                "type": "image",
                "mime_type": mime_type,
                "data": f"data:{mime_type};base64,{base64_data}"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _write_file(self, path: Path, content: str, mode: str, encoding: str) -> Dict[str, Any]:
        """Write content to file"""
        try:
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            write_mode = 'w' if mode == "write" else 'a'
            
            async with aiofiles.open(path, write_mode, encoding=encoding) as f:
                await f.write(content)
            
            return {
                "status": "success",
                "path": str(path),
                "size": len(content),
                "mode": mode
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _create_directory(self, path: Path) -> Dict[str, Any]:
        """Create directory"""
        try:
            path.mkdir(parents=True, exist_ok=True)
            return {
                "status": "success", 
                "path": str(path),
                "created": True
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _move_file(self, src: Path, dst: Path) -> Dict[str, Any]:
        """Move or rename file/directory"""
        if not src.exists():
            return {"status": "error", "error": f"Source not found: {src}"}
        
        try:
            # Create parent directory if needed
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src), str(dst))
            
            return {
                "status": "success",
                "from": str(src),
                "to": str(dst)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _read_url(self, url: str) -> Dict[str, Any]:
        """Read content from URL"""
        try:
            with urlopen(url, timeout=30) as response:
                content = response.read()
                
                # Check if image
                content_type = response.headers.get('Content-Type', '')
                if content_type.startswith('image/'):
                    base64_data = base64.b64encode(content).decode('utf-8')
                    return {
                        "status": "success",
                        "url": url,
                        "type": "image",
                        "mime_type": content_type,
                        "data": f"data:{content_type};base64,{base64_data}"
                    }
                else:
                    # Assume text
                    text = content.decode('utf-8', errors='replace')
                    return {
                        "status": "success",
                        "url": url,
                        "content": text
                    }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _is_url(self, path: str) -> bool:
        """Check if path is a URL"""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except:
            return False