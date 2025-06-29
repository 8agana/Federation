#!/usr/bin/env python3
"""
Federation RAG MCP Server
Unified RAG across ChromaDB, Knowledge Graph, and Obsidian
Phase 1 Implementation - Starting with ChromaDB
"""

import os
import sys
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import hashlib
import json
import re
import glob
from pathlib import Path
from dotenv import load_dotenv

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
logger = logging.getLogger("federation_rag")

# Create MCP server
mcp = FastMCP("federation-rag")

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


class ChromaDBRetriever:
    """Retriever for CC and DT ChromaDB memories"""
    
    def __init__(self, collection_name: str, chroma_path: str):
        """Initialize ChromaDB retriever"""
        try:
            self.client = chromadb.PersistentClient(
                path=chroma_path,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_collection(collection_name)
            
            # Create Langchain wrapper
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=collection_name,
                embedding_function=embeddings
            )
            
            logger.info(f"Initialized ChromaDB retriever for {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB retriever: {e}")
            raise
    
    def retrieve(self, query: str, k: int = 5, filter_dict: Dict = None) -> List[Dict]:
        """Retrieve relevant documents"""
        try:
            # Use metadata filtering if provided
            if filter_dict:
                results = self.vectorstore.similarity_search(
                    query, 
                    k=k,
                    filter=filter_dict
                )
            else:
                results = self.vectorstore.similarity_search(query, k=k)
            
            # Convert to consistent format
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'source': f'chromadb_{self.collection.name}'
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error retrieving from ChromaDB: {e}")
            return []


