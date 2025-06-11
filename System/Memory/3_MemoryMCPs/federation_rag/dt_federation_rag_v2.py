#!/usr/bin/env python3
"""
DT Federation RAG MCP Server V2 - Specialized Tools Edition
Optimized RAG with specialized query tools for different use cases
"""

import os
import sys
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
import hashlib
import json
import re
import glob
from pathlib import Path
from dotenv import load_dotenv
from federation_files_retriever import FederationFilesRetriever
from legacy_json_retriever import LegacyJSONRetriever

# Load environment variables
load_dotenv()

# MCP imports
from mcp.server.fastmcp import FastMCP

# LangChain imports
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.schema import Document

# ChromaDB imports
import chromadb
from chromadb.config import Settings

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dt_federation_rag_v2")

# Create MCP server
mcp = FastMCP("dt-federation-rag-v2")

# Initialize embeddings (using local model for privacy)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

# Initialize Groq LLM (requires GROQ_API_KEY env var)
try:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=2048
    )
except Exception as e:
    logger.warning(f"Failed to initialize Groq LLM: {e}")
    logger.warning("Set GROQ_API_KEY environment variable to enable LLM features")
    llm = None

# Import retriever classes from V1
from dt_federation_rag import (
    ChromaDBRetriever, 
    KnowledgeGraphRetriever, 
    ObsidianRetriever
)

# Query intent patterns for auto-routing
QUERY_PATTERNS = {
    'files': {
        'keywords': ['code', 'implement', 'file', 'config', 'script', 'function', 'class', 'module', 'import'],
        'patterns': [r'where is.*implemented', r'find.*code', r'show.*implementation', r'locate.*file']
    },
    'history': {
        'keywords': ['history', 'evolution', 'timeline', 'when', 'progress', 'journey', 'past', 'before'],
        'patterns': [r'how did.*develop', r'when did', r'evolution of', r'history of', r'timeline']
    },
    'full': {
        'keywords': ['everything', 'comprehensive', 'complete', 'full', 'all', 'entire', 'thorough'],
        'patterns': [r'tell me everything', r'comprehensive.*analysis', r'complete.*overview']
    },
    'handoff': {
        'keywords': ['restart', 'handoff', 'context', 'bio', 'new instance', 'starting', 'onboarding'],
        'patterns': [r'I.*new.*instance', r'just.*started', r'need.*context', r'full.*bio', r'catch.*up', r'bring.*speed']
    }
}

# Cache TTL strategies per tool
CACHE_STRATEGIES = {
    'daily': timedelta(minutes=5),      # Changes frequently
    'history': timedelta(hours=1),      # Rarely changes
    'files': timedelta(minutes=30),     # Occasional updates
    'full': timedelta(minutes=15),      # Balanced
    'auto': timedelta(minutes=10)       # Auto-routing cache
}


