"""Base class for all Federation Commander tools"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self, config, context):
        self.config = config
        self.context = context
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for MCP"""
        pass
    
    @property
    @abstractmethod  
    def input_schema(self) -> Dict[str, Any]:
        """JSON schema for tool inputs"""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        """Execute the tool with given arguments"""
        pass