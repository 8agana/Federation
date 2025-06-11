# Federation Tools - Memory Browser & RAG Search

Two powerful tools for exploring the Federation knowledge system.

## Quick Start

Launch the main menu:
```bash
python3 launch_federation_tools.py
```

This gives you a choice between:
- **🧠 Memory Browser** - Browse and manage ChromaDB memories
- **🚀 RAG V2 Search** - Search across all Federation sources

## Individual Apps

### Memory Browser
```bash
python3 memory_browser_app.py
```

Features:
- Browse CC (772) and DT (565) memories
- Advanced v5 filtering (priority, domain, tags)
- Create, edit, and delete memories
- Export/import functionality
- Memory health diagnostics

### RAG V2 Search
```bash
python3 rag_search_app.py
```

Features:
- 5 specialized search tools:
  - 🚀 `rag_query` - Fast daily driver
  - 📜 `rag_query_history` - Timeline explorer
  - 🔍 `rag_query_files` - Code hunter
  - 🧠 `rag_query_full` - Deep research
  - 🤖 `rag_auto` - Smart auto-routing
- Search across 6 sources:
  - CC & DT Memories
  - Knowledge Graph
  - Obsidian Notes
  - Federation Files
  - Legacy JSON Archives
- Natural language understanding
- LLM-powered synthesis
- Export results to JSON/text

## Why Two Apps?

Separating the apps avoids ChromaDB conflicts where both the browser and RAG try to open the same database with different settings. Each app can now:
- Use ChromaDB optimally for its purpose
- Launch faster with less overhead
- Be developed independently

## Directory Structure

```
ChromaDB_Browser/
├── launch_federation_tools.py  # Main launcher menu
├── memory_browser_app.py      # Standalone memory browser
├── rag_search_app.py         # Standalone RAG search
├── src/                      # Source code
│   ├── tkinter_memory_browser_v5_bigger.py
│   ├── chromadb_rag_browser_v2_direct.py (deprecated)
│   └── ...
└── launchers/               # Old launchers (archived)
```

## Requirements

- Python 3.8+
- ChromaDB
- Federation RAG system installed
- GROQ API key (for LLM synthesis)

## Notes

- The apps are independent - you can run both simultaneously
- Memory Browser connects directly to ChromaDB
- RAG Search initializes the full Federation RAG V2 system
- Both apps have export functionality for results