"""
MCP Server for FederationThinking
Implements the enhanced sequential thinking tools
"""
import asyncio
import json
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

from federation_thinking.config import Config
from federation_thinking.memory import ThinkingMemory
from federation_thinking.session import SessionManager
from federation_thinking.visualization import ThinkingVisualizer
from federation_thinking.models import Framework, ThoughtType

# Initialize components
config = Config()
memory = ThinkingMemory(config)
session_manager = SessionManager(config, memory)
visualizer = ThinkingVisualizer(config)

server = Server("federation-thinking")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available thinking tools"""
    return [
        Tool(
            name="ft_think",
            description="""Advanced sequential thinking with frameworks and persistence.
            
Enhanced version of sequential thinking that integrates with Federation memory system,
supports multiple thinking frameworks, and enables collaboration between instances.

Key improvements over basic sequential thinking:
- Memory persistence across sessions
- Built-in thinking frameworks (OODA, Socratic, etc.)
- Confidence tracking and evidence support
- Branching and revision capabilities
- Collaborative features for sharing thoughts
- Pattern recognition and analysis
- Visual output generation

Parameters:
- thought: Current thinking step content
- framework: Optional thinking framework to use
- type: Type of thought (analysis, synthesis, hypothesis, etc.)
- confidence: Confidence level (0-1)
- evidence: Supporting evidence or references
- tags: Tags for categorization
- save_to_memory: Auto-save significant thoughts
- share_with: Share with other instances (CC/DT/Trips)
- session_id: Session to add thought to (creates new if not provided)
- is_revision: Whether this revises previous thinking
- revises_thought: ID of thought being revised
- branch_from_thought: ID of thought to branch from
- references: IDs of related thoughts""",
            inputSchema={
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "Current thinking step content"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session ID (optional, creates new session if not provided)"
                    },
                    "framework": {
                        "type": "string",
                        "description": "Thinking framework to use",
                        "enum": ["ooda", "socratic", "first_principles", "five_whys", "swot", "devils_advocate", "lateral", "systems"]
                    },
                    "type": {
                        "type": "string",
                        "description": "Type of thought",
                        "enum": ["observation", "analysis", "synthesis", "hypothesis", "question", "proposal", "decision", "reflection", "revision", "branch"],
                        "default": "analysis"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence level (0-1)",
                        "minimum": 0,
                        "maximum": 1,
                        "default": 0.5
                    },
                    "evidence": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Supporting evidence or references"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for categorization"
                    },
                    "save_to_memory": {
                        "type": "boolean",
                        "description": "Auto-save thought to memory",
                        "default": True
                    },
                    "share_with": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Share with other instances"
                    },
                    "is_revision": {
                        "type": "boolean",
                        "description": "Whether this revises previous thinking",
                        "default": False
                    },
                    "revises_thought": {
                        "type": "string",
                        "description": "ID of thought being revised"
                    },
                    "branch_from_thought": {
                        "type": "string",
                        "description": "ID of thought to branch from"
                    },
                    "references": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "IDs of related thoughts"
                    }
                },
                "required": ["thought"]
            }
        ),
        Tool(
            name="ft_session",
            description="""Manage thinking sessions (start, resume, analyze, share).
            
Provides session management capabilities for organizing thoughts into coherent
thinking sessions with metadata, collaboration features, and analysis tools.

Actions:
- start: Create new thinking session
- resume: Resume paused session
- end: Complete and save session
- analyze: Analyze session patterns and insights
- share: Share session with other instances
- list: List existing sessions

Parameters:
- action: Session action to perform
- session_id: Session identifier (required for resume, end, analyze, share)
- title: Session title (for new sessions)
- context: Task or project context
- framework: Default framework for the session
- task_id: Link to specific task
- project_id: Link to specific project
- share_with: Instances to share with
- message: Message for sharing
- status: Filter by status (for list action)
- limit: Maximum results (for list action)""",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Session action to perform",
                        "enum": ["start", "resume", "end", "analyze", "share", "list"]
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier"
                    },
                    "title": {
                        "type": "string",
                        "description": "Session title (for new sessions)"
                    },
                    "context": {
                        "type": "string",
                        "description": "Task or project context"
                    },
                    "framework": {
                        "type": "string",
                        "description": "Default framework for session",
                        "enum": ["ooda", "socratic", "first_principles", "five_whys", "swot", "devils_advocate", "lateral", "systems"]
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Link to specific task"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Link to specific project"
                    },
                    "share_with": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Instances to share with"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message for sharing"
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by status (for list action)",
                        "enum": ["active", "paused", "completed"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (for list action)",
                        "default": 10
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="ft_visualize",
            description="""Generate visual representations of thinking patterns.
            