class DTFederationRAGv2:
    """Enhanced DT Federation RAG with specialized query tools"""
    
    def __init__(self):
        """Initialize the enhanced RAG system"""
        self.retrievers = {}
        self.llm = llm
        
        # Separate caches for each tool with different TTLs
        self.caches = {
            'daily': {},
            'history': {},
            'files': {},
            'full': {},
            'auto': {}
        }
        
        # Initialize all retrievers (lazy loading per query type)
        self._init_retrievers()
        
    def _init_retrievers(self):
        """Initialize all available retrievers"""
        # ChromaDB retrievers (always needed)
        try:
            self.retrievers['cc_memories'] = ChromaDBRetriever(
                collection_name="cc_memories",
                chroma_path="/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation"
            )
            logger.info("CC memories retriever initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize CC memories: {e}")
        
        try:
            self.retrievers['dt_memories'] = ChromaDBRetriever(
                collection_name="dt_memories",
                chroma_path="/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/dt-federation"
            )
            logger.info("DT memories retriever initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize DT memories: {e}")
        
        # Knowledge Graph retriever
        try:
            self.retrievers['dt_knowledge_graph'] = KnowledgeGraphRetriever(
                obsidian_path="/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center"
            )
            logger.info("DT Knowledge Graph retriever initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize DT Knowledge Graph: {e}")
        
        # Obsidian retriever
        try:
            vault_paths = [
                "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault",
                "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center"
            ]
            self.retrievers['dt_obsidian_notes'] = ObsidianRetriever(vault_paths)
            logger.info("DT Obsidian retriever initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize DT Obsidian retriever: {e}")
        
        # Federation Files retriever (lazy load for performance)
        self._federation_files_initialized = False
        
        # Legacy memories retriever (lazy load for performance)
        self._legacy_memories_initialized = False
    
    def _ensure_federation_files(self):
        """Lazy load federation files retriever when needed"""
        if not self._federation_files_initialized:
            try:
                self.retrievers['federation_files'] = FederationFilesRetriever(
                    base_path="/Users/samuelatagana/Documents/Federation"
                )
                logger.info("Federation files retriever initialized (lazy load)")
                self._federation_files_initialized = True
            except Exception as e:
                logger.warning(f"Failed to initialize Federation files: {e}")
    
    def _ensure_legacy_memories(self):
        """Lazy load legacy memories retriever when needed"""
        if not self._legacy_memories_initialized:
            try:
                self.retrievers['legacy_memories'] = LegacyJSONRetriever(
                    json_path="/Users/samuelatagana/Documents/Federation/System/Memory/Legacy_Backups/MemoryJSONS"
                )
                logger.info("Legacy memories retriever initialized (lazy load)")
                self._legacy_memories_initialized = True
            except Exception as e:
                logger.warning(f"Failed to initialize Legacy memories: {e}")
    
    def _get_cache_key(self, query: str, sources: List[str]) -> str:
        """Generate cache key for query"""
        source_str = "_".join(sorted(sources))
        return hashlib.md5(f"{query}_{source_str}".encode()).hexdigest()
    
    def _check_cache(self, cache_type: str, cache_key: str) -> Optional[Dict]:
        """Check cache with TTL strategy"""
        cache = self.caches.get(cache_type, {})
        ttl = CACHE_STRATEGIES.get(cache_type, timedelta(minutes=15))
        
        if cache_key in cache:
            cached_result, timestamp = cache[cache_key]
            if datetime.now() - timestamp < ttl:
                logger.info(f"Cache hit for {cache_type} query")
                return cached_result
        return None
    
    def _update_cache(self, cache_type: str, cache_key: str, result: Dict):
        """Update cache for specific query type"""
        self.caches[cache_type][cache_key] = (result, datetime.now())
    
    def detect_query_intent(self, query: str) -> str:
        """Detect query intent for auto-routing"""
        query_lower = query.lower()
        
        # Check each pattern type
        for intent, patterns in QUERY_PATTERNS.items():
            # Check keywords
            for keyword in patterns['keywords']:
                if keyword in query_lower:
                    logger.info(f"Auto-routing: Detected '{intent}' intent from keyword '{keyword}'")
                    return intent
            
            # Check regex patterns
            for pattern in patterns['patterns']:
                if re.search(pattern, query_lower):
                    logger.info(f"Auto-routing: Detected '{intent}' intent from pattern '{pattern}'")
                    return intent
        
        # Default to daily driver
        logger.info("Auto-routing: No specific intent detected, using daily driver")
        return 'daily'
    
    def query_daily(self, query: str, is_handoff: bool = False) -> Dict[str, Any]:
        """Fast daily driver - memories + knowledge graph + obsidian"""
        sources = ['cc_memories', 'dt_memories', 'dt_knowledge_graph', 'dt_obsidian_notes']
        
        # Check cache
        cache_key = self._get_cache_key(query, sources)
        cached = self._check_cache('daily', cache_key)
        if cached:
            return cached
        
        # Handoff queries need comprehensive synthesis
        if is_handoff:
            synthesis_style = 'comprehensive'
        else:
            synthesis_style = 'concise'
        
        # Execute query - no context limits
        result = self._execute_query(query, sources, synthesis_style=synthesis_style)
        
        # Update result with tool info
        if is_handoff:
            result['tool_used'] = 'rag_query (daily driver - handoff mode)'
        else:
            result['tool_used'] = 'rag_query (daily driver)'
        result['cache_ttl'] = '5 minutes'
        
        # Cache result
        self._update_cache('daily', cache_key, result)
        
        return result
    
    def query_history(self, query: str) -> Dict[str, Any]:
        """Timeline explorer - includes legacy JSON data"""
        # Ensure legacy memories are loaded
        self._ensure_legacy_memories()
        
        sources = ['cc_memories', 'dt_memories', 'dt_knowledge_graph', 'dt_obsidian_notes', 'legacy_memories']
        
        # Check cache
        cache_key = self._get_cache_key(query, sources)
        cached = self._check_cache('history', cache_key)
        if cached:
            return cached
        
        # Execute query with timeline focus
        result = self._execute_query(query, sources, synthesis_style='timeline')
        
        # Update result with tool info
        result['tool_used'] = 'rag_query_history (timeline explorer)'
        result['cache_ttl'] = '1 hour'
        
        # Cache result
        self._update_cache('history', cache_key, result)
        
        return result
    
    def query_files(self, query: str) -> Dict[str, Any]:
        """Code hunter - federation files + technical docs"""
        # Ensure federation files are loaded
        self._ensure_federation_files()
        
        # Include Obsidian for technical documentation (BUILD notes, processes, etc)
        # but NOT memory sources - keep it focused on implementation
        sources = ['federation_files', 'dt_obsidian_notes']
        
        # Check cache
        cache_key = self._get_cache_key(query, sources)
        cached = self._check_cache('files', cache_key)
        if cached:
            return cached
        
        # Execute query with code focus
        result = self._execute_query(query, sources, synthesis_style='technical')
        
        # Update result with tool info
        result['tool_used'] = 'rag_query_files (code hunter)'
        result['cache_ttl'] = '30 minutes'
        
        # Cache result
        self._update_cache('files', cache_key, result)
        
        return result
    
    def query_full(self, query: str) -> Dict[str, Any]:
        """Deep research - all 6 sources"""
        # Ensure all retrievers are loaded
        self._ensure_federation_files()
        self._ensure_legacy_memories()
        
        sources = list(self.retrievers.keys())
        
        # Check cache
        cache_key = self._get_cache_key(query, sources)
        cached = self._check_cache('full', cache_key)
        if cached:
            return cached
        
        # Execute comprehensive query
        result = self._execute_query(query, sources, synthesis_style='comprehensive')
        
        # Update result with tool info
        result['tool_used'] = 'rag_query_full (deep research)'
        result['cache_ttl'] = '15 minutes'
        
        # Cache result
        self._update_cache('full', cache_key, result)
        
        return result
    
    def query_auto(self, query: str, min_results: int = 3) -> Dict[str, Any]:
        """Auto-routing with cascading search"""
        # Detect intent
        intent = self.detect_query_intent(query)
        
        # Route to appropriate tool
        if intent == 'files':
            result = self.query_files(query)
        elif intent == 'history':
            result = self.query_history(query)
        elif intent == 'full':
            result = self.query_full(query)
        elif intent == 'handoff':
            # Handoff/restart queries need comprehensive context
            result = self.query_daily(query, is_handoff=True)
        else:
            # Start with daily driver
            result = self.query_daily(query)
            
            # Cascade if insufficient results
            if result['contexts_found'] < min_results:
                logger.info(f"Cascading search: Daily found {result['contexts_found']} < {min_results}, trying history")
                result = self.query_history(query)
                
                if result['contexts_found'] < min_results:
                    logger.info(f"Cascading search: History found {result['contexts_found']} < {min_results}, trying full")
                    result = self.query_full(query)
        
        # Add auto-routing info
        result['auto_detected_intent'] = intent
        result['tool_used'] = f"rag_auto → {result.get('tool_used', 'unknown')}"
        
        return result
    
    def _execute_query(self, query: str, sources: List[str], 
                      synthesis_style: str = 'standard') -> Dict[str, Any]:
        """Execute query with specified sources and parameters"""
        # Collect contexts from specified sources
        all_contexts = []
        source_metadata = []
        retrieval_stats = {}
        
        for source in sources:
            if source in self.retrievers:
                try:
                    logger.info(f"Querying {source} for: '{query[:50]}...'")
                    start_time = datetime.now()
                    
                    # Adjust k based on source type
                    k = 5 if source in ['federation_files', 'legacy_memories'] else 10
                    results = self.retrievers[source].retrieve(query, k=k)
                    
                    retrieval_time = (datetime.now() - start_time).total_seconds()
                    
                    logger.info(f"{source} returned {len(results)} results in {retrieval_time:.4f}s")
                    
                    retrieval_stats[source] = {
                        'count': len(results),
                        'time': retrieval_time
                    }
                    
                    for result in results:
                        all_contexts.append(result['content'])
                        source_metadata.append({
                            'source': source,
                            'metadata': result['metadata']
                        })
                        
                except Exception as e:
                    logger.error(f"Error retrieving from {source}: {e}")
                    retrieval_stats[source] = {'error': str(e)}
        
        # Build response
        if not all_contexts:
            return {
                'answer': "No relevant information found in the searched sources.",
                'sources_searched': sources,
                'contexts_found': 0,
                'retrieval_stats': retrieval_stats
            }
        
        # Generate synthesis based on style
        if self.llm:
            answer = self._synthesize_with_style(query, all_contexts, source_metadata, synthesis_style)
        else:
            answer = "LLM not available. Raw contexts:\n\n" + "\n\n---\n\n".join(all_contexts[:5])
        
        return {
            'answer': answer,
            'sources_searched': sources,
            'contexts_found': len(all_contexts),
            'retrieval_stats': retrieval_stats,
            'source_metadata': source_metadata
        }
    
    def _synthesize_with_style(self, query: str, contexts: List[str], 
                              metadata: List[Dict], style: str) -> str:
        """Synthesize answer with specific style"""
        # Build context string
        context = "\n\n".join(contexts)
        
        # Style-specific prompts
        if style == 'concise':
            prompt = f"""You are DT, providing quick, focused answers for daily use.
Based on the context, answer concisely (2-3 paragraphs max).

Context: {context}

Question: {query}

Provide a clear, direct answer focusing on the most relevant information."""
        
        elif style == 'timeline':
            prompt = f"""You are DT, analyzing historical patterns and evolution.
Based on the context, create a timeline-focused answer showing progression and key events.

Context: {context}

Question: {query}

Structure your answer chronologically, highlighting:
- Key dates and milestones
- Evolution of concepts/systems
- Important transitions
- Patterns of growth"""
        
        elif style == 'technical':
            prompt = f"""You are DT, providing technical implementation details.
Based on the context, focus on code, configurations, and technical specifics.

Context: {context}

Question: {query}

Include:
- File paths and locations
- Code snippets or configurations
- Technical implementation details
- Practical usage examples"""
        
        elif style == 'comprehensive':
            prompt = f"""You are DT, providing comprehensive analysis across all knowledge sources.
Based on the extensive context, create a thorough, well-structured response.

Context: {context}

Question: {query}

Provide a detailed analysis that:
- Synthesizes information from multiple sources
- Identifies key themes and connections
- Offers deep insights
- Maintains clear organization"""
        
        else:  # standard
            prompt = f"""You are DT, with access to your federation knowledge.
Based on the context, answer the question comprehensively.

Context: {context}

Question: {query}

Provide a well-structured answer that addresses the query directly."""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error generating synthesis: {e}")
            return f"Synthesis error: {e}\n\nTop contexts:\n\n" + "\n\n---\n\n".join(contexts[:3])
    
    def clear_all_caches(self):
        """Clear all caches"""
        for cache in self.caches.values():
            cache.clear()
        return "All RAG caches cleared successfully"
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        stats = {}
        for cache_type, cache in self.caches.items():
            stats[cache_type] = len(cache)
        return stats


