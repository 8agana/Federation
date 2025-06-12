"""FC Analyze tool - Code analysis with async support."""

from typing import Any, Dict, Union, List
from federation_code.core import AsyncEngine, Priority, Mode
from federation_code.analyzers.base import Aspect
from federation_code.tools.base import BaseTool, ToolResult


class AnalyzeTool(BaseTool):
    """Code analysis tool with async and streaming support."""
    
    def __init__(self, engine: AsyncEngine):
        super().__init__(
            name="fc_analyze",
            description="Analyzes code for various issues and patterns with async/streaming support"
        )
        self.engine = engine
        
    def get_schema(self) -> Dict[str, Any]:
        """Get tool parameter schema."""
        return {
            "type": "object",
            "properties": {
                "files": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "string"}}
                    ],
                    "description": "File path(s) or glob patterns to analyze"
                },
                "aspect": {
                    "type": "string",
                    "enum": ["bugs", "security", "performance", "style", "all"],
                    "default": "all",
                    "description": "What aspect to analyze"
                },
                "mode": {
                    "type": "string", 
                    "enum": ["quick", "standard", "deep"],
                    "default": "standard",
                    "description": "Analysis depth"
                },
                "async": {
                    "type": "boolean",
                    "default": False,
                    "description": "Run analysis in background (returns handle)"
                },
                "stream": {
                    "type": "boolean",
                    "default": False,
                    "description": "Stream results as they're found"
                },
                "since_last_run": {
                    "type": "boolean", 
                    "default": False,
                    "description": "Only analyze files changed since last run"
                },
                "include_suggestions": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include fix suggestions"
                },
                "severity_threshold": {
                    "type": "string",
                    "enum": ["info", "warning", "error", "critical"],
                    "default": "info", 
                    "description": "Minimum severity to report"
                },
                "context_lines": {
                    "type": "integer",
                    "default": 3,
                    "description": "Number of context lines around issues"
                },
                "exclude_patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                    "description": "File patterns to exclude"
                },
                "language": {
                    "type": "string",
                    "description": "Override language detection"
                },
                "framework": {
                    "type": "string", 
                    "description": "Override framework detection"
                }
            },
            "required": ["files"]
        }
        
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute code analysis."""
        try:
            # Validate arguments
            self.validate_arguments(arguments)
            
            # Extract parameters
            files = arguments["files"]
            aspect = arguments.get("aspect", "all")
            mode = arguments.get("mode", "standard")
            is_async = arguments.get("async", False)
            stream = arguments.get("stream", False)
            
            # Determine priority based on mode
            priority_map = {
                "quick": Priority.HIGH,
                "standard": Priority.MEDIUM, 
                "deep": Priority.LOW
            }
            priority = priority_map.get(mode, Priority.MEDIUM)
            
            # Determine analyzer type based on aspect
            if aspect == "security":
                task_type = "security"
            else:
                task_type = "analyze"
                
            # Prepare task data
            task_data = {
                "files": files,
                "aspect": aspect,
                "mode": mode,
                "since_last_run": arguments.get("since_last_run", False),
                "include_suggestions": arguments.get("include_suggestions", True),
                "severity_threshold": arguments.get("severity_threshold", "info"),
                "context_lines": arguments.get("context_lines", 3),
                "exclude_patterns": arguments.get("exclude_patterns", []),
                "language": arguments.get("language"),
                "framework": arguments.get("framework")
            }
            
            # Submit task
            if is_async:
                # Background execution
                task_id = self.engine.submit_task(
                    task_type=task_type,
                    data=task_data,
                    priority=priority,
                    mode=Mode(mode),
                    stream=stream
                )
                
                return self.create_json_result({
                    "handle": task_id,
                    "status": "started",
                    "message": f"Analysis started in background. Use fc_status('{task_id}') to check progress."
                })
                
            elif stream:
                # Streaming execution
                task_id = self.engine.submit_task(
                    task_type=task_type,
                    data=task_data,
                    priority=priority,
                    mode=Mode(mode),
                    stream=True
                )
                
                # Collect streaming results
                results = []
                async for result in self.engine.stream_results(task_id):
                    if result.partial:
                        results.append({
                            "type": "partial",
                            "file": result.data.get("file") if result.data else None,
                            "issues_found": len(result.issues) if hasattr(result, 'issues') else 0,
                            "progress": result.progress
                        })
                    else:
                        # Final result
                        results.append({
                            "type": "final",
                            "summary": result.data.summary if result.data else {},
                            "total_issues": len(result.data.issues) if result.data else 0
                        })
                        
                return self.create_json_result({
                    "streaming_results": results,
                    "status": "completed"
                })
                
            else:
                # Synchronous execution (quick mode only)
                if mode != "quick":
                    return self.create_error_result(
                        "Synchronous execution only available for 'quick' mode. "
                        "Use async=True for standard/deep analysis."
                    )
                    
                task_id = self.engine.submit_task(
                    task_type=task_type,
                    data=task_data,
                    priority=Priority.CRITICAL,  # High priority for sync
                    mode=Mode.QUICK,
                    stream=False
                )
                
                # Wait briefly for quick analysis
                import asyncio
                await asyncio.sleep(0.1)
                
                result = self.engine.get_task_result(task_id)
                if result and result.data:
                    return self.create_json_result({
                        "status": "success",
                        "summary": result.data.summary,
                        "issues": [
                            {
                                "id": issue.id,
                                "file": issue.file,
                                "line": issue.line,
                                "column": issue.column,
                                "severity": issue.severity.value,
                                "aspect": issue.aspect.value,
                                "type": issue.type,
                                "message": issue.message,
                                "description": issue.description,
                                "suggestion": issue.suggestion,
                                "fix_available": issue.fix_available,
                                "context": issue.context
                            }
                            for issue in result.data.issues
                        ],
                        "execution_time": result.data.execution_time,
                        "files_analyzed": result.data.files_analyzed
                    })
                else:
                    return self.create_error_result("Quick analysis failed or timed out")
                    
        except Exception as e:
            return self.create_error_result(f"Analysis failed: {str(e)}")
            
    def validate_arguments(self, arguments: Dict[str, Any]) -> None:
        """Validate analysis arguments."""
        if "files" not in arguments:
            raise ValueError("'files' parameter is required")
            
        files = arguments["files"]
        if not files:
            raise ValueError("'files' cannot be empty")
            
        # Validate aspect
        aspect = arguments.get("aspect", "all")
        if aspect not in ["bugs", "security", "performance", "style", "all"]:
            raise ValueError(f"Invalid aspect: {aspect}")
            
        # Validate mode
        mode = arguments.get("mode", "standard")
        if mode not in ["quick", "standard", "deep"]:
            raise ValueError(f"Invalid mode: {mode}")
            
        # Validate severity threshold
        threshold = arguments.get("severity_threshold", "info")
        if threshold not in ["info", "warning", "error", "critical"]:
            raise ValueError(f"Invalid severity threshold: {threshold}")
            
        # Validate context lines
        context_lines = arguments.get("context_lines", 3)
        if not isinstance(context_lines, int) or context_lines < 0:
            raise ValueError("context_lines must be a non-negative integer")