class KnowledgeGraphRetriever:
    """Retriever for CC's Knowledge Graph"""
    
    def __init__(self, obsidian_path: str):
        """Initialize Knowledge Graph retriever"""
        self.obsidian_path = obsidian_path
        self.entities = {}
        self.relations = {}
        self.observations = {}
        self._load_knowledge_graph()
        logger.info("Knowledge Graph retriever initialized")
    
    def _load_knowledge_graph(self):
        """Load knowledge graph data from Obsidian notes"""
        try:
            # Scan all markdown files in the Obsidian vault
            pattern = os.path.join(self.obsidian_path, "**/*.md")
            for filepath in glob.glob(pattern, recursive=True):
                self._parse_note_for_kg_data(filepath)
        except Exception as e:
            logger.error(f"Error loading knowledge graph: {e}")
    
    def _parse_note_for_kg_data(self, filepath: str):
        """Parse a note file for knowledge graph entities, relations, and observations"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract entities (lines starting with ## Entity:)
            entity_matches = re.findall(r'^## Entity: (.+)$', content, re.MULTILINE)
            for entity in entity_matches:
                self.entities[entity.strip()] = {
                    'source_file': filepath,
                    'content': content
                }
            
            # Extract relations (lines with -> )
            relation_matches = re.findall(r'(.+?)\s*->\s*(.+)', content)
            for source, target in relation_matches:
                if source.strip() and target.strip():
                    rel_key = f"{source.strip()}->{target.strip()}"
                    self.relations[rel_key] = {
                        'source': source.strip(),
                        'target': target.strip(),
                        'source_file': filepath
                    }
            
            # Extract observations (lines starting with - **Observation:**)
            obs_matches = re.findall(r'^\s*-\s*\*\*Observation:\*\*\s*(.+)$', content, re.MULTILINE)
            for i, obs in enumerate(obs_matches):
                obs_key = f"{filepath}_{i}"
                self.observations[obs_key] = {
                    'content': obs.strip(),
                    'source_file': filepath
                }
                
        except Exception as e:
            logger.error(f"Error parsing note {filepath}: {e}")
    
    def retrieve(self, query: str, k: int = 5, filter_dict: Dict = None) -> List[Dict]:
        """Retrieve relevant knowledge graph information"""
        try:
            results = []
            query_lower = query.lower()
            
            # Search entities
            for entity, data in self.entities.items():
                if query_lower in entity.lower():
                    results.append({
                        'content': f"Entity: {entity}\nContext: {data['content'][:500]}...",
                        'metadata': {
                            'type': 'entity',
                            'entity_name': entity,
                            'source_file': data['source_file']
                        },
                        'source': 'knowledge_graph'
                    })
            
            # Search relations
            for rel_key, data in self.relations.items():
                if query_lower in rel_key.lower():
                    results.append({
                        'content': f"Relation: {data['source']} -> {data['target']}",
                        'metadata': {
                            'type': 'relation',
                            'source_entity': data['source'],
                            'target_entity': data['target'],
                            'source_file': data['source_file']
                        },
                        'source': 'knowledge_graph'
                    })
            
            # Search observations
            for obs_key, data in self.observations.items():
                if query_lower in data['content'].lower():
                    results.append({
                        'content': f"Observation: {data['content']}",
                        'metadata': {
                            'type': 'observation',
                            'source_file': data['source_file']
                        },
                        'source': 'knowledge_graph'
                    })
            
            # Sort by relevance and limit results
            return results[:k]
            
        except Exception as e:
            logger.error(f"Error retrieving from knowledge graph: {e}")
            return []


class ObsidianRetriever:
    """Retriever for Obsidian notes in SharedVault and Nerve Center"""
    
    def __init__(self, vault_paths: List[str]):
        """Initialize Obsidian retriever"""
        self.vault_paths = vault_paths
        self.notes = {}
        self._load_notes()
        logger.info(f"Obsidian retriever initialized with {len(self.notes)} notes")
    
    def _load_notes(self):
        """Load all notes from the specified vaults"""
        for vault_path in self.vault_paths:
            if os.path.exists(vault_path):
                pattern = os.path.join(vault_path, "**/*.md")
                for filepath in glob.glob(pattern, recursive=True):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Extract title from filename or first heading
                        title = os.path.basename(filepath).replace('.md', '')
                        if content.startswith('# '):
                            title = content.split('\n')[0][2:].strip()
                        
                        self.notes[filepath] = {
                            'title': title,
                            'content': content,
                            'vault': vault_path,
                            'modified': datetime.fromtimestamp(os.path.getmtime(filepath))
                        }
                    except Exception as e:
                        logger.error(f"Error loading note {filepath}: {e}")
    
    def retrieve(self, query: str, k: int = 5, filter_dict: Dict = None) -> List[Dict]:
        """Retrieve relevant Obsidian notes"""
        try:
            results = []
            query_lower = query.lower()
            
            for filepath, note_data in self.notes.items():
                title = note_data['title']
                content = note_data['content']
                
                # Score based on title and content matches
                score = 0
                if query_lower in title.lower():
                    score += 10
                if query_lower in content.lower():
                    score += content.lower().count(query_lower)
                
                if score > 0:
                    # Extract relevant snippet
                    lines = content.split('\n')
                    relevant_snippet = []
                    for line in lines:
                        if query_lower in line.lower():
                            relevant_snippet.append(line.strip())
                        if len(relevant_snippet) >= 5:  # Limit snippet size
                            break
                    
                    if not relevant_snippet:
                        relevant_snippet = lines[:3]  # Fallback to first few lines
                    
                    results.append({
                        'content': f"Note: {title}\n\n" + "\n".join(relevant_snippet),
                        'metadata': {
                            'title': title,
                            'file_path': filepath,
                            'vault': note_data['vault'],
                            'modified': note_data['modified'].isoformat(),
                            'score': score
                        },
                        'source': 'obsidian_notes'
                    })
            
            # Sort by score and return top k
            results.sort(key=lambda x: x['metadata']['score'], reverse=True)
            return results[:k]
            
        except Exception as e:
            logger.error(f"Error retrieving from Obsidian: {e}")
            return []


class FederationRAG:
    """Main orchestrator for federated RAG queries"""
    
    def __init__(self):
        """Initialize the Federation RAG system"""
        self.retrievers = {}
        
        # Initialize ChromaDB retrievers
        try:
            # CC memories
            self.retrievers['cc_memories'] = ChromaDBRetriever(
                collection_name="cc_memories",
                chroma_path="/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation"
            )
            logger.info("CC memories retriever initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize CC memories: {e}")
        
        try:
            # DT memories  
            self.retrievers['dt_memories'] = ChromaDBRetriever(
                collection_name="dt_memories",
                chroma_path="/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/dt-federation"
            )
            logger.info("DT memories retriever initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize DT memories: {e}")
        
        # Initialize Knowledge Graph retriever
        try:
            self.retrievers['knowledge_graph'] = KnowledgeGraphRetriever(
                obsidian_path="/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center"
            )
            logger.info("Knowledge Graph retriever initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Knowledge Graph: {e}")
        
        # Initialize Obsidian retriever
        try:
            vault_paths = [
                "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault",
                "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center"
            ]
            self.retrievers['obsidian_notes'] = ObsidianRetriever(vault_paths)
            logger.info("Obsidian retriever initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Obsidian retriever: {e}")
        
        self.llm = llm
        
        # Simple cache for repeated queries
        self.cache = {}
        self.cache_ttl = timedelta(minutes=15)
    
    def _get_cache_key(self, query: str, sources: List[str]) -> str:
        """Generate cache key for query"""
        source_str = "_".join(sorted(sources))
        return hashlib.md5(f"{query}_{source_str}".encode()).hexdigest()
    
    def federated_query(self, query: str, sources: List[str] = None) -> Dict[str, Any]:
        """Query across multiple sources with RAG"""
        
        # Default to all available sources
        if not sources:
            sources = list(self.retrievers.keys())
        
        # Check cache
        cache_key = self._get_cache_key(query, sources)
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                logger.info("Returning cached result")
                return cached_result
        
        # Collect contexts from all sources
        all_contexts = []
        source_metadata = []
        retrieval_stats = {}
        
        for source in sources:
            if source in self.retrievers:
                try:
                    start_time = datetime.now()
                    results = self.retrievers[source].retrieve(query)
                    retrieval_time = (datetime.now() - start_time).total_seconds()
                    
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
        
        # If no LLM available, return contexts directly
        if not self.llm:
            return {
                'answer': "LLM not available. Raw contexts:\n\n" + "\n\n---\n\n".join(all_contexts),
                'sources_searched': sources,
                'contexts_found': len(all_contexts),
                'retrieval_stats': retrieval_stats,
                'source_metadata': source_metadata
            }
        
        # Build context for LLM
        context = "\n\n".join(all_contexts)
        
        # Create prompt
        prompt = f"""You are a helpful assistant with access to multiple knowledge sources.
        
