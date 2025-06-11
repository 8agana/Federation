#!/usr/bin/env python3
"""
DT Federation Memory MCP Server
Exposes DT's federation memory operations as MCP tools

This is a thin wrapper around the federation bridge layer.
All business logic remains in Layer 2 (bridge scripts).
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import json
import logging
from datetime import datetime

# Add bridge scripts to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "2_BridgeScripts"))
from federation.dt_federation_bridge import DTFederationBridge
from federation.shared_federation_bridge import SharedFederationBridge

# Knowledge graph removed - replaced with Obsidian in CC
# DT will get Obsidian access when ready

# Import MCP SDK
try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
except ImportError:
    print("ERROR: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("dt_federation_mcp")

# Initialize MCP server
server = Server("dt-federation-memory")

# Initialize bridges (will be done on first use)
bridge: Optional[DTFederationBridge] = None
shared_bridge: Optional[SharedFederationBridge] = None

# Auto-summary conversation tracking
conversation_buffer = []
last_summary_time = datetime.now()
current_context = {"task": None, "topic": None}
message_count = 0  # Track message exchanges
MESSAGE_THRESHOLD = 5  # DT needs 5 messages for auto-summary

# Store actual conversation content
conversation_messages = []



def get_bridge() -> DTFederationBridge:
    """Get or initialize the DT federation bridge"""
    global bridge
    if bridge is None:
        try:
            bridge = DTFederationBridge()
            logger.info("DT Federation Bridge initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize bridge: {e}")
            raise
    return bridge


def get_shared_bridge() -> SharedFederationBridge:
    """Get or initialize the shared federation bridge"""
    global shared_bridge
    if shared_bridge is None:
        try:
            shared_bridge = SharedFederationBridge()
            logger.info("Shared Federation Bridge initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize shared bridge: {e}")
            raise
    return shared_bridge

# Auto-summary functions
def track_conversation(tool_name: str, arguments: dict, result: str):
    """Track tool usage for auto-summary"""
    global conversation_buffer, current_context, message_count
    
    logger.info(f"DEBUG: track_conversation called for {tool_name}")
    logger.info(f"DEBUG: Current buffer size before: {len(conversation_buffer)}")
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "arguments": arguments,
        "result": result[:200]  # Limit result size
    }
    
    conversation_buffer.append(entry)
    logger.info(f"DEBUG: Buffer size after append: {len(conversation_buffer)}")
    
    # Increment message count (each tool use represents part of a message exchange)
    # We'll count significant tools as representing a message
    significant_tools = ["dt_remember", "dt_recall", "dt_update_memory", "dt_search_by_tags", 
                        "dt_federation_search", "dt_search_cc"]
    if tool_name in significant_tools:
        message_count += 1
        logger.info(f"Message count: {message_count}/{MESSAGE_THRESHOLD}")
    
    logger.info(f"Tracked conversation: {tool_name} (buffer size: {len(conversation_buffer)})")

def track_message_content(user_message: str = None, assistant_response: str = None):
    """Track actual conversation content for meaningful summaries"""
    global conversation_messages, message_count
    
    if user_message or assistant_response:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message[:500] if user_message else None,  # Limit size
            "assistant": assistant_response[:500] if assistant_response else None,
            "message_number": len(conversation_messages) + 1
        }
        conversation_messages.append(entry)
        
        # Count this as a message exchange if we have both parts
        if user_message and assistant_response:
            message_count += 1
            logger.info(f"Message exchange tracked: {message_count}/{MESSAGE_THRESHOLD}")

def detect_context_switch(new_context: str) -> bool:
    """Detect if we've switched to a different topic/task"""
    global current_context
    
    if not current_context.get("task"):
        return False
    
    # Simple keyword-based detection
    old_task = current_context["task"].lower()
    new_task = new_context.lower()
    
    # Define context switch indicators
    switch_keywords = [
        "switch to", "moving to", "now let's", "different topic", 
        "new task", "change to", "instead", "pivot to"
    ]
    
    # Check for explicit switch indicators
    for keyword in switch_keywords:
        if keyword in new_task:
            return True
    
    # Check for topic change (simple word overlap analysis)
    old_words = set(old_task.split())
    new_words = set(new_task.split())
    
    # If less than 20% word overlap, likely a context switch
    if old_words and new_words:
        overlap = len(old_words.intersection(new_words))
        total_unique = len(old_words.union(new_words))
        if overlap / total_unique < 0.2:
            return True
    
    return False

