"""
Federation context awareness
Understands Federation structure and provides smart defaults
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class FederationContext:
    """Federation-aware context for smart operations"""
    
    def __init__(self):
        self.federation_root = Path("/Users/samuelatagana/Documents/Federation")
        self._git_status = None
        self._current_branch = None
        
    def is_git_repo(self, path: Optional[Path] = None) -> bool:
        """Check if path is in a git repository"""
        check_path = path or Path.cwd()
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=check_path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_git_info(self, path: Optional[Path] = None) -> Dict[str, str]:
        """Get git information for current context"""
        check_path = path or Path.cwd()
        
        if not self.is_git_repo(check_path):
            return {}
        
        info = {}
        
        # Get current branch
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=check_path,
                capture_output=True,
                text=True
            )
            info['branch'] = result.stdout.strip()
        except Exception:
            pass
        
        # Get status summary
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=check_path,
                capture_output=True,
                text=True
            )
            changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
            info['changes'] = len(changes)
            info['has_changes'] = len(changes) > 0
        except Exception:
            pass
        
        return info
    
    def detect_project_type(self, path: Path) -> Optional[str]:
        """Detect the type of project in a directory"""
        # Check for Federation-specific structures
        if (path / "System" / "Memory").exists():
            return "federation_root"
        elif (path / "TaskTracker").exists():
            return "federation_system"
        elif (path / "pyproject.toml").exists():
            return "python_project"
        elif (path / "package.json").exists():
            return "node_project"
        elif (path / "Cargo.toml").exists():
            return "rust_project"
        elif (path / "go.mod").exists():
            return "go_project"
        
        return None
    
    def get_gitignore_patterns(self, path: Path) -> List[str]:
        """Get gitignore patterns for a directory"""
        patterns = []
        gitignore_path = path / ".gitignore"
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        
        # Add default patterns
        patterns.extend([
            "__pycache__",
            "*.pyc",
            ".DS_Store",
            ".git",
            "node_modules",
            ".env",
            "*.log"
        ])
        
        return list(set(patterns))
    
    def is_federation_path(self, path: Path) -> bool:
        """Check if path is within Federation structure"""
        try:
            path.resolve().relative_to(self.federation_root)
            return True
        except ValueError:
            return False
    
    def get_relative_path(self, path: Path) -> str:
        """Get path relative to Federation root if applicable"""
        try:
            return str(path.resolve().relative_to(self.federation_root))
        except ValueError:
            return str(path)
    
    def suggest_location(self, file_type: str) -> Path:
        """Suggest appropriate location for different file types"""
        suggestions = {
            "mcp": self.federation_root / "System",
            "app": self.federation_root / "Apps", 
            "script": self.federation_root / "Scripts",
            "doc": Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault"),
            "memory": self.federation_root / "System" / "Memory",
            "task": self.federation_root / "System" / "TaskTracker"
        }
        
        return suggestions.get(file_type, Path.cwd())