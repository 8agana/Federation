"""FC Status tool - Check async operation status."""

from typing import Any, Dict
from federation_code.core import AsyncEngine
from federation_code.tools.base import BaseTool, ToolResult


class StatusTool(BaseTool):
    """Check status of async operations."""
    
    def __init__(self, engine: AsyncEngine):
        super().__init__(
            name="fc_status",
            description="Check status of async operations"
        )
        self.engine = engine
        
    def get_schema(self) -> Dict[str, Any]:
        """Get tool parameter schema."""
        return {
            "type": "object",
            "properties": {
                "handle": {
                    "type": "string",
                    "description": "Operation handle to check"
                },
                "verbose": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include detailed progress information"
                }
            },
            "required": ["handle"]
        }
        
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Check operation status."""
        try:
            handle = arguments["handle"]
            verbose = arguments.get("verbose", False)
            
            # Get task status
            status = self.engine.get_task_status(handle)
            
            if not status:
                return self.create_error_result(f"Task not found: {handle}")
                
            # Build response
            response = {
                "handle": handle,
                "status": status.status.value,
                "progress": status.progress
            }
            
            # Add message if available
            if status.error:
                response["message"] = status.error
            elif status.status.value == "running":
                response["message"] = "Analysis in progress..."
            elif status.status.value == "completed":
                response["message"] = "Analysis completed successfully"
            elif status.status.value == "pending":
                response["message"] = "Waiting to start analysis"
            elif status.status.value == "cancelled":
                response["message"] = "Analysis was cancelled"
                
            # Add verbose details
            if verbose:
                response["details"] = {
                    "start_time": status.start_time.isoformat() if status.start_time else None,
                    "end_time": status.end_time.isoformat() if status.end_time else None,
                }
                
                # Calculate elapsed time
                if status.start_time:
                    from datetime import datetime
                    end_time = status.end_time or datetime.now()
                    elapsed = (end_time - status.start_time).total_seconds()
                    response["details"]["time_elapsed"] = elapsed
                    
                # Add estimated remaining time for running tasks
                if status.status.value == "running" and status.progress > 0:
                    elapsed = response["details"].get("time_elapsed", 0)
                    if elapsed > 0:
                        estimated_total = elapsed / status.progress
                        estimated_remaining = estimated_total - elapsed
                        response["details"]["estimated_remaining"] = max(0, estimated_remaining)
                        
            # Check if partial results are available
            partial = await self.engine.get_partial_results(handle)
            response["partial_results_available"] = partial is not None
            
            return self.create_json_result(response)
            
        except Exception as e:
            return self.create_error_result(f"Failed to get status: {str(e)}")