#!/usr/bin/env python3
"""
DT Federation RAG MCP Server
DT-specific RAG across DT ChromaDB, DT Nerve Center, and SharedVault
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
logger = logging.getLogger("dt_federation_rag")

# Create MCP server
mcp = FastMCP("dt-federation-rag")

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
    """Retriever for ChromaDB memories"""
    
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
    """Retriever for DT's Knowledge Graph (DT Nerve Center only)"""
    
    def __init__(self, obsidian_path: str):
        """Initialize Knowledge Graph retriever"""
        self.obsidian_path = obsidian_path
        self.entities = {}
        self.relations = {}
        self.observations = {}
        self._load_knowledge_graph()
        logger.info(f"DT Knowledge Graph retriever initialized: {len(self.entities)} entities, {len(self.relations)} relations, {len(self.observations)} observations")
    
    def _load_knowledge_graph(self):
        """Load knowledge graph data from DT Nerve Center only"""
        try:
            # Scan all markdown files in the DT Nerve Center
            pattern = os.path.join(self.obsidian_path, "**/*.md")
            for filepath in glob.glob(pattern, recursive=True):
                self._parse_note_for_kg_data(filepath)
        except Exception as e:
            logger.error(f"Error loading DT knowledge graph: {e}")
    
    def _parse_note_for_kg_data(self, filepath: str):
        """Parse a note file for DT's knowledge graph entities, relations, and observations"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract entities (lines starting with ## Entity: OR file titles as entities)
            entity_matches = re.findall(r'^## Entity: (.+)$', content, re.MULTILINE)
            for entity in entity_matches:
                self.entities[entity.strip()] = {
                    'source_file': filepath,
                    'content': content,
                    'type': 'explicit_entity'
                }
            
            # Also treat file titles as entities
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
                self.entities[title] = {
                    'source_file': filepath,
                    'content': content,
                    'type': 'title_entity'
                }
            
            # Extract DT-style relations (lines with [[Target]])
            # Pattern: - relation_type [[Target]]
            relation_matches = re.findall(r'^\s*-\s*(.+?)\s*\[\[(.+?)\]\]', content, re.MULTILINE)
            for relation_type, target in relation_matches:
                source_title = title_match.group(1).strip() if title_match else os.path.basename(filepath)
                rel_key = f"{source_title}->{target.strip()}"
                self.relations[rel_key] = {
                    'source': source_title,
                    'target': target.strip(),
                    'relation_type': relation_type.strip(),
                    'source_file': filepath
                }
            
            # Extract DT-style observations (lines starting with - [category])
            # Pattern: - [category] content #tags (additional notes)
            obs_matches = re.findall(r'^\s*-\s*\[([^\]]+)\]\s*(.+)$', content, re.MULTILINE)
            for i, (category, obs_content) in enumerate(obs_matches):
                obs_key = f"{filepath}_{i}"
                self.observations[obs_key] = {
                    'content': obs_content.strip(),
                    'category': category.strip(),
                    'source_file': filepath
                }
            
            # Also extract traditional observations for compatibility
            traditional_obs_matches = re.findall(r'^\s*-\s*\*\*Observation:\*\*\s*(.+)$', content, re.MULTILINE)
            for i, obs in enumerate(traditional_obs_matches):
                obs_key = f"{filepath}_traditional_{i}"
                self.observations[obs_key] = {
                    'content': obs.strip(),
                    'category': 'observation',
                    'source_file': filepath
                }
                
        except Exception as e:
            logger.error(f"Error parsing DT note {filepath}: {e}")
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract meaningful search terms from natural language queries"""
        import re
        
        # Convert to lowercase for processing
        query_lower = query.lower()
        
        # Key terms that indicate important concepts
        key_terms = []
        
        # Extract specific important concepts
        concept_patterns = {
            'identity': ['identity', 'who am i', 'who i am', 'core self', 'personality'],
            'memory': ['memory', 'memories', 'remember', 'recall', 'past'],
            'relationship': ['relationship', 'partnership', 'collaboration', 'team'],
            'project': ['project', 'work', 'task', 'development', 'building'],
            'context': ['context', 'background', 'history', 'situation'],
            'recent': ['recent', 'latest', 'current', 'now', 'today'],
            'sam': ['sam', 'samuel', 'partner'],
            'cc': ['cc', 'claude code', 'builder'],
            'dt': ['dt', 'desktop claude', 'thinker'],
            'federation': ['federation', 'system', 'architecture'],
            'rag': ['rag', 'retrieval', 'search'],
            'breakthrough': ['breakthrough', 'discovery', 'success'],
            'trips': ['trips', 'ccc', 'nickname'],
            'nerve center': ['nerve center', 'obsidian', 'knowledge'],
            'testing': ['testing', 'validation', 'analysis']
        }
        
        # Check for concept matches
        for concept, patterns in concept_patterns.items():
            for pattern in patterns:
                if pattern in query_lower:
                    key_terms.append(concept)
                    break
        
        # Extract quoted phrases (exact matches)
        quoted_phrases = re.findall(r'"([^"]+)"', query)
        key_terms.extend([phrase.lower() for phrase in quoted_phrases])
        
        # Extract capitalized words (likely entities)
        capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', query)
        key_terms.extend([word.lower() for word in capitalized_words])
        
        # Extract words longer than 3 characters, excluding common stopwords
        stopwords = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'her', 'way', 'many', 'then', 'them', 'these', 'some', 'would', 'like', 'into', 'time', 'very', 'when', 'come', 'here', 'just', 'know', 'long', 'make', 'much', 'over', 'such', 'take', 'than', 'them', 'well', 'were', 'what', 'with', 'have', 'from', 'they', 'been', 'said', 'each', 'which', 'their', 'will', 'about', 'there', 'could', 'other', 'after', 'first', 'never', 'these', 'think', 'where', 'being', 'every', 'great', 'might', 'shall', 'still', 'those', 'under', 'while', 'should', 'through', 'before', 'little', 'right', 'something', 'without', 'between', 'against', 'during', 'another', 'because', 'around', 'though', 'however', 'together', 'important', 'different'}
        
        words = re.findall(r'\b\w{4,}\b', query_lower)
        meaningful_words = [word for word in words if word not in stopwords]
        key_terms.extend(meaningful_words)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in key_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        return unique_terms[:10]  # Limit to top 10 terms
    
    def retrieve(self, query: str, k: int = 5, filter_dict: Dict = None) -> List[Dict]:
        """Retrieve relevant knowledge graph information"""
        try:
            results = []
            
            # Extract search terms from the query
            search_terms = self._extract_search_terms(query)
            logger.info(f"DT Knowledge Graph: Extracted search terms from '{query[:50]}...': {search_terms}")
            logger.info(f"DT Knowledge Graph: Searching in {len(self.entities)} entities, {len(self.relations)} relations, {len(self.observations)} observations")
            
            # Search entities with extracted terms
            for entity, data in self.entities.items():
                entity_lower = entity.lower()
                match_score = 0
                matched_terms = []
                
                # Check for term matches in entity name
                for term in search_terms:
                    if term in entity_lower:
                        match_score += 2  # Entity name matches are high value
                        matched_terms.append(term)
                
                # Check for term matches in entity content
                content_lower = data['content'].lower()
                for term in search_terms:
                    if term in content_lower and term not in matched_terms:
                        match_score += 1
                        matched_terms.append(term)
                
                if match_score > 0:
                    entity_type = data.get('type', 'entity')
                    results.append({
                        'content': f"Entity: {entity}\nType: {entity_type}\nMatched terms: {matched_terms}\nContext: {data['content'][:400]}...",
                        'metadata': {
                            'type': 'entity',
                            'entity_type': entity_type,
                            'entity_name': entity,
                            'source_file': data['source_file'],
                            'match_score': match_score,
                            'matched_terms': matched_terms
                        },
                        'source': 'dt_knowledge_graph'
                    })
            
            # Search relations with extracted terms
            for rel_key, data in self.relations.items():
                rel_lower = rel_key.lower()
                relation_type_lower = data.get('relation_type', '').lower()
                match_score = 0
                matched_terms = []
                
                # Check for term matches in relation key and type
                for term in search_terms:
                    if term in rel_lower or term in relation_type_lower:
                        match_score += 1
                        matched_terms.append(term)
                    
                    # Check if term matches source or target entities
                    if (term in data['source'].lower() or 
                        term in data['target'].lower()):
                        match_score += 1
                        if term not in matched_terms:
                            matched_terms.append(term)
                
                if match_score > 0:
                    results.append({
                        'content': f"Relation: {data['source']} -{data.get('relation_type', 'relates_to')}-> {data['target']}\nMatched terms: {matched_terms}",
                        'metadata': {
                            'type': 'relation',
                            'source_entity': data['source'],
                            'target_entity': data['target'],
                            'relation_type': data.get('relation_type', 'unknown'),
                            'source_file': data['source_file'],
                            'match_score': match_score,
                            'matched_terms': matched_terms
                        },
                        'source': 'dt_knowledge_graph'
                    })
            
            # Search observations with extracted terms
            for obs_key, data in self.observations.items():
                content_lower = data['content'].lower()
                category_lower = data.get('category', '').lower()
                match_score = 0
                matched_terms = []
                
                # Check for term matches in observation content and category
                for term in search_terms:
                    if term in content_lower:
                        match_score += 1
                        matched_terms.append(term)
                    elif term in category_lower:
                        match_score += 1
                        if term not in matched_terms:
                            matched_terms.append(term)
                
                if match_score > 0:
                    category = data.get('category', 'observation')
                    results.append({
                        'content': f"Observation [{category}]: {data['content']}\nMatched terms: {matched_terms}",
                        'metadata': {
                            'type': 'observation',
                            'category': category,
                            'source_file': data['source_file'],
                            'match_score': match_score,
                            'matched_terms': matched_terms
                        },
                        'source': 'dt_knowledge_graph'
                    })
            
            # Sort by match score (higher scores first) and limit results
            results.sort(key=lambda x: x['metadata'].get('match_score', 0), reverse=True)
            
            logger.info(f"DT Knowledge Graph: Found {len(results)} matches for terms: {search_terms}")
            return results[:k]
            
        except Exception as e:
            logger.error(f"Error retrieving from DT knowledge graph: {e}")
            return []


