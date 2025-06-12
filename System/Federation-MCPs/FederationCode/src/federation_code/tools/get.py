"""FC Get tool - Retrieve async operation results."""

from typing import Any, Dict
from federation_code.core import AsyncEngine
from federation_code.tools.base import BaseTool, ToolResult


class GetTool(BaseTool):
    """Retrieve results of async operations."""
    
    def __init__(self, engine: AsyncEngine):
        super().__init__(
            name="fc_get",
            description="Retrieve results of async operations"
        )
        self.engine = engine
        
    def get_schema(self) -> Dict[str, Any]:
        """Get tool parameter schema."""
        return {
            "type": "object",
            "properties": {
                "handle": {
                    "type": "string",
                    "description": "Operation handle"
                },
                "partial": {
                    "type": "boolean",
                    "default": False,
                    "description": "Get partial results if available"
                },
                "wait": {
                    "type": "boolean", 
                    "default": False,
                    "description": "Wait for completion"
                },
                "timeout": {
                    "type": "number",
                    "default": 30,
                    "description": "Max wait time in seconds"
                }
            },
            "required": ["handle"]
        }
        
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Retrieve operation results."""
        try:
            handle = arguments["handle"]
            partial = arguments.get("partial", False)
            wait = arguments.get("wait", False)
            timeout = arguments.get("timeout", 30)
            
            # Get current status
            status = self.engine.get_task_status(handle)
            
            if not status:
                return self.create_error_result(f"Task not found: {handle}")
                
            # If requesting partial results
            if partial:
                partial_result = await self.engine.get_partial_results(handle)
                if partial_result and partial_result.data:
                    return self.create_json_result({
                        "handle": handle,
                        "status": "partial",
                        "progress": partial_result.progress,
                        "partial_data": self._format_analysis_result(partial_result.data)
                    })
                else:
                    return self.create_json_result({
                        "handle": handle,
                        "status": status.status.value,
                        "message": "No partial results available"
                    })
                    
            # Check if already completed
            if status.status.value in ["completed", "failed", "cancelled"]:
                return await self._get_final_result(handle, status)
                
            # Wait for completion if requested
            if wait and status.status.value in ["pending", "running"]:
                import asyncio
                
                wait_time = 0
                poll_interval = 0.5
                
                while wait_time < timeout:
                    await asyncio.sleep(poll_interval)
                    wait_time += poll_interval
                    
                    status = self.engine.get_task_status(handle)
                    if not status or status.status.value in ["completed", "failed", "cancelled"]:
                        break
                        
                # Get final result
                if status and status.status.value in ["completed", "failed", "cancelled"]:
                    return await self._get_final_result(handle, status)
                else:
                    return self.create_json_result({
                        "handle": handle,
                        "status": "timeout",
                        "message": f"Operation did not complete within {timeout} seconds",
                        "current_progress": status.progress if status else 0
                    })
                    
            # Task not ready and not waiting
            return self.create_json_result({
                "handle": handle,
                "status": status.status.value,
                "progress": status.progress,
                "message": f"Task is {status.status.value}. Use wait=true to wait for completion."
            })
            
        except Exception as e:
            return self.create_error_result(f"Failed to get results: {str(e)}")
            
    async def _get_final_result(self, handle: str, status) -> ToolResult:
        """Get final result for completed task."""
        if status.status.value == "failed":
            return self.create_json_result({
                "handle": handle,
                "status": "failed",
                "error": status.error,
                "message": f"Task failed: {status.error}"
            })
            
        elif status.status.value == "cancelled":
            return self.create_json_result({
                "handle": handle,
                "status": "cancelled",
                "message": "Task was cancelled"
            })
            
        elif status.status.value == "completed":
            # Get final result
            result = self.engine.get_task_result(handle)
            
            if result and result.data:
                return self.create_json_result({
                    "handle": handle,
                    "status": "success",
                    "data": self._format_analysis_result(result.data),
                    "execution_time": result.data.execution_time,
                    "files_analyzed": result.data.files_analyzed
                })
            else:
                return self.create_error_result("Task completed but no result data available")
                
        return self.create_error_result(f"Unknown task status: {status.status.value}")
        
    def _format_analysis_result(self, analysis_result) -> Dict[str, Any]:
        """Format analysis result for JSON output."""
        return {
            "summary": analysis_result.summary,
            "issues": [
                {
                    "id": issue.id,
                    "file": issue.file,
                    "line": issue.line,
                    "column": issue.column,
                    "end_line": issue.end_line,
                    "end_column": issue.end_column,
                    "severity": issue.severity.value,
                    "aspect": issue.aspect.value,
                    "type": issue.type,
                    "message": issue.message,
                    "description": issue.description,
                    "suggestion": issue.suggestion,
                    "fix_available": issue.fix_available,
                    "context": issue.context,
                    "references": issue.references
                }
                for issue in analysis_result.issues
            ],
            "cache_hits": analysis_result.cache_hits
        }