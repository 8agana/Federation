"""
Base tool class for FederationWeb tools
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
import asyncio
from datetime import datetime

from ..utils.config import Config
from ..core.context import FederationContext

class BaseTool(ABC):
    """Base class for all FederationWeb tools"""
    
    def __init__(self, config: Config, context: FederationContext):
        self.config = config
        self.context = context
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for tool parameters"""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        """Execute the tool with given arguments"""
        pass
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> None:
        """Validate arguments against schema"""
        # TODO: Implement proper JSON schema validation
        required = self.get_schema().get("required", [])
        for req in required:
            if req not in arguments:
                raise ValueError(f"Missing required argument: {req}")
    
    async def with_timeout(self, coro, timeout: Optional[int] = None):
        """Execute coroutine with timeout"""
        if timeout is None:
            timeout = self.config.get("search_timeout", 30)
        
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "message": f"Operation timed out after {timeout} seconds"
            }
    
    def create_response(self, status: str = "success", **kwargs) -> Dict[str, Any]:
        """Create standardized response"""
        response = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "tool": self.__class__.__name__,
            **kwargs
        }
        
        # Add session context if available
        if self.context.session_id:
            response["session_id"] = self.context.session_id
            
        return response
    
    def create_error_response(self, error: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        """Create standardized error response"""
        response = {
            "status": "error",
            "error": str(error),
            "timestamp": datetime.now().isoformat(),
            "tool": self.__class__.__name__
        }
        
        if details:
            response["details"] = details
            
        return response