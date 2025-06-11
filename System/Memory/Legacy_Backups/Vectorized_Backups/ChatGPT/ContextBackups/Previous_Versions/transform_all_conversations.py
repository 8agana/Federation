import json
import datetime
import time
import os
import sys

# Load the JSON files
with open('/home/ubuntu/upload/conversations.json', 'r') as f:
    conversations = json.load(f)

with open('/home/ubuntu/upload/ideas.json', 'r') as f:
    ideas_template = json.load(f)

# Function to convert epoch time to ISO format
def epoch_to_iso(epoch_time):
    if epoch_time is None:
        return datetime.datetime.now().isoformat()
    return datetime.datetime.fromtimestamp(epoch_time).isoformat()

# Function to extract meaningful content from a conversation
def extract_conversation_content(conversation):
    mapping = conversation.get('mapping', {})
    
    # Find the root message
    root_id = None
    for node_id, node in mapping.items():
        if node.get('parent') is None or node.get('parent') == '':
            root_id = node_id
            break
    
    if not root_id:
        return "No content found"
    
    # Extract meaningful messages (user and assistant)
    messages = []
    
    # BFS traversal to get messages in order
    queue = [root_id]
    visited = set()
    
    while queue:
        current_id = queue.pop(0)
        if current_id in visited:
            continue
            
        visited.add(current_id)
        node = mapping.get(current_id)
        
        if not node:
            continue
            
        message_data = node.get('message')
        if message_data:
            author_role = message_data.get('author', {}).get('role')
            
            # Only include user and assistant messages
            if author_role in ['user', 'assistant']:
                content_parts = message_data.get('content', {}).get('parts', [])
                if content_parts and content_parts[0]:  # Skip empty messages
                    messages.append({
                        'role': author_role,
                        'content': content_parts[0],
                        'create_time': message_data.get('create_time')
                    })
        
        # Add children to queue
        children = node.get('children', [])
        queue.extend(children)
    
    # Format the content
    formatted_content = ""
    for msg in messages:
        if msg['content']:
            role_prefix = "User: " if msg['role'] == 'user' else "Assistant: "
            content_snippet = msg['content']
            
            # Truncate very long messages for readability
            if len(content_snippet) > 500:
                content_snippet = content_snippet[:497] + "..."
                
            formatted_content += f"{role_prefix}{content_snippet}\n\n"
    
    return formatted_content.strip()

# Function to extract tags from conversation content
def extract_tags(conversation, content):
    tags = ["conversation"]
    
    # Add title-based tag
    title = conversation.get('title', '').lower()
    if title:
        # Convert title to tag format (lowercase, underscores)
        title_tag = title.replace(' ', '_').lower()
        tags.append(title_tag)
    
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
conversations.sort(key=lambda x: x.get('update_time', 0) if x.get('update_time') else x.get('create_time', 0), reverse=True)

# Create output directory if it doesn't exist
output_dir = '/home/ubuntu/output'
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
    
    # Create entry
    entry = {
        "key": f"conversation.{conversation.get('title', 'untitled').lower().replace(' ', '_')}",
        "value": content,
        "timestamp": epoch_to_iso(conversation.get('create_time')),
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
                "source": f"transformed_conversations_part_{file_counter}.json",
                "schema_version": "1.0",
                "last_updated": datetime.datetime.now().isoformat(),
                "tags": [
                    "conversations",
                    "transformed",
                    "llm_readable"
                ],
                "item_count": len(current_conversations)
            },
            "conversations": current_conversations
        }
        
        output_path = os.path.join(output_dir, f"transformed_conversations_part_{file_counter}.json")
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
            "source": f"transformed_conversations_part_{file_counter}.json",
            "schema_version": "1.0",
            "last_updated": datetime.datetime.now().isoformat(),
            "tags": [
                "conversations",
                "transformed",
                "llm_readable"
            ],
            "item_count": len(current_conversations)
        },
        "conversations": current_conversations
    }
    
    output_path = os.path.join(output_dir, f"transformed_conversations_part_{file_counter}.json")
    with open(output_path, 'w') as f:
        json.dump(transformed_data, f, indent=2)
    
    print(f"Part {file_counter} saved with {len(current_conversations)} conversations, size: {current_file_size / 1024:.2f} KB")

print(f"Transformation complete. {file_counter} files created in {output_dir}")
