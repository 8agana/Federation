"""
Federation context management for web operations
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

class FederationContext:
    """Manages Federation-specific context for web operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.federation_root = Path("/Users/samuelatagana/Documents/Federation")
        self.current_task = None
        self.current_project = None
        self.session_id = None
        
    def get_federation_domains(self) -> List[str]:
        """Get list of Federation-related domains to prioritize"""
        return [
            "anthropic.com",
            "docs.anthropic.com",
            "github.com/anthropics",
            "modelcontextprotocol.io",
            "docs.modelcontextprotocol.io",
            # Add more Federation-specific domains
        ]
    
    def get_shared_vault_path(self) -> Path:
        """Get SharedVault path"""
        return Path(self.config.get("shared_vault_path"))
    
    def get_interest_docs_path(self) -> Path:
        """Get path to interest documents"""
        vault = self.get_shared_vault_path()
        folder = self.config.get("interest_docs_folder", "🧠 Knowledge Base/Interests")
        return vault / folder
    
    def get_personal_interest_doc(self, instance: str = "CC") -> Path:
        """Get path to personal interest document"""
        return self.get_interest_docs_path() / f"{instance} - What Interests Me.md"
    
    def get_shared_interest_doc(self) -> Path:
        """Get path to shared interest document"""
        return self.get_interest_docs_path() / "Federation - Shared Interests & Discoveries.md"
    
    def get_memory_path(self) -> Path:
        """Get ChromaDB memory path"""
        return Path(self.config.get("federation_memory_path"))
    
    def set_session(self, session_id: str, task: Optional[str] = None, project: Optional[str] = None):
        """Set current session context"""
        self.session_id = session_id
        self.current_task = task
        self.current_project = project
    
    def get_session_context(self) -> Dict[str, Any]:
        """Get current session context"""
        return {
            "session_id": self.session_id,
            "task": self.current_task,
            "project": self.current_project,
            "timestamp": datetime.now().isoformat(),
            "federation_root": str(self.federation_root)
        }
    
    def is_federation_url(self, url: str) -> bool:
        """Check if URL is Federation-related"""
        federation_domains = self.get_federation_domains()
        return any(domain in url.lower() for domain in federation_domains)
    
    def get_task_context(self) -> Optional[Dict[str, Any]]:
        """Get context from current task if available"""
        if not self.current_task:
            return None
            
        # TODO: Integrate with TaskTracker to get task details
        return {
            "task_id": self.current_task,
            "project": self.current_project,
            "priority": "high"  # Default for now
        }