Creates various visualizations of thinking sessions including network graphs,
timelines, thought trees, and summary dashboards to help understand thinking
patterns and session evolution.

Visualization formats:
- graph: Network graph showing thought relationships
- timeline: Chronological timeline with confidence evolution
- tree: Hierarchical tree structure of thoughts
- summary: Dashboard with key metrics and distributions

Include options:
- all: Include all thoughts
- thoughts: Include main thoughts only (no revisions)
- branches: Include only branching thoughts
- revisions: Include only revisions

Parameters:
- session_id: Session to visualize
- format: Visualization format
- include: What types of thoughts to include
- output_path: Custom output path (optional)""",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session to visualize"
                    },
                    "format": {
                        "type": "string",
                        "description": "Visualization format",
                        "enum": ["graph", "timeline", "tree", "summary"],
                        "default": "graph"
                    },
                    "include": {
                        "type": "string",
                        "description": "What to include in visualization",
                        "enum": ["all", "thoughts", "branches", "revisions"],
                        "default": "all"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Custom output path (optional)"
                    }
                },
                "required": ["session_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any] | None) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls"""
    if arguments is None:
        arguments = {}
    
    try:
        if name == "ft_think":
            return await handle_ft_think(arguments)
        elif name == "ft_session":
            return await handle_ft_session(arguments)
        elif name == "ft_visualize":
            return await handle_ft_visualize(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]

