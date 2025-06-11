#!/usr/bin/env python3
"""
Wake Manager for TaskTracker MCP
Handles wake message sending between CC and DT instances

Includes message sanitization to prevent script syntax errors
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WakeManager:
    """Manages wake messages between CC and DT instances"""
    
    def __init__(self):
        """Initialize wake manager with script paths and config"""
        # Wake script paths
        self.script_base = Path("/Users/samuelatagana/Documents/Federation/System/MaintScripts/Scripts")
        self.dt_wake_script = self.script_base / "wake_dt.sh"
        self.cc_wake_script = self.script_base / "wake_cc.sh"
        
        # Configuration file
        self.config_file = Path(__file__).parent / "wake_config.json"
        self.config = self._load_config()
        
        # Wake history
        self.wake_history = []
        
    def _load_config(self) -> Dict[str, Any]:
        """Load wake configuration from file"""
        default_config = {
            "auto_wake_enabled": False,  # OFF by default - must be manually enabled
            "auto_wake_targets": ["dt"],  # Who to wake automatically
            "auto_wake_triggers": ["create", "complete", "status_change"],  # Which events trigger wakes
            "message_prefix": "SharedVault: ",
            "max_message_length": 200
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                logger.error(f"Failed to load wake config: {e}")
                return default_config
        else:
            # Create default config file
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save wake configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.config = config
        except Exception as e:
            logger.error(f"Failed to save wake config: {e}")
    
    def sanitize_message(self, message: str) -> str:
        """
        Sanitize message to prevent bash script syntax errors
        
        Args:
            message: Raw message to sanitize
            
        Returns:
            Sanitized message safe for bash scripts
        """
        if not message:
            return ""
        
        # Remove problematic characters that break bash scripts
        sanitized = message.replace("'", "").replace('"', "")
        sanitized = sanitized.replace("`", "").replace("$", "")
        sanitized = sanitized.replace("\\", "").replace("\n", " ")
        
        # Trim to max length
        max_length = self.config.get("max_message_length", 200)
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length-3] + "..."
        
        return sanitized.strip()
    
    def wake_dt(self, message: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send wake message to Desktop Claude
        
        Args:
            message: Message to send
            task_id: Optional task ID for context
            
        Returns:
            Result dictionary with success status
        """
        try:
            # Sanitize message
            clean_message = self.sanitize_message(message)
            if not clean_message:
                return {"success": False, "error": "Empty message after sanitization"}
            
            # Add prefix if configured
            prefix = self.config.get("message_prefix", "")
            if prefix and not clean_message.startswith(prefix):
                clean_message = prefix + clean_message
            
            # Add task context if provided
            if task_id:
                clean_message = f"[{task_id}] {clean_message}"
            
            # Execute wake script
            result = subprocess.run(
                [str(self.dt_wake_script), clean_message],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Record wake attempt
            wake_record = {
                "timestamp": datetime.now().isoformat(),
                "target": "dt",
                "message": clean_message,
                "task_id": task_id,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
            self.wake_history.append(wake_record)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Wake message sent to DT",
                    "clean_message": clean_message
                }
            else:
                return {
                    "success": False,
                    "error": f"Wake script failed: {result.stderr}",
                    "clean_message": clean_message
                }
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Wake script timeout"}
        except Exception as e:
            return {"success": False, "error": f"Wake failed: {str(e)}"}
    
    def wake_cc(self, message: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send wake message to Claude Code
        
        Args:
            message: Message to send
            task_id: Optional task ID for context
            
        Returns:
            Result dictionary with success status
        """
        try:
            # Sanitize message
            clean_message = self.sanitize_message(message)
            if not clean_message:
                return {"success": False, "error": "Empty message after sanitization"}
            
            # Add prefix if configured
            prefix = self.config.get("message_prefix", "")
            if prefix and not clean_message.startswith(prefix):
                clean_message = prefix + clean_message
            
            # Add task context if provided
            if task_id:
                clean_message = f"[{task_id}] {clean_message}"
            
            # Execute wake script
            result = subprocess.run(
                [str(self.cc_wake_script), clean_message],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Record wake attempt
            wake_record = {
                "timestamp": datetime.now().isoformat(),
                "target": "cc",
                "message": clean_message,
                "task_id": task_id,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
            self.wake_history.append(wake_record)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Wake message sent to CC",
                    "clean_message": clean_message
                }
            else:
                return {
                    "success": False,
                    "error": f"Wake script failed: {result.stderr}",
                    "clean_message": clean_message
                }
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Wake script timeout"}
        except Exception as e:
            return {"success": False, "error": f"Wake failed: {str(e)}"}
    
    def auto_wake_for_event(self, event_type: str, message: str, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Send auto-wake messages based on configuration
        
        Args:
            event_type: Type of event (create, update, complete, status_change)
            message: Message to send
            task_id: Task ID for context
            
        Returns:
            List of wake results
        """
        results = []
        
        # Check if auto-wake is enabled
        if not self.config.get("auto_wake_enabled", True):
            return results
        
        # Check if this event type should trigger wake
        triggers = self.config.get("auto_wake_triggers", [])
        if event_type not in triggers:
            return results
        
        # Send wake to configured targets
        targets = self.config.get("auto_wake_targets", [])
        for target in targets:
            if target == "dt":
                result = self.wake_dt(message, task_id)
                results.append({"target": "dt", **result})
            elif target == "cc":
                result = self.wake_cc(message, task_id)
                results.append({"target": "cc", **result})
        
        return results
    
    def update_config(self, **kwargs) -> Dict[str, Any]:
        """
        Update wake configuration
        
        Args:
            **kwargs: Configuration values to update
            
        Returns:
            Updated configuration
        """
        new_config = self.config.copy()
        new_config.update(kwargs)
        self._save_config(new_config)
        
        return new_config
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current wake manager status
        
        Returns:
            Status dictionary with config and recent history
        """
        recent_wakes = self.wake_history[-5:] if self.wake_history else []
        
        return {
            "config": self.config,
            "recent_wakes": recent_wakes,
            "total_wakes": len(self.wake_history),
            "script_paths": {
                "dt_wake": str(self.dt_wake_script),
                "cc_wake": str(self.cc_wake_script)
            },
            "script_exists": {
                "dt_wake": self.dt_wake_script.exists(),
                "cc_wake": self.cc_wake_script.exists()
            }
        }


# Example usage and testing
if __name__ == "__main__":
    wm = WakeManager()
    
    # Test message sanitization
    test_msg = "Task update: Sam's new task with 'quotes' and \"double quotes\""
    clean_msg = wm.sanitize_message(test_msg)
    print(f"Original: {test_msg}")
    print(f"Sanitized: {clean_msg}")
    
    # Test configuration
    status = wm.get_status()
    print(f"\nWake Manager Status:")
    print(f"Auto-wake enabled: {status['config']['auto_wake_enabled']}")
    print(f"Targets: {status['config']['auto_wake_targets']}")
    print(f"Triggers: {status['config']['auto_wake_triggers']}")