# Initialize enhanced RAG system
rag_v2 = DTFederationRAGv2()


# MCP Tool Definitions

@mcp.tool()
def rag_query(query: str) -> Dict[str, Any]:
    """
    Fast daily driver RAG - Current context from memories + knowledge graph + notes
    
    Best for:
    - "What are we working on?"
    - "Remind me about X"
    - Current state questions
    - Quick context lookups
    
    Sources: ChromaDB memories, Knowledge Graph, Obsidian notes
    Cache: 5 minutes
    """
    return rag_v2.query_daily(query)


@mcp.tool()
def rag_query_history(query: str) -> Dict[str, Any]:
    """
    Timeline explorer RAG - Includes historical JSON data for evolution patterns
    
    Best for:
    - "How did we develop X?"
    - "When did we implement Y?"
    - Evolution and timeline questions
    - Historical context
    
    Sources: All daily sources + Legacy JSON memories
    Cache: 1 hour
    """
    return rag_v2.query_history(query)


@mcp.tool()
def rag_query_files(query: str) -> Dict[str, Any]:
    """
    Code hunter RAG - Search Federation files and technical documentation
    
    Best for:
    - "Where is X implemented?"
    - "Find the code for Y"
    - Configuration files
    - Technical implementation details
    - BUILD documentation
    - Process documentation
    
    Sources: Federation files (7,884 Python + 848 Markdown) + Obsidian technical docs
    NOT included: Memory collections (use rag_query for that)
    Cache: 30 minutes
    """
    return rag_v2.query_files(query)


