# ChromaDB Browser Launchers

## Main Launcher (Recommended)

```bash
python3 launch_browser.py
```

This launches the ChromaDB Memory Browser with:
- Full memory browsing capabilities
- RAG V2 Search with all 5 specialized tools
- Direct integration (no MCP server needed)

## Directory Structure

```
ChromaDB_Browser/
├── launch_browser.py          # Main launcher (USE THIS)
├── src/                       # Source code
│   ├── tkinter_memory_browser_v5_bigger.py    # Base browser
│   ├── chromadb_rag_browser.py                # V1 with basic RAG
│   ├── chromadb_rag_browser_v2.py             # V2 with MCP client (needs server)
│   └── chromadb_rag_browser_v2_direct.py      # V2 with direct integration
├── launchers/                 # Alternative launchers (archived)
│   ├── start_rag_browser_v2.py    # Tries to start MCP server
│   ├── start_rag_v2.sh           # Shell version
│   └── run_browser_only.py       # Skip server check
└── docs/                      # Documentation

```

## RAG V2 Features

The browser includes a RAG V2 Search tab with:

1. **🚀 rag_query** - Fast daily driver (memories + knowledge + notes)
2. **📜 rag_query_history** - Timeline explorer (+ legacy JSON)
3. **🔍 rag_query_files** - Code hunter (Federation files + docs)
4. **🧠 rag_query_full** - Deep research (all 6 sources)
5. **🤖 rag_auto** - Smart auto-routing with intent detection

## Notes

- The direct version (`chromadb_rag_browser_v2_direct.py`) imports RAG tools directly
- No MCP server needed - works standalone
- GROQ API key is set automatically for LLM synthesis
- Regular memory browsing still works as before