import json
import datetime
import time
import os
import sys
import hashlib
import re

# Create output directory if it doesn't exist
output_dir = '/home/ubuntu/combined_output'
os.makedirs(output_dir, exist_ok=True)

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
            
            # Add the formatted message to the content
            formatted_content += f"{role_prefix}{content_snippet}\n\n"
    
    return formatted_content.strip()

# Function to extract tags from conversation content
def extract_tags(conversation, content):
    tags = ["conversation", "chatgpt"]
    
    # Add title-based tag
    title = conversation.get('title', '').lower()
    if title:
        # Convert title to tag format (lowercase, underscores)
        title_tag = title.replace(' ', '_').lower()
        tags.append(title_tag)
    
    # Look for common themes in content
    content_lower = content.lower()
    if "memory" in content_lower:
        tags.append("memory")
    if "project" in content_lower:
        tags.append("project")
    if "json" in content_lower:
        tags.append("json")
    if "claude" in content_lower:
        tags.append("claude")
    if "ai" in content_lower or "artificial intelligence" in content_lower:
        tags.append("ai")
    if "ethics" in content_lower:
        tags.append("ethics")
    if "philosophy" in content_lower:
        tags.append("philosophy")
    if "code" in content_lower or "programming" in content_lower or "python" in content_lower:
        tags.append("programming")
    if "law" in content_lower or "legal" in content_lower:
        tags.append("law")
    if "physics" in content_lower:
        tags.append("physics")
    
    return tags

# Process all uploaded files
all_conversations = []
processed_hashes = set()  # To track duplicates
file_count = 0
total_conversations = 0
successful_files = 0

# Get all JSON files in the upload directory
json_files = [f for f in os.listdir('/home/ubuntu/upload/') if f.endswith('_conversations.json')]

print(f"Found {len(json_files)} JSON files to process")

# Process each JSON file
for json_file in json_files:
    file_path = os.path.join('/home/ubuntu/upload/', json_file)
    file_count += 1
    
    print(f"Processing file {file_count}/{len(json_files)}: {json_file}")
    
    try:
        with open(file_path, 'r') as f:
            conversations = json.load(f)
            
            file_conversation_count = 0
            
            # Process each conversation
            for conversation in conversations:
                total_conversations += 1
                file_conversation_count += 1
                
                try:
                    # Extract content
                    content = extract_conversation_content(conversation)
                    
                    # Create a hash of the content to detect duplicates
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    
                    # Skip if this is a duplicate
                    if content_hash in processed_hashes:
                        continue
                        
                    # Add to processed hashes
                    processed_hashes.add(content_hash)
                    
                    # Create entry
                    entry = {
                        "key": f"conversation.{conversation.get('title', 'untitled').lower().replace(' ', '_')}",
                        "value": content,
                        "timestamp": epoch_to_iso(conversation.get('create_time')),
                        "status": "active",
                        "tags": extract_tags(conversation, content),
                        "create_time": conversation.get('create_time', 0),  # For sorting
                        "content_hash": content_hash,  # For deduplication
                        "source_file": json_file  # Track source file
                    }
                    
                    all_conversations.append(entry)
                except Exception as e:
                    print(f"Error processing conversation in {json_file}: {str(e)}")
            
            print(f"Processed {file_conversation_count} conversations from {json_file}")
            successful_files += 1
            
    except Exception as e:
        print(f"Error parsing file {json_file}: {str(e)}")

print(f"Successfully processed {successful_files}/{file_count} files")
print(f"Total conversations found: {total_conversations}")
print(f"Unique conversations after deduplication: {len(all_conversations)}")

# Sort conversations by most recent first
all_conversations.sort(key=lambda x: x.get('create_time', 0), reverse=True)

# Remove temporary fields used for processing
for entry in all_conversations:
    if 'create_time' in entry:
        del entry['create_time']
    if 'content_hash' in entry:
        del entry['content_hash']
    if 'source_file' in entry:
        del entry['source_file']

# Split into files with 150 KB size cap
file_counter = 1
current_file_size = 0
max_file_size = 150 * 1024  # 150 KB in bytes
current_entries = []

# Process all entries
for entry in all_conversations:
    # Estimate entry size in bytes
    entry_size = sys.getsizeof(json.dumps(entry))
    
    # Check if adding this entry would exceed the file size limit
    if current_file_size + entry_size > max_file_size and current_entries:
        # Save current batch to file
        transformed_data = {
            "metadata": {
                "source": f"combined_conversations_part_{file_counter}.json",
                "schema_version": "1.0",
                "last_updated": datetime.datetime.now().isoformat(),
                "tags": [
                    "chatgpt",
                    "conversations",
                    "transformed",
                    "llm_readable",
                    "deduplicated"
                ],
                "item_count": len(current_entries)
            },
            "conversations": current_entries
        }
        
        output_path = os.path.join(output_dir, f"combined_conversations_part_{file_counter}.json")
        with open(output_path, 'w') as f:
            json.dump(transformed_data, f, indent=2)
        
        print(f"Part {file_counter} saved with {len(current_entries)} entries, size: {current_file_size / 1024:.2f} KB")
        
        # Reset for next file
        file_counter += 1
        current_file_size = entry_size
        current_entries = [entry]
    else:
        # Add entry to current batch
        current_entries.append(entry)
        current_file_size += entry_size

# Save any remaining entries
if current_entries:
    transformed_data = {
        "metadata": {
            "source": f"combined_conversations_part_{file_counter}.json",
            "schema_version": "1.0",
            "last_updated": datetime.datetime.now().isoformat(),
            "tags": [
                "chatgpt",
                "conversations",
                "transformed",
                "llm_readable",
                "deduplicated"
            ],
            "item_count": len(current_entries)
        },
        "conversations": current_entries
    }
    
    output_path = os.path.join(output_dir, f"combined_conversations_part_{file_counter}.json")
    with open(output_path, 'w') as f:
        json.dump(transformed_data, f, indent=2)
    
    print(f"Part {file_counter} saved with {len(current_entries)} entries, size: {current_file_size / 1024:.2f} KB")

print(f"Transformation complete. {file_counter} files created in {output_dir}")
print(f"Total unique conversations processed: {len(all_conversations)}")
