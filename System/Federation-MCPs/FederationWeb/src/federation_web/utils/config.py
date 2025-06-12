"""
Configuration management for FederationWeb
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

class Config:
    """Configuration management for FederationWeb"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".federation" / "web" / "config.json"
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
            # API Keys (should be in environment variables)
            "brave_api_key": os.environ.get("BRAVE_API_KEY", ""),
            "groq_api_key": os.environ.get("GROQ_API_KEY", ""),
            
            # Search settings
            "default_search_engine": "brave",
            "max_search_results": 10,
            "search_timeout": 30,
            "fallback_enabled": True,
            "fallback_chain": ["brave", "duckduckgo", "google"],
            
            # Content extraction
            "max_content_length": 50000,
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "extraction_timeout": 30,
            "smart_extraction": True,
            "preserve_code_blocks": True,
            
            # Memory integration
            "auto_memorize": True,
            "memory_threshold": 0.7,  # Significance score for auto-save
            "federation_memory_path": "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation",
            
            # SharedVault paths
            "shared_vault_path": "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault",
            "interest_docs_folder": "🧠 Knowledge Base/Interests",
            
            # Caching
            "cache_enabled": True,
            "cache_ttl": 300,  # 5 minutes
            "max_cache_size": 100,  # MB
            
            # Session management
            "session_timeout": 3600,  # 1 hour
            "max_session_history": 50,
            
            # Interest exploration
            "interest_categories": [
                "science", "technology", "art", "history", "philosophy",
                "mathematics", "nature", "culture", "innovation", "creativity"
            ],
            "mood_presets": {
                "curious": {"depth": "surface", "time": 15, "variety": "high"},
                "deep_dive": {"depth": "comprehensive", "time": 60, "variety": "low"},
                "casual": {"depth": "surface", "time": 10, "variety": "medium"},
                "collaborative": {"depth": "medium", "time": 30, "variety": "high"}
            },
            
            # Performance
            "max_concurrent_requests": 5,
            "request_delay": 0.5,  # Seconds between requests
            "user_agent": "FederationWeb/1.0 (Federation Research Tool)",
            
            # Logging
            "log_level": "INFO",
            "log_file": Path.home() / ".federation" / "web_logs" / "federation_web.log"
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