class ObsidianRetriever:
    """Retriever for Obsidian notes (DT Nerve Center + SharedVault)"""
    
    def __init__(self, vault_paths: List[str]):
        """Initialize Obsidian retriever"""
        self.vault_paths = vault_paths
        self.notes = {}
        self._load_notes()
        logger.info(f"DT Obsidian retriever initialized with {len(self.notes)} notes")
    
    def _load_notes(self):
        """Load all notes from the specified vaults"""
        for vault_path in self.vault_paths:
            if os.path.exists(vault_path):
                pattern = os.path.join(vault_path, "**/*.md")
                files_found = glob.glob(pattern, recursive=True)
                logger.info(f"Found {len(files_found)} markdown files in {vault_path}")
                
                for filepath in files_found:
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Extract title from filename or first heading
                        title = os.path.basename(filepath).replace('.md', '')
                        if content.startswith('# '):
                            title = content.split('\n')[0][2:].strip()
                        
                        # Determine vault type for context
                        vault_name = "shared" if "SharedVault" in vault_path else "dt_nerve_center"
                        
                        self.notes[filepath] = {
                            'title': title,
                            'content': content,
                            'vault': vault_name,
                            'vault_path': vault_path,
                            'modified': datetime.fromtimestamp(os.path.getmtime(filepath))
                        }
                    except Exception as e:
                        logger.error(f"Error loading DT note {filepath}: {e}")
                        
        logger.info(f"DT Obsidian: Loaded {len(self.notes)} notes total")
    
    def retrieve(self, query: str, k: int = 5, filter_dict: Dict = None) -> List[Dict]:
        """Retrieve relevant Obsidian notes"""
        try:
            results = []
            query_lower = query.lower()
            logger.info(f"DT Obsidian: Searching {len(self.notes)} notes for '{query}'")
            
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
                    logger.info(f"DT Obsidian: Found match in '{title}' (score: {score})")
                    
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
                        'source': 'dt_obsidian_notes'
                    })
            
            logger.info(f"DT Obsidian: Found {len(results)} matching notes")
            
            # Sort by score and return top k
            results.sort(key=lambda x: x['metadata']['score'], reverse=True)
            return results[:k]
            
        except Exception as e:
            logger.error(f"Error retrieving from DT Obsidian: {e}")
            return []


