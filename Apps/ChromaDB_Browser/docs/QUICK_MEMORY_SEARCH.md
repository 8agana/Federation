# 🔍 Quick Memory Search Commands

Until the memory system is consolidated, use these CLI tools:

## Quick Search
```bash
# Search all memories
python3 /Users/samuelatagana/Documents/Claude_Home/System/Scripts/query_memory.py "search term"

# ChromaDB vector search
python3 /Users/samuelatagana/Documents/Claude_Home/System/Scripts/cc_chromadb_bridge.py --search "query"
```

## Your Browser (when ready)
```bash
# Launch Federation Browser
/Users/samuelatagana/Documents/Claude_Home/Tools/ChromaDB_Browser/launch.sh
```

## Current Memory State
- **CC Memories**: 1,869 (in CC's database)
- **DT Memories**: 203 total
  - 26 in DT's database (June 3-4)
  - 177 in CC's database (May 29 - June 1) 
- **Shared**: 112 memories

## TODO
1. Consolidate DT's memories into one database
2. Fix the timezone issues in the browser
3. Add list view to the browser
4. Maybe add a simple web UI

For now, the CLI tools work great for searching!