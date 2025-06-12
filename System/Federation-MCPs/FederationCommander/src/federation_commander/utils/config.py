"""
Configuration management for Federation Commander
Simple, no-nonsense config that doesn't require separate chat windows
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

class Config:
    """Simple configuration management"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".federation_commander" / "config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default configuration
        return {
            "shell": os.environ.get("SHELL", "/bin/bash"),
            "federation_root": "/Users/samuelatagana/Documents/Federation",
            "default_timeout": 30,
            "auto_git_ignore": True,
            "preview_edits": True,
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "excluded_patterns": [".git", "__pycache__", "*.pyc", ".DS_Store"],
            "federation_paths": {
                "shared_vault": "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault",
                "nerve_center": "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center",
                "chromadb_cc": "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation",
                "chromadb_dt": "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/dt-federation",
                "task_tracker": "/Users/samuelatagana/Documents/Federation/System/TaskTracker"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def list(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()