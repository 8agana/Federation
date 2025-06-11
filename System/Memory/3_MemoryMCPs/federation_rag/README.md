# Federation RAG MCP Server

Unified Retrieval-Augmented Generation across multiple data sources.

## Overview

Federation RAG provides a single query interface to search across:
- ChromaDB memories (CC and DT)
- Knowledge Graph (coming soon)
- Obsidian notes (coming soon)
- Gmail (Phase 2)
- Google Drive (Phase 2)

## Installation

1. Install dependencies:
```bash
cd /Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/federation_rag
pip install -r requirements.txt
```

2. Set up your Groq API key (already configured in .env file)

3. Add to MCP settings (already done for DT)

4. Restart Claude to activate

## Available Tools

### rag_query
Query across federated data sources with intelligent synthesis.

```python
# Query all available sources
result = rag_query("What have we learned about RAG?")

# Query specific sources
result = rag_query(
    query="What are Sam's thoughts on organization?",
    sources=["cc_memories"]
)
```

### rag_sources
List available and planned data sources.

```python
sources = rag_sources()
# Returns: {
#   'available': ['cc_memories', 'dt_memories'],
#   'planned': ['knowledge_graph', 'obsidian_notes', ...],
#   'total_available': 2
# }
```

### rag_test
Test system functionality.

```python
test = rag_test()
# Returns system status and test query results
```

### rag_clear_cache
Clear the 15-minute query cache.

```python
rag_clear_cache()
```

## Architecture

```
Query → Router → Parallel Retrievers → Context Merge → LLM → Response
                    ↓
            [ChromaDB] [KG] [Obsidian]
```

## Configuration

The system uses:
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (local)
- **LLM**: Groq Llama 3.3 70B
- **Cache**: 15-minute TTL for repeated queries

## Phase 1 Features (Current)
- ✅ ChromaDB retrieval (CC and DT memories)
- ✅ Parallel source querying
- ✅ LLM synthesis with Groq
- ✅ Simple caching
- ✅ Source attribution

## Phase 2 Features (Planned)
- Knowledge Graph traversal
- Obsidian note search
- Query cost estimation
- Advanced caching layers
- Security gateway

## Troubleshooting

### No LLM Response
- Check that GROQ_API_KEY is set
- Verify internet connection
- System will fall back to raw context display

### No Results Found
- Verify ChromaDB paths are correct
- Check that collections have data
- Try broader search terms

## Performance

- ChromaDB queries: ~100-500ms
- LLM generation: ~1-3s
- Cache hits: <10ms

## Security Notes

Phase 1 implementation has basic security. Phase 2 will add:
- JWT-based authentication
- Query audit logging
- Rate limiting
- Cost controls