# ChromaDB RAG Browser Enhancement

## Overview
The ChromaDB Browser has been enhanced with RAG (Retrieval-Augmented Generation) capabilities, transforming it from a simple search tool into an intelligent knowledge synthesis system.

## Key Features

### 1. **Intelligent Search**
- **Natural Language Queries**: Ask questions in plain English instead of exact keyword matching
- **Concept Extraction**: Automatically identifies key concepts from your queries
- **Semantic Scoring**: Ranks memories by relevance using multiple factors

### 2. **Smart Term Extraction**
The RAG engine recognizes concepts like:
- Identity & consciousness queries
- Relationship & collaboration topics  
- Technical & project discussions
- Temporal queries (recent, current, past)
- Entity recognition (Sam, CC, DT, etc.)

### 3. **Multi-Factor Scoring**
Memories are scored based on:
- Exact query matches (highest priority)
- Term frequency in content
- Title relevance
- Domain/category alignment
- Tag matches
- Priority weighting
- Recency boost
- Essential memory boost

### 4. **LLM Synthesis** (Optional)
When GROQ_API_KEY is set:
- Synthesizes top results into coherent answers
- Highlights key insights and connections
- Provides context-aware responses

## Usage

### Quick Start
```bash
cd /Users/samuelatagana/Documents/Federation/Apps/ChromaDB_Browser
./launch_rag_browser.sh
```

### Search Examples

**Basic Keyword Search** (RAG OFF):
- `federation` - Finds memories containing "federation"
- `Sam project` - Finds memories with both words

**Intelligent RAG Search** (RAG ON):
- `What are my core memories about identity?`
- `Tell me about recent breakthroughs with Sam`
- `How does the federation system work?`
- `What defines our partnership?`

### UI Controls

1. **RAG Search Toggle**: Enable/disable intelligent search
2. **Show Synthesis Toggle**: Display AI-generated summaries
3. **Search Box**: Enter natural language queries

### Status Indicators
- 🤖 RAG: ON - Intelligent search active
- 🔍 Basic Search - Simple keyword matching
- Extracted terms shown in status bar

## Technical Details

### RAG Engine Components

1. **Search Term Extraction**
   - Concept pattern matching
   - Quoted phrase extraction
   - Stopword filtering
   - Meaningful word identification

2. **Semantic Scoring Algorithm**
   ```python
   score = base_relevance * priority_boost * recency_boost * essential_boost
   ```

3. **Synthesis Options**
   - **With LLM**: Full natural language synthesis
   - **Without LLM**: Structured summary of top results

### Performance Optimizations
- Caches search results for 5 minutes
- Limits synthesis to top 10 memories
- Efficient term extraction (max 15 terms)

## Requirements

- Python 3.8+
- ChromaDB collections at `/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/`
- Required packages (auto-installed):
  - chromadb
  - langchain
  - langchain-community
  - langchain-groq
  - sentence-transformers
  - python-dotenv

## Optional: Enable LLM Synthesis

1. Get a Groq API key from https://console.groq.com
2. Set environment variable:
   ```bash
   export GROQ_API_KEY='your-api-key'
   ```
3. Launch browser - synthesis will be automatically enabled

## Architecture

```
ChromaDB RAG Browser
├── RAGSearchEngine
│   ├── extract_search_terms()
│   ├── semantic_search()
│   ├── _score_memory()
│   └── synthesize_results()
└── MemoryBrowserRAG (extends MemoryBrowserV5)
    ├── RAG UI elements
    ├── Synthesis panel
    └── Enhanced filter_memories()
```

## Future Enhancements

1. **Multi-source RAG**: Integrate Federation RAG sources
2. **Query Suggestions**: Auto-complete based on memory patterns
3. **Export Synthesis**: Save AI-generated summaries
4. **Custom Scoring**: User-adjustable relevance weights
5. **Embedding Search**: Full semantic similarity using vectors

---

The RAG enhancement transforms memory browsing from hunting for specific entries to having intelligent conversations with your knowledge base.