"""
Message flow hooks for auto-summary system
Integrates with MCP message handling
"""
from datetime import datetime
from typing import Dict, Any, Optional


class MessageFlowHooks:
    """Hooks for capturing conversation flow"""
    
    def __init__(self, integration):
        self.integration = integration
        self.enabled = True
    
    def capture_tool_call(self, tool_name: str, arguments: Dict[str, Any], result: str):
        """Capture tool calls for context"""
        if not self.enabled:
            return
        
        # Build message content
        content = f"Tool: {tool_name}\n"
        
        # Add key arguments (not full content to avoid bloat)
        if tool_name == "cc_remember":
            content += f"Storing memory: {arguments.get('content', '')[:100]}..."
        elif tool_name == "cc_create_note":
            content += f"Creating note: {arguments.get('title', 'Untitled')}"
        elif tool_name == "cc_search_notes":
            content += f"Searching for: {arguments.get('query', '')}"
        else:
            # Generic argument capture
            arg_str = ", ".join(f"{k}={v}" for k, v in list(arguments.items())[:3])
            content += f"Args: {arg_str}"
        
        # Add result preview
        if isinstance(result, str):
            content += f"\nResult: {result[:100]}..."
        
        # Buffer the message
        self.integration.buffer_conversation(content, role="assistant")
    
    def capture_user_message(self, message: str):
        """Capture user messages"""
        if not self.enabled and message:
            return
        
        self.integration.buffer_conversation(message, role="user")
    
    def capture_response(self, response: str):
        """Capture assistant responses"""
        if not self.enabled and response:
            return
            
        self.integration.buffer_conversation(response, role="assistant")
    
    def check_daily_note(self):
        """Check if we need a new daily note"""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_note_title = f"{today} Daily Summary"
        
        # Check if today's note exists
        existing = self.integration.vault.read_note(daily_note_title, "📅 Daily_Notes")
        
        if not existing:
            # Create new daily note
            events = []
            
            # Add startup event
            events.append({
                "time": datetime.now().strftime("%H:%M"),
                "description": "Session started",
                "details": "Beginning new day with Nerve Center active"
            })
            
            # Create the note
            self.integration.vault.create_daily_note(
                summary="New day begins. Nerve Center operational.",
                events=events
            )
            
            return True
        return False
    
    def trigger_summary_if_needed(self, force: bool = False):
        """Check and trigger auto-summary if needed"""
        if force or self.integration._should_summarize():
            return self.integration.create_auto_summary()
        return None