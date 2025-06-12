"""
Configuration management tool
NEW - Simplified configuration for Federation Commander
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .base import BaseTool

class ConfigTool(BaseTool):
    """Manage Federation Commander configuration"""
    
    @property
    def description(self) -> str:
        return """Manage Federation Commander configuration settings.
        
        Examples:
        - config("show") - Display current configuration
        - config("set", "default_timeout", 60)
        - config("get", "excluded_patterns")
        - config("reset") - Reset to defaults
        - config("add", "excluded_patterns", "*.log")
        
        Features:
        - View and modify settings
        - Add/remove from lists
        - Reset to defaults
        - Validate settings
        - Export/import configs
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["show", "get", "set", "add", "remove", "reset", "export", "import"],
                    "description": "Configuration action"
                },
                "key": {
                    "type": "string",
                    "description": "Configuration key"
                },
                "value": {
                    "description": "Value to set"
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "yaml"],
                    "default": "json",
                    "description": "Export/import format"
                },
                "path": {
                    "type": "string",
                    "description": "Path for export/import"
                }
            },
            "required": ["action"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        action = arguments["action"]
        
        if action == "show":
            return await self._show_config()
        elif action == "get":
            return await self._get_config(arguments.get("key"))
        elif action == "set":
            return await self._set_config(arguments.get("key"), arguments.get("value"))
        elif action == "add":
            return await self._add_to_config(arguments.get("key"), arguments.get("value"))
        elif action == "remove":
            return await self._remove_from_config(arguments.get("key"), arguments.get("value"))
        elif action == "reset":
            return await self._reset_config(arguments.get("key"))
        elif action == "export":
            return await self._export_config(arguments.get("path"), arguments.get("format", "json"))
        elif action == "import":
            return await self._import_config(arguments.get("path"))
        else:
            return {"status": "error", "error": f"Unknown action: {action}"}
    
    async def _show_config(self) -> Dict[str, Any]:
        """Show current configuration"""
        # Get default config
        defaults = self._get_defaults()
        
        # Get current config
        current = self.config.list()
        
        # Merge and categorize
        categories = {
            "execution": ["default_timeout", "shell", "max_retries"],
            "file_operations": ["max_file_size", "excluded_patterns", "preview_edits"],
            "search": ["search_extensions", "max_search_results", "ripgrep_path"],
            "git": ["auto_stage", "commit_template", "default_branch"],
            "federation": ["federation_root", "memory_path", "task_path"]
        }
        
        organized = {}
        for category, keys in categories.items():
            organized[category] = {}
            for key in keys:
                if key in current:
                    organized[category][key] = {
                        "value": current[key],
                        "default": defaults.get(key),
                        "modified": current[key] != defaults.get(key)
                    }
        
        # Add any uncategorized settings
        uncategorized = {}
        for key, value in current.items():
            categorized = any(key in keys for keys in categories.values())
            if not categorized:
                uncategorized[key] = {
                    "value": value,
                    "default": defaults.get(key),
                    "modified": value != defaults.get(key)
                }
        
        if uncategorized:
            organized["other"] = uncategorized
        
        return {
            "status": "success",
            "configuration": organized,
            "config_file": str(self._get_config_path())
        }
    
    async def _get_config(self, key: Optional[str]) -> Dict[str, Any]:
        """Get specific configuration value"""
        if not key:
            return {"status": "error", "error": "Key required"}
        
        if key in self.config:
            return {
                "status": "success",
                "key": key,
                "value": self.config[key],
                "default": self._get_defaults().get(key)
            }
        else:
            return {
                "status": "error",
                "error": f"Unknown configuration key: {key}",
                "available_keys": list(self._get_defaults().keys())
            }
    
    async def _set_config(self, key: Optional[str], value: Any) -> Dict[str, Any]:
        """Set configuration value"""
        if not key:
            return {"status": "error", "error": "Key required"}
        
        # Validate key
        defaults = self._get_defaults()
        if key not in defaults:
            return {
                "status": "error",
                "error": f"Unknown configuration key: {key}",
                "available_keys": list(defaults.keys())
            }
        
        # Validate value type
        default_value = defaults[key]
        if not self._validate_type(value, default_value):
            return {
                "status": "error",
                "error": f"Invalid type for {key}. Expected {type(default_value).__name__}"
            }
        
        # Update config
        old_value = self.config.get(key)
        self.config[key] = value
        
        # Save to file
        await self._save_config()
        
        return {
            "status": "success",
            "message": f"Configuration updated: {key}",
            "old_value": old_value,
            "new_value": value
        }
    
    async def _add_to_config(self, key: Optional[str], value: Any) -> Dict[str, Any]:
        """Add value to list configuration"""
        if not key or value is None:
            return {"status": "error", "error": "Key and value required"}
        
        if key not in self.config:
            return {"status": "error", "error": f"Unknown configuration key: {key}"}
        
        if not isinstance(self.config[key], list):
            return {"status": "error", "error": f"{key} is not a list configuration"}
        
        if value not in self.config[key]:
            self.config[key].append(value)
            await self._save_config()
            
            return {
                "status": "success",
                "message": f"Added to {key}: {value}",
                "current_list": self.config[key]
            }
        else:
            return {
                "status": "success",
                "message": f"Value already in {key}: {value}",
                "current_list": self.config[key]
            }
    
    async def _remove_from_config(self, key: Optional[str], value: Any) -> Dict[str, Any]:
        """Remove value from list configuration"""
        if not key or value is None:
            return {"status": "error", "error": "Key and value required"}
        
        if key not in self.config:
            return {"status": "error", "error": f"Unknown configuration key: {key}"}
        
        if not isinstance(self.config[key], list):
            return {"status": "error", "error": f"{key} is not a list configuration"}
        
        if value in self.config[key]:
            self.config[key].remove(value)
            await self._save_config()
            
            return {
                "status": "success",
                "message": f"Removed from {key}: {value}",
                "current_list": self.config[key]
            }
        else:
            return {
                "status": "error",
                "error": f"Value not found in {key}: {value}",
                "current_list": self.config[key]
            }
    
    async def _reset_config(self, key: Optional[str] = None) -> Dict[str, Any]:
        """Reset configuration to defaults"""
        defaults = self._get_defaults()
        
        if key:
            # Reset single key
            if key not in defaults:
                return {"status": "error", "error": f"Unknown configuration key: {key}"}
            
            old_value = self.config.get(key)
            self.config[key] = defaults[key]
            await self._save_config()
            
            return {
                "status": "success",
                "message": f"Reset {key} to default",
                "old_value": old_value,
                "new_value": defaults[key]
            }
        else:
            # Reset all
            old_config = dict(self.config)
            self.config.clear()
            self.config.update(defaults)
            await self._save_config()
            
            return {
                "status": "success",
                "message": "All configuration reset to defaults",
                "previous_config": old_config
            }
    
    async def _export_config(self, path: Optional[str], format: str) -> Dict[str, Any]:
        """Export configuration to file"""
        if not path:
            # Default path
            path = f"federation_commander_config.{format}"
        
        export_path = Path(path).expanduser()
        
        try:
            # Prepare config data
            export_data = {
                "federation_commander": {
                    "version": "1.0.0",
                    "config": dict(self.config)
                }
            }
            
            # Write file
            with open(export_path, 'w') as f:
                if format == "json":
                    json.dump(export_data, f, indent=2)
                elif format == "yaml":
                    yaml.dump(export_data, f, default_flow_style=False)
            
            return {
                "status": "success",
                "message": f"Configuration exported to {export_path}",
                "format": format
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _import_config(self, path: Optional[str]) -> Dict[str, Any]:
        """Import configuration from file"""
        if not path:
            return {"status": "error", "error": "Path required"}
        
        import_path = Path(path).expanduser()
        
        if not import_path.exists():
            return {"status": "error", "error": f"File not found: {import_path}"}
        
        try:
            # Read file
            with open(import_path, 'r') as f:
                if import_path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            # Validate structure
            if "federation_commander" not in data or "config" not in data["federation_commander"]:
                return {"status": "error", "error": "Invalid configuration file format"}
            
            # Import config
            imported = data["federation_commander"]["config"]
            old_config = dict(self.config)
            
            # Validate and merge
            defaults = self._get_defaults()
            for key, value in imported.items():
                if key in defaults:
                    if self._validate_type(value, defaults[key]):
                        self.config[key] = value
            
            await self._save_config()
            
            return {
                "status": "success",
                "message": f"Configuration imported from {import_path}",
                "imported_keys": list(imported.keys()),
                "previous_config": old_config
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            # Execution settings
            "default_timeout": 30,
            "shell": "/bin/bash",
            "max_retries": 3,
            
            # File operations
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "excluded_patterns": [
                "*.pyc", "__pycache__", "node_modules", ".git",
                ".DS_Store", "*.swp", "*.swo", "*~"
            ],
            "preview_edits": True,
            
            # Search settings
            "search_extensions": [
                ".py", ".js", ".ts", ".json", ".md", ".txt", 
                ".yaml", ".yml", ".sh", ".tsx", ".jsx"
            ],
            "max_search_results": 50,
            "ripgrep_path": "rg",
            
            # Git settings
            "auto_stage": True,
            "commit_template": "Federation update {timestamp}",
            "default_branch": "main",
            
            # Federation paths
            "federation_root": "/Users/samuelatagana/Documents/Federation",
            "memory_path": "/Users/samuelatagana/Documents/Federation/System/Memory",
            "task_path": "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault/📋 TaskTracker"
        }
    
    def _get_config_path(self) -> Path:
        """Get configuration file path"""
        return Path.home() / ".federation" / "commander_config.json"
    
    async def _save_config(self):
        """Save configuration to file"""
        config_path = self._get_config_path()
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _validate_type(self, value: Any, reference: Any) -> bool:
        """Validate value type against reference"""
        if isinstance(reference, bool):
            return isinstance(value, bool)
        elif isinstance(reference, int):
            return isinstance(value, (int, float))
        elif isinstance(reference, str):
            return isinstance(value, str)
        elif isinstance(reference, list):
            return isinstance(value, list)
        elif isinstance(reference, dict):
            return isinstance(value, dict)
        return True