def get_active_tasks():
    """Get list of active tasks from SharedVault"""
    try:
        # This would need integration with Obsidian or file system
        # For now, return a placeholder
        return ["2 - Implement Auto-Summary System", "Other active tasks"]
    except Exception as e:
        logger.error(f"Failed to get active tasks: {e}")
        return []

def should_create_summary() -> bool:
    """Check if it's time to create a summary"""
    global message_count
    
    # Message count trigger (5 messages for DT)
    if message_count >= MESSAGE_THRESHOLD:
        return True
    
    return False

def generate_summary() -> str:
    """Generate a summary from the conversation buffer and messages"""
    global conversation_buffer, current_context, conversation_messages
    
    if not conversation_buffer and not conversation_messages:
        return None
    
    # Build summary
    summary_parts = [
        f"## Auto-Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Messages Exchanged**: {message_count}",
        f"**Total Operations**: {len(conversation_buffer)}",
        ""
    ]
    
    # Current context and task linking
    if current_context.get("task"):
        summary_parts.append(f"**Context**: {current_context['task']}")
        
        # Try to identify related active tasks
        active_tasks = get_active_tasks()
        if active_tasks:
            # Simple matching - look for task keywords in context
            related_tasks = []
            context_lower = current_context['task'].lower()
            for task in active_tasks:
                # Extract task keywords
                task_keywords = task.lower().split()
                if any(keyword in context_lower for keyword in task_keywords if len(keyword) > 3):
                    related_tasks.append(task)
            
            if related_tasks:
                summary_parts.append(f"**Related Tasks**: {', '.join(related_tasks)}")
        
        summary_parts.append("")
    
    # Conversation content (if available)
    if conversation_messages:
        summary_parts.append("### Conversation Highlights")
        # Get the most recent meaningful exchanges
        recent_messages = conversation_messages[-3:] if len(conversation_messages) > 3 else conversation_messages
        for msg in recent_messages:
            if msg.get("user") and len(msg["user"]) > 10:  # Skip very short messages
                summary_parts.append(f"**User**: {msg['user']}")
            if msg.get("assistant") and len(msg["assistant"]) > 10:
                summary_parts.append(f"**Assistant**: {msg['assistant']}")
            summary_parts.append("")
    
    # Enhanced content analysis - identify key themes
    if conversation_messages:
        all_content = " ".join([
            msg.get("user", "") + " " + msg.get("assistant", "") 
            for msg in conversation_messages
        ]).lower()
        
        # Look for key patterns
        key_themes = []
        theme_patterns = {
            "implementation": ["implement", "build", "create", "develop"],
            "problem-solving": ["problem", "issue", "fix", "solve", "error"],
            "planning": ["plan", "design", "architecture", "approach"],
            "testing": ["test", "verify", "check", "validate"],
            "decision": ["decide", "choose", "prefer", "option"]
        }
        
        for theme, keywords in theme_patterns.items():
            if any(keyword in all_content for keyword in keywords):
                key_themes.append(theme)
        
        if key_themes:
            summary_parts.append(f"**Key Themes**: {', '.join(key_themes)}")
            summary_parts.append("")
    
    # Memory operations for context
    memory_ops = [e for e in conversation_buffer if e["tool"] in ["dt_remember", "dt_recall", "dt_update_memory"]]
    if memory_ops:
        summary_parts.append("### Key Memory Operations")
        for entry in memory_ops[-3:]:  # Last 3 operations
            if entry["tool"] == "dt_remember":
                title = entry["arguments"].get("title", "")
                content_preview = entry["arguments"].get("content", "")[:80]
                if title:
                    summary_parts.append(f"- **Stored** '{title}': {content_preview}...")
                else:
                    summary_parts.append(f"- **Stored**: {content_preview}...")
            elif entry["tool"] == "dt_recall":
                query = entry["arguments"].get("query", "")
                summary_parts.append(f"- **Searched**: {query}")
            elif entry["tool"] == "dt_update_memory":
                memory_id = entry["arguments"].get("memory_id", "")
                summary_parts.append(f"- **Updated**: {memory_id}")
    
    # Next steps inference
    if conversation_messages:
        last_message = conversation_messages[-1]
        assistant_msg = last_message.get("assistant", "").lower()
        
        next_steps = []
        if "implement" in assistant_msg or "add" in assistant_msg:
            next_steps.append("Continue implementation")
        if "test" in assistant_msg:
            next_steps.append("Test changes")
        if "phase" in assistant_msg:
            next_steps.append("Move to next phase")
        
        if next_steps:
            summary_parts.append(f"\n**Likely Next Steps**: {', '.join(next_steps)}")
    
    return "\n".join(summary_parts)

