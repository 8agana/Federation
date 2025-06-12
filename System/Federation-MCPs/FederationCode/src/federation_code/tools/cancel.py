"""FC Cancel tool - Cancel running async operations."""

from typing import Any, Dict
from federation_code.core import AsyncEngine
from federation_code.tools.base import BaseTool, ToolResult


class CancelTool(BaseTool):
    """Cancel running async operations."""
    
    def __init__(self, engine: AsyncEngine):
        super().__init__(
            name="fc_cancel",
            description="Cancel running async operations"
        )
        self.engine = engine
        
    def get_schema(self) -> Dict[str, Any]:
        """Get tool parameter schema."""
        return {
            "type": "object",
            "properties": {
                "handle": {
                    "type": "string",
                    "description": "Operation handle to cancel"
                },
                "force": {
                    "type": "boolean",
                    "default": False,
                    "description": "Force termination (use with caution)"
                }
            },
            "required": ["handle"]
        }
        
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Cancel operation."""
        try:
            handle = arguments["handle"]
            force = arguments.get("force", False)
            
            # Get current status
            status = self.engine.get_task_status(handle)
            
            if not status:
                return self.create_json_result({
                    "status": "not_found",
                    "message": f"Task not found: {handle}"
                })
                
            # Check if already completed
            if status.status.value in ["completed", "failed", "cancelled"]:
                return self.create_json_result({
                    "status": "already_completed",
                    "message": f"Task is already {status.status.value}",
                    "handle": handle
                })
                
            # Attempt cancellation
            cancelled = await self.engine.cancel_task(handle, force=force)
            
            if cancelled:
                # Check for partial results
                partial_results = None
                try:
                    partial = await self.engine.get_partial_results(handle)
                    if partial and partial.data:
                        partial_results = {
                            "summary": partial.data.summary,
                            "issues_found": len(partial.data.issues),
                            "files_analyzed": partial.data.files_analyzed,
                            "progress": partial.progress
                        }
                except:
                    pass  # No partial results available
                    
                response = {
                    "status": "cancelled",
                    "handle": handle,
                    "message": f"Task {handle} was successfully cancelled",
                    "cleanup_performed": True
                }
                
                if partial_results:
                    response["partial_results"] = partial_results
                    response["message"] += f" (partial results available: {partial_results['issues_found']} issues found)"
                    
                return self.create_json_result(response)
                
            else:
                return self.create_json_result({
                    "status": "failed_to_cancel",
                    "handle": handle,
                    "message": f"Failed to cancel task {handle}. It may have completed already."
                })
                
        except Exception as e:
            return self.create_error_result(f"Failed to cancel task: {str(e)}")