Based on the following context from various sources, answer the question comprehensively.
If information comes from different sources, synthesize it intelligently.
Be specific and cite which insights come from which sources when relevant.

Context:
{context}

Question: {query}

Provide a detailed, well-structured answer that integrates information from all relevant sources."""

        # Generate response
        try:
            response = self.llm.invoke(prompt)
            answer = response.content
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            answer = f"Error generating response: {e}\n\nRaw contexts:\n\n" + "\n\n---\n\n".join(all_contexts)
        
        result = {
            'answer': answer,
            'sources_searched': sources,
            'contexts_found': len(all_contexts),
            'retrieval_stats': retrieval_stats,
            'source_metadata': source_metadata
        }
        
        # Cache the result
        self.cache[cache_key] = (result, datetime.now())
        
        return result
    
    def clear_cache(self):
        """Clear the query cache"""
        self.cache.clear()
        return "Cache cleared successfully"


# Initialize RAG system
rag = FederationRAG()


# MCP Tool Definitions
@mcp.tool()
def rag_query(query: str, sources: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Query Federation data sources using RAG
    
    Args:
        query: Your question or search query
        sources: Optional list of sources to search. 
                Available: cc_memories, dt_memories, knowledge_graph, obsidian_notes
                (defaults to all available sources)
    
    Returns:
        Dictionary with:
        - answer: Synthesized response
        - sources_searched: List of sources queried
        - contexts_found: Number of relevant contexts
        - retrieval_stats: Performance stats per source
    """
    return rag.federated_query(query, sources)


@mcp.tool()
def rag_sources() -> Dict[str, List[str]]:
    """
    List available RAG sources
    
    Returns:
        Dictionary with available sources and their status
    """
    available = list(rag.retrievers.keys())
    planned = ['gmail', 'google_drive', 'calendar', 'file_system']
    
    return {
        'available': available,
        'planned': planned,
        'total_available': len(available)
    }


@mcp.tool()
def rag_clear_cache() -> str:
    """
    Clear the RAG query cache
    
    Returns:
        Confirmation message
    """
    return rag.clear_cache()


@mcp.tool() 
def rag_test() -> Dict[str, Any]:
    """
    Test RAG system with a sample query
    
    Returns:
        Test results showing system functionality
    """
    test_query = "What is RAG and how does it work?"
    result = rag.federated_query(test_query)
    
    return {
        'test_query': test_query,
        'system_status': 'operational' if result['contexts_found'] > 0 else 'no data found',
        'llm_status': 'available' if rag.llm else 'not configured (set GROQ_API_KEY)',
        'sources_available': list(rag.retrievers.keys()),
        'result_preview': result['answer'][:200] + '...' if len(result['answer']) > 200 else result['answer']
    }


if __name__ == "__main__":
    # Test the system
    print("Federation RAG MCP Server")
    print("Testing system...")
    
    test_result = rag_test()
    print(f"Status: {test_result['system_status']}")
    print(f"LLM: {test_result['llm_status']}")
    print(f"Sources: {test_result['sources_available']}")