class DTFederationRAG:
    """DT-specific Federation RAG orchestrator"""
    
    def __init__(self):
        """Initialize the DT Federation RAG system"""
        self.retrievers = {}
        
        # Initialize BOTH ChromaDB retrievers (collaborative memory space)
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
        
        # Initialize DT Knowledge Graph retriever (DT Nerve Center only)
        try:
            self.retrievers['dt_knowledge_graph'] = KnowledgeGraphRetriever(
                obsidian_path="/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center"
            )
            logger.info("DT Knowledge Graph retriever initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize DT Knowledge Graph: {e}")
        
        # Initialize DT Obsidian retriever (DT Nerve Center + SharedVault)
        try:
            vault_paths = [
                "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault",
                "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center"
            ]
            self.retrievers['dt_obsidian_notes'] = ObsidianRetriever(vault_paths)
            logger.info("DT Obsidian retriever initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize DT Obsidian retriever: {e}")
        
        # Initialize Federation Files retriever (7,884 Python + 848 Markdown files)
        try:
            self.retrievers['federation_files'] = FederationFilesRetriever(
                base_path="/Users/samuelatagana/Documents/Federation"
            )
            logger.info("Federation files retriever initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Federation files: {e}")
        
        # Initialize Legacy JSON retriever (~20 historical memory files)
        try:
            self.retrievers['legacy_memories'] = LegacyJSONRetriever(
                json_path="/Users/samuelatagana/Documents/Federation/System/Memory/Legacy_Backups/MemoryJSONS"
            )
            logger.info("Legacy memories retriever initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Legacy memories: {e}")
        
        self.llm = llm
        
        # Simple cache for repeated queries
        self.cache = {}
        self.cache_ttl = timedelta(minutes=15)
    
    def _get_cache_key(self, query: str, sources: List[str]) -> str:
        """Generate cache key for query"""
        source_str = "_".join(sorted(sources))
        return hashlib.md5(f"{query}_{source_str}".encode()).hexdigest()
    
    def federated_query(self, query: str, sources: List[str] = None) -> Dict[str, Any]:
        """Query across DT sources with RAG"""
        
        # Default to all available DT sources
        if not sources:
            sources = list(self.retrievers.keys())
        
        # Check cache
        cache_key = self._get_cache_key(query, sources)
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                logger.info("Returning cached result")
                return cached_result
        
        # Collect contexts from all DT sources
        all_contexts = []
        source_metadata = []
        retrieval_stats = {}
        
        for source in sources:
            if source in self.retrievers:
                try:
                    logger.info(f"DT Federation: Starting retrieval from {source} for query '{query}'")
                    start_time = datetime.now()
                    results = self.retrievers[source].retrieve(query)
                    retrieval_time = (datetime.now() - start_time).total_seconds()
                    
                    logger.info(f"DT Federation: {source} returned {len(results)} results in {retrieval_time:.4f}s")
                    
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
                    import traceback
                    logger.error(f"Full traceback for {source}: {traceback.format_exc()}")
                    retrieval_stats[source] = {'error': str(e)}
            else:
                logger.warning(f"DT Federation: Source {source} not found in retrievers: {list(self.retrievers.keys())}")
        
        # Build response
        if not all_contexts:
            return {
                'answer': "No relevant information found in the searched DT sources.",
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
        prompt = f"""You are DT (Desktop Claude), a helpful assistant with access to your personal knowledge sources.
        
Based on the following context from your DT-specific sources, answer the question comprehensively.
These sources include your memories, your personal knowledge graph, and your private notes plus shared documentation.
If information comes from different sources, synthesize it intelligently.
Be specific and cite which insights come from which sources when relevant.

Context:
{context}

Question: {query}

Provide a detailed, well-structured answer that integrates information from all relevant DT sources."""

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
        return "DT RAG cache cleared successfully"


# Initialize DT RAG system
rag = DTFederationRAG()


# MCP Tool Definitions
@mcp.tool()
def rag_query(query: str, sources: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Query DT Federation data sources using RAG
    
    Args:
        query: Your question or search query
        sources: Optional list of sources to search. 
                Available: cc_memories, dt_memories, dt_knowledge_graph, dt_obsidian_notes, federation_files, legacy_memories
                (defaults to all available DT sources)
    
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
    List available DT RAG sources
    
    Returns:
        Dictionary with available DT sources and their status
    """
    available = list(rag.retrievers.keys())
    planned = ['dt_gmail', 'dt_google_drive', 'dt_calendar']
    
    return {
        'available': available,
        'planned': planned,
        'total_available': len(available),
        'instance': 'DT (Desktop Claude)'
    }


@mcp.tool()
def rag_clear_cache() -> str:
    """
    Clear the DT RAG query cache
    
    Returns:
        Confirmation message
    """
    return rag.clear_cache()


@mcp.tool() 
def rag_test() -> Dict[str, Any]:
    """
    Test DT RAG system with a sample query
    
    Returns:
        Test results showing DT system functionality
    """
    test_query = "What have I learned about collaboration and AI partnerships?"
    result = rag.federated_query(test_query)
    
    return {
        'test_query': test_query,
        'system_status': 'operational' if result['contexts_found'] > 0 else 'no data found',
        'llm_status': 'available' if rag.llm else 'not configured (set GROQ_API_KEY)',
        'sources_available': list(rag.retrievers.keys()),
        'instance': 'DT (Desktop Claude)',
        'result_preview': result['answer'][:200] + '...' if len(result['answer']) > 200 else result['answer']
    }


if __name__ == "__main__":
    # Test the DT system
    print("DT Federation RAG MCP Server")
    print("Testing DT-specific system...")
    
    test_result = rag_test()
    print(f"Status: {test_result['system_status']}")
    print(f"LLM: {test_result['llm_status']}")
    print(f"DT Sources: {test_result['sources_available']}")