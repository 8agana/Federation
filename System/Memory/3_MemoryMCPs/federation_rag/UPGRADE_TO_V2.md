# Federation RAG V2 Upgrade Guide

## Current Status
- V2 is fully implemented with all specialized tools
- Configuration has been updated to use V2
- GROQ API key is configured

## To Activate V2

### For Desktop Claude (DT):
1. **Restart Desktop Claude** completely (Quit and reopen)
2. After restart, you'll have these new tools:
   - `rag_query` - Fast daily driver (unchanged name, enhanced performance)
   - `rag_query_history` - Timeline explorer with legacy JSON
   - `rag_query_files` - Code/document hunter
   - `rag_query_full` - **Deep research mode (ALL 6 sources)** ← This is what you're missing!
   - `rag_auto` - Smart auto-routing with cascading

### For Claude Code (CC):
Same process - restart to activate V2

## What's New in V2

### 1. **rag_query_full IS IMPLEMENTED!**
- Searches across ALL 6 sources
- Comprehensive synthesis
- Perfect for deep research

### 2. **rag_auto** - Smart Router
- Auto-detects query intent
- Routes to appropriate tool
- Cascades if insufficient results

### 3. **Performance Optimizations**
- Lazy loading (files/legacy only when needed)
- Separate caches per tool
- No artificial context limits

### 4. **Enhanced Features**
- Handoff detection for restart scenarios
- Custom synthesis styles per tool
- Cache statistics tracking

## Verification
After restart, test with:
```
rag_sources()
```

Should show:
- Version: "v2 - Specialized Tools"
- All 5 specialized tools listed
- 6 total sources available

## Troubleshooting
If tools don't appear after restart:
1. Check MCP logs for errors
2. Verify python dependencies are installed
3. Confirm configuration points to `run_dt_server_v2.py`

The system is ready - just needs a restart to activate!