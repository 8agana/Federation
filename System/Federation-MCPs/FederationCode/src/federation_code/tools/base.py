"""Base tool class for MCP tools."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ToolResult(BaseModel):
    """Standard tool result format."""
    content: List[Dict[str, Any]]
    isError: bool = False


class BaseTool(ABC):
    """Base class for all MCP tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's parameter schema."""
        pass
        
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute the tool with given arguments."""
        pass
        
    def validate_arguments(self, arguments: Dict[str, Any]) -> None:
        """Validate tool arguments (override in subclasses)."""
        pass
        
    def create_text_result(self, text: str) -> ToolResult:
        """Create a text result."""
        return ToolResult(
            content=[{"type": "text", "text": text}]
        )
        
    def create_error_result(self, error: str) -> ToolResult:
        """Create an error result."""
        return ToolResult(
            content=[{"type": "text", "text": f"Error: {error}"}],
            isError=True
        )
        
    def create_json_result(self, data: Any) -> ToolResult:
        """Create a JSON result."""
        import json
        return ToolResult(
            content=[{"type": "text", "text": json.dumps(data, indent=2)}]
        )