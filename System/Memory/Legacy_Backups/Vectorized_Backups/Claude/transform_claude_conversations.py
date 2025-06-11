import json
import datetime
import time
import os
import sys
from dateutil import parser

# Load the JSON files
with open('/home/ubuntu/upload/conversations.json', 'r') as f:
    conversations = json.load(f)

with open('/home/ubuntu/upload/ideas.json', 'r') as f:
    ideas_template = json.load(f)

# Function to convert ISO timestamp to ISO format (standardized)
def standardize_timestamp(timestamp_str):
    if not timestamp_str:
        return datetime.datetime.now().isoformat()
    try:
        # Parse the timestamp string to a datetime object
        dt = parser.parse(timestamp_str)
        # Return the ISO format
        return dt.isoformat()
    except Exception as e:
        print(f"Error parsing timestamp {timestamp_str}: {e}")
        return datetime.datetime.now().isoformat()

# Function to extract meaningful content from a Claude conversation
def extract_conversation_content(conversation):
    chat_messages = conversation.get('chat_messages', [])
    
    # Extract meaningful messages (user and assistant)
    messages = []
    
    for message in chat_messages:
        sender = message.get('sender')
        
        # Only include user and assistant messages
        if sender in ['human', 'assistant']:
            # Extract text from content array
            message_text = ""
            content_array = message.get('content', [])
            
            for content_item in content_array:
                if content_item.get('type') == 'text':
                    text = content_item.get('text', '')
                    if text:  # Skip empty text
                        message_text += text
            
            # If message has text content, add to messages list
            if message_text:
                messages.append({
                    'role': 'user' if sender == 'human' else 'assistant',
                    'content': message_text,
                    'created_at': message.get('created_at')
                })
    
    # Format the content
    formatted_content = ""
    for msg in messages:
        role_prefix = "User: " if msg['role'] == 'user' else "Assistant: "
        content_snippet = msg['content']
        
        # Truncate very long messages for readability
        if len(content_snippet) > 500:
            content_snippet = content_snippet[:497] + "..."
            
        formatted_content += f"{role_prefix}{content_snippet}\n\n"
    
    return formatted_content.strip()

# Function to extract tags from conversation content
def extract_tags(conversation, content):
    tags = ["claude_conversation"]
    
    # Add uuid-based tag
    uuid = conversation.get('uuid', '').lower()
    if uuid:
        tags.append(f"uuid_{uuid[:8]}")
    
    # Look for common themes in content
    if "memory" in content.lower():
        tags.append("memory")
    if "project" in content.lower():
        tags.append("project")
    if "json" in content.lower():
        tags.append("json")
    if "claude" in content.lower():
        tags.append("claude")
    
    return tags

# Sort conversations by most recent first
conversations.sort(key=lambda x: x.get('updated_at', '') if x.get('updated_at') else x.get('created_at', ''), reverse=True)

# Create output directory if it doesn't exist
output_dir = '/home/ubuntu/claude_output'
os.makedirs(output_dir, exist_ok=True)

# Initialize variables for file splitting
file_counter = 1
current_file_size = 0
max_file_size = 150 * 1024  # 150 KB in bytes
current_conversations = []

# Process all conversations
for conversation in conversations:
    # Extract content
    content = extract_conversation_content(conversation)
    
    # Skip conversations with no meaningful content
    if not content or content == "No content found":
        continue
    
    # Create entry
    entry = {
        "key": f"claude_conversation.{conversation.get('uuid', 'unknown')[:8]}",
        "value": content,
        "timestamp": standardize_timestamp(conversation.get('created_at')),
        "status": "archived",
        "tags": extract_tags(conversation, content)
    }
    
    # Estimate entry size in bytes
    entry_size = sys.getsizeof(json.dumps(entry))
    
    # Check if adding this entry would exceed the file size limit
    if current_file_size + entry_size > max_file_size and current_conversations:
        # Save current batch to file
        transformed_data = {
            "metadata": {
                "source": f"claude_conversations_part_{file_counter}.json",
                "schema_version": "1.0",
                "last_updated": datetime.datetime.now().isoformat(),
                "tags": [
                    "claude",
                    "conversations",
                    "transformed",
                    "llm_readable"
                ],
                "item_count": len(current_conversations)
            },
            "conversations": current_conversations
        }
        
        output_path = os.path.join(output_dir, f"claude_conversations_part_{file_counter}.json")
        with open(output_path, 'w') as f:
            json.dump(transformed_data, f, indent=2)
        
        print(f"Part {file_counter} saved with {len(current_conversations)} conversations, size: {current_file_size / 1024:.2f} KB")
        
        # Reset for next file
        file_counter += 1
        current_file_size = entry_size
        current_conversations = [entry]
    else:
        # Add entry to current batch
        current_conversations.append(entry)
        current_file_size += entry_size

# Save any remaining conversations
if current_conversations:
    transformed_data = {
        "metadata": {
            "source": f"claude_conversations_part_{file_counter}.json",
            "schema_version": "1.0",
            "last_updated": datetime.datetime.now().isoformat(),
            "tags": [
                "claude",
                "conversations",
                "transformed",
                "llm_readable"
            ],
            "item_count": len(current_conversations)
        },
        "conversations": current_conversations
    }
    
    output_path = os.path.join(output_dir, f"claude_conversations_part_{file_counter}.json")
    with open(output_path, 'w') as f:
        json.dump(transformed_data, f, indent=2)
    
    print(f"Part {file_counter} saved with {len(current_conversations)} conversations, size: {current_file_size / 1024:.2f} KB")

print(f"Transformation complete. {file_counter} files created in {output_dir}")
