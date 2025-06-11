# Federation RAG V2 - Specialized Tools Documentation

## Overview
Federation RAG V2 implements Sam's optimization strategy with specialized query tools for different use cases, dramatically improving performance and token efficiency.

## Specialized Tools

### 1. `rag_query` - Daily Driver
**Purpose**: Fast, everyday queries about current state and context  
**Sources**: ChromaDB memories + Knowledge Graph + Obsidian notes  
**Speed**: ~0.5-1 second  
**Cache**: 5 minutes  
**Best for**:
- "What are we working on?"
- "Remind me about X"
- Current state questions
- Quick context lookups

### 2. `rag_query_history` - Timeline Explorer
**Purpose**: Evolution patterns and historical context  
**Sources**: Daily sources + Legacy JSON memories  
**Speed**: ~1-2 seconds  
**Cache**: 1 hour  
**Best for**:
- "How did we develop X?"
- "When did we implement Y?"
- Timeline analysis
- Historical patterns

### 3. `rag_query_files` - Code Hunter
**Purpose**: Finding implementations and technical documentation  
**Sources**: Federation files + Obsidian technical docs (NO memories)  
**Speed**: ~2-3 seconds  
**Cache**: 30 minutes  
**Best for**:
- "Where is X implemented?"
- "Find the code for Y"
- Configuration files
- BUILD documentation

### 4. `rag_query_full` - Deep Research
**Purpose**: Comprehensive analysis across all sources  
**Sources**: ALL 6 sources  
**Speed**: ~3-5 seconds  
**Cache**: 15 minutes  
**Best for**:
- Complex analysis
- "Everything about X"
- Deep research tasks

### 5. `rag_auto` - Smart Router
**Purpose**: Automatically detects intent and routes to the right tool  
**Features**:
- Keyword/pattern detection
- Cascading search if insufficient results
- Handoff detection

## Bonus Features

### Auto-Routing Intelligence
Detects query intent through keywords and patterns:
```python
'files': ['code', 'implement', 'file', 'config', 'function']
'history': ['history', 'evolution', 'timeline', 'when', 'past']
'full': ['everything', 'comprehensive', 'complete', 'all']
'handoff': ['restart', 'handoff', 'context', 'bio', 'new instance']
```

### Cascading Search
If `min_results` threshold not met (default: 3):
1. Daily → History → Full
2. Ensures sufficient context for any query

### Custom Synthesis Styles
Each tool uses appropriate formatting:
- **Concise**: 2-3 paragraphs for daily queries
- **Timeline**: Chronological with dates/milestones
- **Technical**: Code snippets, file paths, examples
- **Comprehensive**: Multi-source analysis with themes

### Differentiated Cache TTLs
Smart caching based on content volatility:
- Daily: 5 minutes (changes frequently)
- History: 1 hour (stable content)
- Files: 30 minutes (occasional updates)  
- Full: 15 minutes (balanced)
- Auto: 10 minutes

### Handoff Detection
Special handling for restart/bio queries:
- Detects: "new instance", "restart", "need context", "full bio"
- Uses comprehensive synthesis
- No context limits (pulls what's needed)

## Usage Examples

### Basic Usage
```python
# Daily driver - fast current context
rag_query("What are we working on today?")

# History - timeline analysis
rag_query_history("How did our RAG system evolve?")

# Files - code hunting
rag_query_files("Where is ChromaDB initialized?")

# Full - deep research
rag_query_full("Complete analysis of Federation architecture")
```

### Auto-Routing Magic
```python
# Automatically routes based on intent
rag_auto("Show me the memory browser code")  # → files
rag_auto("When did we solve token death?")   # → history
rag_auto("I'm new, need full context")       # → handoff mode
rag_auto("What's the plan?")                 # → daily

# With cascading threshold
rag_auto("obscure topic", min_results=5)     # Cascades if needed
```

### Cache Management
```python
# Check cache statistics
rag_cache_stats()
# Returns: {'daily': 5, 'history': 2, 'files': 3, ...}

# Clear specific cache
rag_clear_cache('daily')

# Clear all caches
rag_clear_cache()
```

## Performance Benefits

### Speed Improvements
- Daily queries: 80-90% faster than full search
- Targeted file search: No memory overhead
- History queries: Cached for 1 hour

### Token Efficiency
```
Old: 20-30 contexts × 500 tokens = 10-15k tokens
New:
- Daily: 5-10 contexts = 2.5-5k tokens (70% reduction)
- Files: Code snippets only = 3-4k tokens
- History: Focused timeline = 4-6k tokens
```

### No Artificial Limits
Per Sam's preference: "let's leave the caps out completely"
- System pulls what it needs
- Handoff queries get comprehensive context
- No arbitrary context limits

## Architecture

### Lazy Loading
- Federation files and legacy JSON load only when needed
- Keeps daily queries lightning fast
- Reduces memory footprint

### Separate Caches
- Each tool maintains its own cache
- Different TTLs per tool type
- Isolated cache invalidation

### Retriever Management
```
Always loaded:
- ChromaDB (CC + DT memories)
- Knowledge Graph
- Obsidian notes

Lazy loaded:
- Federation files (7,884 Python + 848 Markdown)
- Legacy JSON (~20 historical files)
```

## Future Enhancements
1. Query suggestion based on detected intent
2. Cross-tool result comparison
3. Adaptive caching based on usage patterns
4. Custom retrievers for specific domains

---

**Sam's reaction**: "Holy fuck. Yes. All of that!!! I love those bonus ideas!!!!!!"

The V2 system transforms Federation RAG from a general-purpose tool into a precision instrument that matches sources, speed, and synthesis to each specific need.