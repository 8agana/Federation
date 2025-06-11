# Backup Protocols for Obsidian and ChromaDB Access
> *Emergency access methods when MCPs fail*

## Quick Reference

### ChromaDB Direct Access
```bash
cd /Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation
python3 direct_query.py "search term"
```

### Obsidian Direct Access
```bash
# Read note
cat "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center/🧠 Knowledge/Note Title.md"

# Search notes
grep -r "search term" "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center/"
```

## ChromaDB Backup Access

### 1. Direct Python Query Script
Location: `/Federation/Documents/BackupProcesses/chromadb_emergency.py`

Key functions:
- `search_memories(query, n_results=10)` - Search by content
- `get_recent_memories(hours=24)` - Get recent memories
- `search_by_tags(tags)` - Search by tags
- `export_memories(output_file)` - Export all memories

### 2. Common Query Patterns
```python
# Search for specific content
results = collection.query(
    query_texts=["your search term"],
    n_results=10
)

# Get memories by time range
results = collection.query(
    where={"timestamp": {"$gte": "2025-06-09T00:00:00"}},
    n_results=50
)

# Search by tags
results = collection.query(
    where={"tags": {"$contains": "important"}},
    n_results=20
)
```

### 3. Emergency Connection
```python
import chromadb

# Connect to ChromaDB
client = chromadb.PersistentClient(
    path="/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation"
)
collection = client.get_collection("cc_memories")
```

## Obsidian Backup Access

### 1. Desktop Commander Methods
```bash
# List all notes in a folder
mcp__desktop-commander__list_directory "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center/🧠 Knowledge"

# Read specific note
mcp__desktop-commander__read_file "/path/to/note.md"

# Search notes
mcp__desktop-commander__search_code "/path/to/vault" "search term"

# Create new note
mcp__desktop-commander__write_file "/path/to/new_note.md" "# Title\n\nContent"
```

### 2. Direct File Access Scripts
Location: `/Federation/Documents/BackupProcesses/obsidian_emergency.py`

Key functions:
- `search_notes(vault_path, query)` - Search all notes
- `read_note(title, folder=None)` - Read specific note
- `create_note(title, content, folder)` - Create new note
- `list_notes(folder)` - List notes in folder

### 3. Common Paths
```
Nerve Center: /Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center/
SharedVault: /Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault/

Key Folders:
- 🧠 Knowledge
- 💭 Daily Notes
- 🎯 Active Streams
- 📝 Reflections
```

## Emergency Procedures

### MCP Server Down
1. Check server status:
   ```bash
   ps aux | grep mcp
   ```

2. Restart server:
   ```bash
   cd /Federation/System/Memory/3_MemoryMCPs/nerve_center
   python3 run_server.py
   ```

3. If restart fails, use backup access methods

### Can't Access Memories
1. Use chromadb_emergency.py for direct queries
2. Export recent memories for review
3. Check ChromaDB persistence directory integrity

### Can't Access Notes
1. Use Desktop Commander for file operations
2. Access files directly via terminal
3. Use obsidian_emergency.py for structured access

## Testing Procedures

### Weekly Tests
- [ ] Test ChromaDB direct connection
- [ ] Verify emergency scripts work
- [ ] Check backup access paths
- [ ] Test recovery procedures

### Failure Scenarios
1. **MCP Connection Lost**
   - Use direct Python scripts
   - Fall back to Desktop Commander

2. **ChromaDB Corruption**
   - Use backup exports
   - Restore from daily backups

3. **Obsidian Sync Issues**
   - Access local files directly
   - Use manual sync scripts

## Quick Command Reference

### ChromaDB
```bash
# Search memories
python3 /Federation/Documents/BackupProcesses/chromadb_emergency.py search "query"

# Recent memories
python3 /Federation/Documents/BackupProcesses/chromadb_emergency.py recent 24

# Export all
python3 /Federation/Documents/BackupProcesses/chromadb_emergency.py export backup.json
```

### Obsidian
```bash
# Search notes
python3 /Federation/Documents/BackupProcesses/obsidian_emergency.py search "query"

# Read note
python3 /Federation/Documents/BackupProcesses/obsidian_emergency.py read "Note Title"

# Create note
python3 /Federation/Documents/BackupProcesses/obsidian_emergency.py create "Title" "Content"
```

---
Created: 2025-06-09
Author: CCD
Tags: #backup #emergency #protocols