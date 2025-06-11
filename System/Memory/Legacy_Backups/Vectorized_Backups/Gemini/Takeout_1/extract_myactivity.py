import os
import re
import json
import datetime
import hashlib
from bs4 import BeautifulSoup
import sys

# Create output directory if it doesn't exist
output_dir = '/home/ubuntu/gemini_output'
os.makedirs(output_dir, exist_ok=True)

# Read the HTML file
print("Reading MyActivity.html file...")
with open('/home/ubuntu/upload/MyActivity.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

print(f"File size: {len(html_content)} bytes")

# Parse HTML with BeautifulSoup
print("Parsing HTML content...")
soup = BeautifulSoup(html_content, 'html.parser')

# Find all activity blocks
print("Finding activity blocks...")
activity_blocks = soup.find_all('div', class_='outer-cell')
print(f"Found {len(activity_blocks)} activity blocks")

# Function to extract timestamp from string
def extract_timestamp(timestamp_str):
    # Example: "May 26, 2025, 10:07:57 AM CDT"
    try:
        # Remove timezone abbreviation
        timestamp_str = re.sub(r'\s[A-Z]{3}$', '', timestamp_str)
        # Parse the timestamp
        dt = datetime.datetime.strptime(timestamp_str, "%b %d, %Y, %I:%M:%S %p")
        return dt.isoformat()
    except Exception as e:
        print(f"Error parsing timestamp '{timestamp_str}': {e}")
        return datetime.datetime.now().isoformat()

# Extract conversations
print("Extracting conversations...")
conversations = []
processed_hashes = set()  # For deduplication

for block in activity_blocks:
    try:
        # Get product type (e.g., "Gemini Apps")
        header = block.find('div', class_='header-cell')
        if not header:
            continue
            
        title = header.find('p', class_='mdl-typography--title')
        if not title or not title.text.strip():
            continue
            
        product = title.text.strip()
        
        # Skip if not Gemini Apps
        if "Gemini" not in product:
            continue
        
        # Get content cells
        content_cells = block.find_all('div', class_='content-cell')
        if not content_cells or len(content_cells) < 1:
            continue
            
        # Get prompt and timestamp
        main_content = content_cells[0].text.strip()
        
        # Extract prompt
        prompt_match = re.search(r'Prompted\s+(.*?)(?:\n|$)', main_content)
        prompt = prompt_match.group(1).strip() if prompt_match else "Unknown prompt"
        
        # Check if prompt is "a sensitive query"
        if prompt == "a sensitive query":
            prompt = "[Sensitive query]"
        
        # Extract timestamp
        timestamp_match = re.search(r'([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4},\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M\s+[A-Z]{3})', main_content)
        timestamp_str = timestamp_match.group(1) if timestamp_match else ""
        timestamp = extract_timestamp(timestamp_str) if timestamp_str else datetime.datetime.now().isoformat()
        
        # Extract response (if available)
        response = ""
        response_paragraphs = []
        
        # Look for paragraphs after the timestamp
        for p in content_cells[0].find_all('p'):
            if p.text and not p.text.startswith("Prompted"):
                response_paragraphs.append(p.text.strip())
        
        # Also look for lists
        for ul in content_cells[0].find_all('ul'):
            response_paragraphs.append(ul.text.strip())
            
        response = "\n\n".join(response_paragraphs)
        
        # Check for attachments
        attachments = []
        attachment_match = re.search(r'Attached\s+\d+\s+file', main_content)
        if attachment_match:
            for link in content_cells[0].find_all('a'):
                if link.get('href'):
                    attachments.append(link.get('href'))
        
        # Create conversation content
        content = f"User: {prompt}\n\n"
        if response:
            content += f"Assistant: {response}\n\n"
        if attachments:
            content += f"Attachments: {', '.join(attachments)}\n\n"
        
        # Create a hash of the content for deduplication
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Skip if duplicate
        if content_hash in processed_hashes:
            continue
            
        # Add to processed hashes
        processed_hashes.add(content_hash)
        
        # Extract tags
        tags = ["gemini", "conversation"]
        
        # Add content-based tags
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
        
        # Create conversation entry
        entry = {
            "key": f"gemini_conversation.{hashlib.md5(prompt.encode()).hexdigest()[:8]}",
            "value": content,
            "timestamp": timestamp,
            "status": "active",
            "tags": tags,
            "create_time": timestamp,  # For sorting
            "content_hash": content_hash  # For deduplication
        }
        
        conversations.append(entry)
        
    except Exception as e:
        print(f"Error processing block: {e}")

print(f"Extracted {len(conversations)} unique conversations")

# Sort conversations by most recent first
print("Sorting conversations by timestamp...")
conversations.sort(key=lambda x: x.get('create_time', ''), reverse=True)

# Remove temporary fields used for processing
for entry in conversations:
    if 'create_time' in entry:
        del entry['create_time']
    if 'content_hash' in entry:
        del entry['content_hash']

# Split into files with 150 KB size cap
print("Splitting into files...")
file_counter = 1
current_file_size = 0
max_file_size = 150 * 1024  # 150 KB in bytes
current_entries = []

# Process all entries
for entry in conversations:
    # Estimate entry size in bytes
    entry_size = sys.getsizeof(json.dumps(entry))
    
    # Check if adding this entry would exceed the file size limit
    if current_file_size + entry_size > max_file_size and current_entries:
        # Save current batch to file
        transformed_data = {
            "metadata": {
                "source": f"gemini_conversations_part_{file_counter}.json",
                "schema_version": "1.0",
                "last_updated": datetime.datetime.now().isoformat(),
                "tags": [
                    "gemini",
                    "conversations",
                    "transformed",
                    "llm_readable",
                    "deduplicated"
                ],
                "item_count": len(current_entries)
            },
            "conversations": current_entries
        }
        
        output_path = os.path.join(output_dir, f"gemini_conversations_part_{file_counter}.json")
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
            "source": f"gemini_conversations_part_{file_counter}.json",
            "schema_version": "1.0",
            "last_updated": datetime.datetime.now().isoformat(),
            "tags": [
                "gemini",
                "conversations",
                "transformed",
                "llm_readable",
                "deduplicated"
            ],
            "item_count": len(current_entries)
        },
        "conversations": current_entries
    }
    
    output_path = os.path.join(output_dir, f"gemini_conversations_part_{file_counter}.json")
    with open(output_path, 'w') as f:
        json.dump(transformed_data, f, indent=2)
    
    print(f"Part {file_counter} saved with {len(current_entries)} entries, size: {current_file_size / 1024:.2f} KB")

print(f"Transformation complete. {file_counter} files created in {output_dir}")
print(f"Total unique conversations processed: {len(conversations)}")