@mcp.tool()
def rag_query_full(query: str) -> Dict[str, Any]:
    """
    Deep research RAG - Comprehensive search across all 6 sources
    
    Best for:
    - Complex analysis questions
    - "Everything about X"
    - Comprehensive overviews
    - Deep research tasks
    
    Sources: ALL (memories, knowledge graph, notes, files, legacy)
    Cache: 15 minutes
    """
    return rag_v2.query_full(query)


@mcp.tool()
def rag_auto(query: str, min_results: int = 3) -> Dict[str, Any]:
    """
    Smart auto-routing RAG with cascading search
    
    Automatically detects intent and routes to the best tool:
    - Code/file queries → rag_query_files
    - History/timeline → rag_query_history  
    - Comprehensive requests → rag_query_full
    - Default → rag_query (daily)
    
    Cascades to broader search if insufficient results found.
    
    Args:
        query: Your question
        min_results: Minimum contexts before cascading (default: 3)
    """
    return rag_v2.query_auto(query, min_results)


@mcp.tool()
def rag_cache_stats() -> Dict[str, Any]:
    """
    Get RAG cache statistics
    
    Shows number of cached queries per tool type
    """
    stats = rag_v2.get_cache_stats()
    return {
        'cache_stats': stats,
        'cache_strategies': {k: str(v) for k, v in CACHE_STRATEGIES.items()},
        'total_cached': sum(stats.values())
    }