async def handle_ft_think(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle ft_think tool calls"""
    thought_content = arguments.get("thought", "")
    session_id = arguments.get("session_id")
    framework = arguments.get("framework")
    thought_type = arguments.get("type", "analysis")
    confidence = arguments.get("confidence", 0.5)
    evidence = arguments.get("evidence", [])
    tags = arguments.get("tags", [])
    save_to_memory = arguments.get("save_to_memory", True)
    share_with = arguments.get("share_with", [])
    is_revision = arguments.get("is_revision", False)
    revises_thought = arguments.get("revises_thought")
    branch_from_thought = arguments.get("branch_from_thought")
    references = arguments.get("references", [])
    
    # Get or create session
    if session_id:
        session = session_manager.get_session(session_id)
        if not session:
            return [TextContent(type="text", text=f"Session {session_id} not found")]
    else:
        # Create new session
        session = session_manager.start_session(
            title=f"Thinking Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            framework=framework
        )
        session_id = session.id
    
    # Determine framework step if using a framework
    framework_step = None
    if framework and session.framework:
        framework_config = config.get_framework(framework)
        if framework_config:
            steps = framework_config.get("steps", [])
            # Simple logic to suggest next step
            current_step_count = len([t for t in session.thoughts if t.framework_step])
            if current_step_count < len(steps):
                framework_step = steps[current_step_count]
    
    # Add thought to session
    thought = session_manager.add_thought(
        session_id=session_id,
        content=thought_content,
        thought_type=thought_type,
        framework_step=framework_step,
        confidence=confidence,
        evidence=evidence,
        tags=tags,
        is_revision=is_revision,
        revises_thought=revises_thought,
        branch_from_thought=branch_from_thought,
        references=references
    )
    
    # Handle sharing
    if share_with:
        session_manager.share_session(session_id, share_with, f"New thought added: {thought_content[:100]}")
    
    # Search for related memories
    related_memories = memory.get_related_memories(thought, n_results=3)
    
    # Build response
    response = {
        "thought": {
            "id": thought.id,
            "session_id": session_id,
            "thought_number": thought.thought_number,
            "content": thought.content,
            "type": thought.type,
            "framework": thought.framework,
            "framework_step": thought.framework_step,
            "confidence": thought.confidence,
            "evidence": thought.evidence,
            "tags": thought.tags,
            "timestamp": thought.timestamp.isoformat(),
            "saved_to_memory": thought.saved_to_memory
        },
        "session": {
            "id": session.id,
            "title": session.title,
            "total_thoughts": session.total_thoughts,
            "average_confidence": session.average_confidence,
            "framework": session.framework
        },
        "related_memories": related_memories[:2] if related_memories else [],
        "next_steps": _suggest_next_steps(session, thought)
    }
    
    if framework and framework_config:
        response["framework_guidance"] = {
            "current_step": framework_step,
            "next_step": _get_next_framework_step(framework_config, framework_step),
            "progress": f"{current_step_count + 1}/{len(steps)}"
        }
    
    return [TextContent(type="text", text=json.dumps(response, indent=2))]

async def handle_ft_session(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle ft_session tool calls"""
    action = arguments.get("action", "list")
    session_id = arguments.get("session_id")
    
    try:
        if action == "start":
            title = arguments.get("title", f"New Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            context = arguments.get("context")
            framework = arguments.get("framework")
            task_id = arguments.get("task_id")
            project_id = arguments.get("project_id")
            
            session = session_manager.start_session(
                title=title,
                context=context,
                framework=framework,
                task_id=task_id,
                project_id=project_id
            )
            
            response = {
                "action": "start",
                "session": session.to_dict(),
                "status": "Session started successfully"
            }
            
        elif action == "resume":
            if not session_id:
                return [TextContent(type="text", text="session_id required for resume action")]
            
            session = session_manager.resume_session(session_id)
            response = {
                "action": "resume",
                "session": session.to_dict(),
                "status": "Session resumed successfully"
            }
            
        elif action == "end":
            if not session_id:
                return [TextContent(type="text", text="session_id required for end action")]
            
            session = session_manager.end_session(session_id)
            response = {
                "action": "end",
                "session": session.to_dict(),
                "status": "Session ended and saved to memory"
            }
            
        elif action == "analyze":
            if not session_id:
                return [TextContent(type="text", text="session_id required for analyze action")]
            
            analysis = session_manager.analyze_session(session_id)
            response = {
                "action": "analyze",
                "analysis": analysis
            }
            
        elif action == "share":
            if not session_id:
                return [TextContent(type="text", text="session_id required for share action")]
            
            share_with = arguments.get("share_with", [])
            message = arguments.get("message")
            
            if not share_with:
                return [TextContent(type="text", text="share_with list required for share action")]
            
            result = session_manager.share_session(session_id, share_with, message)
            response = {
                "action": "share",
                "result": result,
                "status": "Session shared successfully"
            }
            
        elif action == "list":
            status = arguments.get("status")
            framework = arguments.get("framework")
            limit = arguments.get("limit", 10)
            
            sessions = session_manager.list_sessions(status, framework, limit)
            response = {
                "action": "list",
                "sessions": sessions,
                "count": len(sessions)
            }
            
        else:
            return [TextContent(type="text", text=f"Unknown action: {action}")]
        
        return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error in {action}: {str(e)}")]

async def handle_ft_visualize(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Handle ft_visualize tool calls"""
    session_id = arguments.get("session_id")
    if not session_id:
        return [TextContent(type="text", text="session_id required for visualization")]
    
    format_type = arguments.get("format", "graph")
    include = arguments.get("include", "all")
    output_path = arguments.get("output_path")
    
    # Get session
    session = session_manager.get_session(session_id)
    if not session:
        return [TextContent(type="text", text=f"Session {session_id} not found")]
    
    try:
        # Override output path if provided
        if output_path:
            original_path = visualizer.output_path
            visualizer.output_path = Path(output_path)
            visualizer.output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate visualization
        result = visualizer.generate_session_graph(session, format_type, include)
        
        # Restore original path
        if output_path:
            visualizer.output_path = original_path
        
        response = {
            "session_id": session_id,
            "visualization": result,
            "session_info": {
                "title": session.title,
                "total_thoughts": session.total_thoughts,
                "status": session.status
            }
        }
        
        return [TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error generating visualization: {str(e)}")]

def _suggest_next_steps(session, current_thought):
    """Suggest next steps based on current thought and session context"""
    suggestions = []
    
    # Framework-based suggestions
    if session.framework and current_thought.framework_step:
        framework_config = config.get_framework(session.framework.value)
        if framework_config:
            steps = framework_config.get("steps", [])
            current_index = steps.index(current_thought.framework_step) if current_thought.framework_step in steps else -1
            if current_index < len(steps) - 1:
                next_step = steps[current_index + 1]
                suggestions.append(f"Continue with {session.framework.value} framework: {next_step}")
    
    # Confidence-based suggestions
    if current_thought.confidence < 0.5:
        suggestions.append("Consider gathering more evidence to increase confidence")
    elif current_thought.confidence > 0.8:
        suggestions.append("High confidence thought - consider testing or implementing")
    
    # Type-based suggestions
    if current_thought.type == ThoughtType.HYPOTHESIS:
        suggestions.append("Design experiments or gather evidence to test this hypothesis")
    elif current_thought.type == ThoughtType.QUESTION:
        suggestions.append("Research or analyze to answer this question")
    elif current_thought.type == ThoughtType.PROPOSAL:
        suggestions.append("Evaluate pros/cons or seek feedback on this proposal")
    
    return suggestions[:3]  # Limit to top 3 suggestions

def _get_next_framework_step(framework_config, current_step):
    """Get the next step in a framework"""
    steps = framework_config.get("steps", [])
    if not current_step or current_step not in steps:
        return steps[0] if steps else None
    
    current_index = steps.index(current_step)
    if current_index < len(steps) - 1:
        return steps[current_index + 1]
    elif framework_config.get("cycle", False):
        return steps[0]  # Cycle back to beginning
    else:
        return None  # Framework complete

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="federation-thinking",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())