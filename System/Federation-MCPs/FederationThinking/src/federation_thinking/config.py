"""
Configuration for FederationThinking MCP
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for FederationThinking"""
    
    def __init__(self):
        # Federation paths
        self.federation_root = Path(os.environ.get(
            "FEDERATION_ROOT", 
            "/Users/samuelatagana/Documents/Federation"
        ))
        
        # Memory paths
        self.memory_root = self.federation_root / "System/Memory/1_ChromaDBs"
        self.cc_memory_path = self.memory_root / "cc-federation"
        self.dt_memory_path = self.memory_root / "dt-federation"
        
        # SharedVault path  
        self.shared_vault = Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault")
        
        # Nerve Center paths
        self.nerve_center = Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center")
        
        # Config file
        self.config_path = Path.home() / ".federation" / "thinking_config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load config
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        # Default config
        default_config = {
            "default_framework": None,
            "auto_save_thoughts": True,
            "min_confidence_to_save": 0.5,
            "enable_collaboration": True,
            "visual_output_path": str(self.federation_root / "Output/Thinking/Visualizations"),
            "session_timeout_minutes": 60,
            "max_thoughts_per_session": 1000,
            "frameworks": {
                "ooda": {
                    "steps": ["observe", "orient", "decide", "act"],
                    "cycle": True
                },
                "socratic": {
                    "steps": ["question", "examine", "challenge", "refine"],
                    "cycle": False
                },
                "first_principles": {
                    "steps": ["break_down", "fundamental_truths", "rebuild"],
                    "cycle": False
                },
                "five_whys": {
                    "steps": ["why1", "why2", "why3", "why4", "why5"],
                    "cycle": False
                },
                "swot": {
                    "steps": ["strengths", "weaknesses", "opportunities", "threats"],
                    "cycle": False
                },
                "devils_advocate": {
                    "steps": ["assumption", "challenge", "counter", "synthesis"],
                    "cycle": True
                },
                "lateral": {
                    "steps": ["random_entry", "movement", "provocation"],
                    "cycle": False
                },
                "systems": {
                    "steps": ["components", "connections", "purpose", "emergence"],
                    "cycle": False
                }
            }
        }
        
        # Save default config
        self.save_config(default_config)
        return default_config
        
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        self._config = config
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
        
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value
        self.save_config(self._config)
        
    def get_framework(self, name: str) -> Optional[Dict[str, Any]]:
        """Get framework configuration"""
        frameworks = self._config.get("frameworks", {})
        return frameworks.get(name)
        
    def list_frameworks(self) -> List[str]:
        """List available frameworks"""
        return list(self._config.get("frameworks", {}).keys())