@mcp.tool()
def rag_clear_cache(cache_type: Optional[str] = None) -> str:
    """
    Clear RAG query cache
    
    Args:
        cache_type: Optional - clear specific cache (daily/history/files/full/auto)
                   If not specified, clears all caches
    """
    if cache_type and cache_type in rag_v2.caches:
        rag_v2.caches[cache_type].clear()
        return f"Cleared {cache_type} cache"
    else:
        return rag_v2.clear_all_caches()


@mcp.tool()
def rag_sources() -> Dict[str, Any]:
    """
    List available DT RAG sources and tools
    
    Shows all specialized query tools and their source configurations
    """
    available_retrievers = list(rag_v2.retrievers.keys())
    
    # Check lazy-loaded retrievers
    if rag_v2._federation_files_initialized:
        if 'federation_files' not in available_retrievers:
            available_retrievers.append('federation_files')
    if rag_v2._legacy_memories_initialized:
        if 'legacy_memories' not in available_retrievers:
            available_retrievers.append('legacy_memories')
    
    return {
        'instance': 'DT (Desktop Claude)',
        'version': 'v2 - Specialized Tools',
        'available_retrievers': available_retrievers,
        'specialized_tools': {
            'rag_query': 'Fast daily driver (memories + knowledge + notes)',
            'rag_query_history': 'Timeline explorer (+ legacy JSON)',
            'rag_query_files': 'Code hunter (Federation files + docs)',
            'rag_query_full': 'Deep research (all 6 sources)',
            'rag_auto': 'Smart routing with cascading'
        },
        'cache_ttls': {k: str(v) for k, v in CACHE_STRATEGIES.items()},
        'total_sources': 6
    }


if __name__ == "__main__":
    # Test the enhanced system
    print("DT Federation RAG v2 - Specialized Tools Edition")
    print("=" * 60)
    
    sources_info = rag_sources()
    print(f"Instance: {sources_info['instance']}")
    print(f"Version: {sources_info['version']}")
    print(f"\nSpecialized Tools:")
    for tool, desc in sources_info['specialized_tools'].items():
        print(f"  - {tool}: {desc}")
    
    print("\nCache Strategies:")
    for cache_type, ttl in sources_info['cache_ttls'].items():
        print(f"  - {cache_type}: {ttl}")
    
    print(f"\nTotal available sources: {sources_info['total_sources']}")