def clear_conversation_buffer():
    """Clear the conversation buffer after summary"""
    global conversation_buffer, last_summary_time, message_count, conversation_messages
    conversation_buffer = []
    conversation_messages = []
    last_summary_time = datetime.now()
    message_count = 0
    logger.info("Conversation buffer cleared")




# Tool definitions
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available DT federation memory tools"""
    return [
        types.Tool(
            name="dt_remember",
            description="Store a memory in DT's federation database",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The memory content to store"},
                    "title": {"type": "string", "description": "Optional title for the memory"},
                    "tags": {
                        "oneOf": [
                            {"type": "string", "description": "Comma-separated tags"},
                            {"type": "array", "items": {"type": "string"}, "description": "Array of tags"}
                        ]
                    },
                    "metadata": {"type": "object", "description": "Optional metadata dict"}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="dt_recall",
            description="Search DT's memories with natural language time parsing",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (may include time expressions)"},
                    "n_results": {"type": "integer", "description": "Maximum number of results (default: 5)"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="dt_update_memory",
            description="Update an existing memory (living documents)",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {"type": "string", "description": "ID of memory to update"},
                    "content": {"type": "string", "description": "New content (optional)"},
                    "metadata": {"type": "object", "description": "Metadata updates (optional)"},
                    "version_comment": {"type": "string", "description": "Comment about the update"}
                },
                "required": ["memory_id"]
            }
        ),
        types.Tool(
            name="dt_search_by_tags",
            description="Search memories by tags (OR logic)",
            inputSchema={
                "type": "object",
                "properties": {
                    "tags": {
                        "oneOf": [
                            {"type": "string", "description": "Tag to search for"},
                            {"type": "array", "items": {"type": "string"}, "description": "Tags to search for"}
                        ]
                    },
                    "n_results": {"type": "integer", "description": "Maximum results (default: 10)"}
                },
                "required": ["tags"]
            }
        ),
        types.Tool(
            name="dt_health_check",
            description="Check DT federation memory system health",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="dt_memory_stats",
            description="Get DT memory system statistics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="dt_search_cc",
            description="Search ONLY CC's memories (respecting privacy)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "n_results": {"type": "integer", "description": "Maximum results (default: 10)"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="dt_federation_search",
            description="Search across BOTH DT and CC memories",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "n_results": {"type": "integer", "description": "Maximum results per instance (default: 10)"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="dt_auto_summary",
            description="Create auto-summary of recent conversation",
            inputSchema={
                "type": "object",
                "properties": {
                    "force": {"type": "boolean", "description": "Force summary even if triggers not met", "default": False},
                    "save_to_memory": {"type": "boolean", "description": "Save summary to ChromaDB", "default": True}
                }
            }
        ),
        types.Tool(
            name="dt_track_conversation",
            description="Track conversation content for auto-summary",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_message": {"type": "string", "description": "User's message content"},
                    "assistant_response": {"type": "string", "description": "Assistant's response content"},
                    "context": {"type": "string", "description": "Current task or topic context"}
                }
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    """Handle tool calls"""
    
    result = []  # Initialize as empty list instead of None
    try:
        if name == "dt_remember":
            bridge = get_bridge()
            memory_id = bridge.remember(
                content=arguments["content"],
                title=arguments.get("title"),
                tags=arguments.get("tags"),
                metadata=arguments.get("metadata")
            )
            
            # Check for duplicate
            if memory_id.startswith("DUPLICATE:"):
                result = [types.TextContent(
                    type="text",
                    text=f"Duplicate content detected. Existing ID: {memory_id.replace('DUPLICATE:', '')}"
                )]
            else:
                result = [types.TextContent(
                    type="text",
                    text=f"Memory stored successfully: {memory_id}"
                )]
            
        elif name == "dt_recall":
            bridge = get_bridge()
            memories = bridge.recall(
                query=arguments["query"],
                n_results=arguments.get("n_results", 5)
            )
            
            if not memories:
                result = [types.TextContent(
                    type="text",
                    text="No memories found matching your query."
                )]
            else:
                # Format results
                results = []
                for i, memory in enumerate(memories):
                    metadata = memory.get('metadata', {})
                    results.append(f"{i+1}. [{memory['id']}]")
                    if metadata.get('title'):
                        results.append(f"   Title: {metadata['title']}")
                    results.append(f"   Content: {memory['content'][:200]}...")
                    if metadata.get('tags'):
                        results.append(f"   Tags: {metadata['tags']}")
                    results.append(f"   Relevance: {memory.get('relevance_score', 0):.2f}")
                    results.append("")
                
                result = [types.TextContent(
                    type="text",
                    text=f"Found {len(memories)} memories:\n\n" + "\n".join(results)
                )]
            
        elif name == "dt_update_memory":
            bridge = get_bridge()
            update_success = bridge.update_memory(
                memory_id=arguments["memory_id"],
                content=arguments.get("content"),
                metadata=arguments.get("metadata"),
                version_comment=arguments.get("version_comment")
            )
            
            if update_success:
                result = [types.TextContent(
                    type="text",
                    text=f"Memory {arguments['memory_id']} updated successfully"
                )]
            else:
                result = [types.TextContent(
                    type="text",
                    text=f"Failed to update memory {arguments['memory_id']} - not found"
                )]
                
        elif name == "dt_search_by_tags":
            bridge = get_bridge()
            memories = bridge.search_by_tags(
                tags=arguments["tags"],
                n_results=arguments.get("n_results", 10)
            )
            
            if not memories:
                result = [types.TextContent(
                    type="text",
                    text="No memories found with those tags."
                )]
            else:
                # Format results
                results = []
                for i, memory in enumerate(memories):
                    results.append(f"{i+1}. [{memory['id']}]")
                    results.append(f"   Content: {memory['content'][:200]}...")
                    results.append(f"   Tags: {', '.join(memory.get('tags', []))}")
                    results.append("")
                
                result = [types.TextContent(
                    type="text",
                    text=f"Found {len(memories)} memories with tags:\n\n" + "\n".join(results)
                )]
            
        elif name == "dt_health_check":
            bridge = get_bridge()
            health_data = bridge.health_check()
            
            result = [types.TextContent(
                type="text",
                text=f"DT Federation Memory Health:\n"
                     f"Status: {health_data['status']}\n"
                     f"Total Memories: {health_data['total_memories']}\n"
                     f"Recent (24h): {health_data['recent_24h']}\n"
                     f"Health Score: {health_data['health_score']:.2f}\n"
                     f"Duplicates: {health_data['duplicates_found']}"
            )]
            
        elif name == "dt_memory_stats":
            bridge = get_bridge()
            stats_data = bridge.get_memory_stats()
            
            result = [types.TextContent(
                type="text",
                text=f"DT Memory Statistics:\n"
                     f"Total: {stats_data['total_memories']}\n"
                     f"Recent: {stats_data['recent_24h']}\n"
                     f"Health: {stats_data['health_status']}\n"
                     f"Domains: {json.dumps(stats_data.get('domain_stats', {}), indent=2)}"
            )]
            
        elif name == "dt_search_cc":
            shared = get_shared_bridge()
            memories = shared.search_other_instance(
                query=arguments["query"],
                from_instance='dt',
                n_results=arguments.get("n_results", 10)
            )
            
            if not memories:
                result = [types.TextContent(
                    type="text",
                    text="No memories found in CC's database."
                )]
            else:
                # Format results
                results = []
                for i, memory in enumerate(memories):
                    metadata = memory.get('metadata', {})
                    results.append(f"{i+1}. [CC: {memory['id']}]")
                    if metadata.get('title'):
                        results.append(f"   Title: {metadata['title']}")
                    results.append(f"   Content: {memory['content'][:200]}...")
                    results.append("")
                
                result = [types.TextContent(
                    type="text",
                    text=f"Found {len(memories)} memories from CC:\n\n" + "\n".join(results)
                )]
            
        elif name == "dt_federation_search":
            shared = get_shared_bridge()
            fed_results = shared.federation_search(
                query=arguments["query"],
                instances=['cc', 'dt'],
                n_results=arguments.get("n_results", 10)
            )
            
            total = fed_results['total_found']
            if total == 0:
                result = [types.TextContent(
                    type="text",
                    text="No memories found across the federation."
                )]
            else:
                # Format results by instance
                output = [f"Found {total} total memories across federation:\n"]
                
                for instance, data in fed_results['results'].items():
                    if data['status'] == 'success' and data['count'] > 0:
                        output.append(f"\n{instance.upper()} ({data['count']} memories):")
                        for i, memory in enumerate(data['memories'][:5]):  # Show first 5
                            metadata = memory.get('metadata', {})
                            output.append(f"  {i+1}. [{memory['id']}]")
                            if metadata.get('title'):
                                output.append(f"     Title: {metadata['title']}")
                            output.append(f"     Content: {memory['content'][:150]}...")
                
                result = [types.TextContent(
                    type="text",
                    text="\n".join(output)
                )]
        
            
        elif name == "dt_auto_summary":
            force = arguments.get("force", False)
            save_to_memory = arguments.get("save_to_memory", True)
            
            # Check if summary is needed or forced
            if not force and not should_create_summary():
                result = [types.TextContent(
                    type="text",
                    text=f"ℹ️ Not time for summary yet\nMessages: {message_count}/{MESSAGE_THRESHOLD}\nOperations tracked: {len(conversation_buffer)}"
                )]
            else:
                # Generate summary
                summary = generate_summary()
                if not summary:
                    result = [types.TextContent(
                        type="text",
                        text="❌ No conversation data to summarize"
                    )]
                else:
                    results = []
                    
                    # Save to memory
                    if save_to_memory:
                        bridge = get_bridge()
                        memory_id = bridge.remember(
                            content=summary,
                            title=f"Auto-Summary {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                            tags=["auto-summary", "context"],
                            metadata={"created_by": "auto_summary", "message_count": message_count, "operation_count": len(conversation_buffer)}
                        )
                        results.append(f"💾 Saved to memory: {memory_id}")
                    
                    # Clear buffer
                    clear_conversation_buffer()
                    
                    result = [types.TextContent(
                        type="text",
                        text=f"✅ Auto-summary created\n" + "\n".join(results) + f"\n\nSummary:\n{summary}"
                    )]
        
        elif name == "dt_track_conversation":
            user_msg = arguments.get("user_message")
            assistant_msg = arguments.get("assistant_response")
            context = arguments.get("context")
            
            # Detect context switch before updating
            context_switched = False
            if context and detect_context_switch(context):
                context_switched = True
                logger.info(f"Context switch detected: {current_context.get('task')} → {context}")
                
                # Auto-trigger summary on context switch
                if len(conversation_buffer) > 0 or len(conversation_messages) > 0:
                    try:
                        summary = generate_summary()
                        if summary:
                            bridge = get_bridge()
                            memory_id = bridge.remember(
                                content=summary,
                                title=f"Context Switch Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                                tags=["auto-summary", "context-switch", "automatic"],
                                metadata={"created_by": "context_switch", "old_context": current_context.get('task'), "new_context": context}
                            )
                            logger.info(f"Context switch summary saved: {memory_id}")
                            clear_conversation_buffer()
                    except Exception as e:
                        logger.error(f"Failed to create context switch summary: {e}")
            
            # Update current context if provided
            if context:
                current_context["task"] = context
            
            # Track the conversation content
            track_message_content(user_msg, assistant_msg)
            
            response_parts = [f"✅ Conversation tracked. Messages: {len(conversation_messages)}, Context: {current_context.get('task', 'None')}"]
            if context_switched:
                response_parts.append("🔄 Context switch detected - summary created")
            
            result = [types.TextContent(
                type="text",
                text="\n".join(response_parts)
            )]
        
        else:
            result = [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
        
        # Track conversation for all tools except auto_summary itself
        logger.info(f"DEBUG: About to check tracking for tool {name}, result type: {type(result)}, result length: {len(result) if result else 'None'}")
        if name != "dt_auto_summary" and result and len(result) > 0:
            result_text = result[0].text if isinstance(result[0], types.TextContent) else str(result)
            logger.info(f"DEBUG: Calling track_conversation for {name} with result_text: {result_text[:50]}...")
            track_conversation(name, arguments, result_text)
            
            # Check if we should trigger auto-summary
            if should_create_summary():
                logger.info("Auto-summary trigger detected! Creating automatic summary...")
                try:
                    # Generate and save automatic summary
                    summary = generate_summary()
                    if summary:
                        bridge = get_bridge()
                        memory_id = bridge.remember(
                            content=summary,
                            title=f"Auto-Summary {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                            tags=["auto-summary", "context", "automatic"],
                            metadata={"created_by": "auto_trigger", "message_count": message_count, "operation_count": len(conversation_buffer)}
                        )
                        logger.info(f"Automatic summary saved: {memory_id}")
                        
                        # Clear buffer after automatic summary
                        clear_conversation_buffer()
                    else:
                        logger.warning("Auto-summary triggered but no content to summarize")
                except Exception as e:
                    logger.error(f"Failed to create automatic summary: {e}")
        
        return result
            
    except Exception as e:
        logger.error(f"Tool {name} error: {e}", exc_info=True)
        result = [types.TextContent(
            type="text",
            text=f"Error in {name}: {str(e)}"
        )]
    
    # Return result after tracking
    return result


# Main entry point
async def main():
    """Run the DT Federation Memory MCP server"""
    logger.info("Starting DT Federation Memory MCP Server")
    
    try:
        # Run the server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="dt-federation-memory",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    )
                )
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())