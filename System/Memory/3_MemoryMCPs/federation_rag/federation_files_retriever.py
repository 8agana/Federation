#!/usr/bin/env python3
"""
Federation File System Retriever
Searches across the complete Federation directory structure for implementation context
"""

import os
import re
import time
import logging
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class FederationFilesRetriever:
    """Retriever for Federation file system content"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.supported_extensions = ['.py', '.md', '.json', '.txt', '.sh', '.yaml', '.yml', '.js', '.ts']
        self.files_index = {}
        self.load_time = None
        self._load_files()
        
    def _load_files(self):
        """Recursively scan and index Federation directory files"""
        start_time = time.time()
        file_count = 0
        
        logger.info(f"Federation Files: Starting to index files in {self.base_path}")
        
        try:
            for root, dirs, files in os.walk(self.base_path):
                # Skip common unwanted directories and symlinked directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                    '__pycache__', 'node_modules', 'venv', '.git', '.DS_Store'
                ] and not os.path.islink(os.path.join(root, d))]
                
                for file in files:
                    if any(file.endswith(ext) for ext in self.supported_extensions):
                        filepath = os.path.join(root, file)
                        
                        # Skip symlinks to avoid duplicate Obsidian vault indexing
                        if os.path.islink(filepath):
                            logger.debug(f"Federation Files: Skipping symlink {filepath}")
                            continue
                            
                        try:
                            self._index_file(filepath)
                            file_count += 1
                        except Exception as e:
                            logger.warning(f"Federation Files: Could not index {filepath}: {e}")
            
            self.load_time = time.time() - start_time
            logger.info(f"Federation Files: Indexed {file_count} files in {self.load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Federation Files: Error loading files from {self.base_path}: {e}")
    
    def _index_file(self, filepath: str):
        """Index a single file with metadata and content preview"""
        try:
            stat_info = os.stat(filepath)
            file_size = stat_info.st_size
            
            # Skip very large files to avoid memory issues
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                logger.debug(f"Federation Files: Skipping large file {filepath} ({file_size} bytes)")
                return
            
            # Get relative path from Federation base
            rel_path = os.path.relpath(filepath, self.base_path)
            
            # Read file content (with encoding fallback)
            content = ""
            content_preview = ""
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(filepath, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception:
                    content = "[Binary or unreadable file]"
            
            # Create content preview (first 500 characters)
            if content and content != "[Binary or unreadable file]":
                content_preview = content[:500] + ("..." if len(content) > 500 else "")
            
            # Extract file metadata
            file_ext = Path(filepath).suffix
            file_name = Path(filepath).name
            
            # Store indexed file information
            self.files_index[filepath] = {
                'rel_path': rel_path,
                'name': file_name,
                'extension': file_ext,
                'size': file_size,
                'modified': datetime.fromtimestamp(stat_info.st_mtime),
                'content': content,
                'content_preview': content_preview,
                'directory': os.path.dirname(rel_path)
            }
            
        except Exception as e:
            logger.warning(f"Federation Files: Error indexing {filepath}: {e}")
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract meaningful search terms from natural language queries"""
        # Convert to lowercase for processing
        query_lower = query.lower()
        
        # Key terms that indicate important concepts
        key_terms = []
        
        # Extract specific technical concepts
        concept_patterns = {
            'config': ['config', 'configuration', 'settings', 'setup'],
            'implementation': ['implementation', 'implement', 'code', 'build'],
            'federation': ['federation', 'system', 'architecture'],
            'memory': ['memory', 'memories', 'chromadb', 'storage'],
            'rag': ['rag', 'retrieval', 'search', 'query'],
            'mcp': ['mcp', 'server', 'protocol'],
            'obsidian': ['obsidian', 'vault', 'notes'],
            'knowledge': ['knowledge', 'graph', 'semantic'],
            'testing': ['test', 'testing', 'validation', 'debug'],
            'documentation': ['doc', 'documentation', 'readme', 'guide'],
            'script': ['script', 'automation', 'tool'],
            'api': ['api', 'endpoint', 'interface'],
            'database': ['database', 'db', 'sql'],
            'browser': ['browser', 'gui', 'interface'],
            'migration': ['migration', 'import', 'export'],
            'enhancement': ['enhancement', 'improvement', 'upgrade']
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
        
        # Extract capitalized words (likely entities/names)
        capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', query)
        key_terms.extend([word.lower() for word in capitalized_words])
        
        # Extract meaningful words (4+ chars, excluding stopwords)
        stopwords = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 
            'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 
            'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'way', 'many', 'then', 'them', 'these', 
            'some', 'would', 'like', 'into', 'time', 'very', 'when', 'come', 'here', 'just', 'know', 
            'long', 'make', 'much', 'over', 'such', 'take', 'than', 'well', 'were', 'what', 'with', 
            'have', 'from', 'they', 'been', 'said', 'each', 'which', 'their', 'will', 'about', 'there', 
            'could', 'other', 'after', 'first', 'never', 'think', 'where', 'being', 'every', 'great', 
            'might', 'shall', 'still', 'those', 'under', 'while', 'should', 'through', 'before', 'little', 
            'right', 'something', 'without', 'between', 'against', 'during', 'another', 'because', 
            'around', 'though', 'however', 'together', 'important', 'different'
        }
        
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
        
        return unique_terms[:15]  # Limit to top 15 terms
    
    def _score_file_match(self, file_data: Dict, search_terms: List[str]) -> tuple:
        """Score how well a file matches the search terms"""
        match_score = 0
        matched_terms = []
        match_details = []
        
        # File name matches (highest weight)
        name_lower = file_data['name'].lower()
        for term in search_terms:
            if term in name_lower:
                match_score += 5
                matched_terms.append(term)
                match_details.append(f"filename:{term}")
        
        # Path matches (high weight)
        path_lower = file_data['rel_path'].lower()
        for term in search_terms:
            if term in path_lower and term not in matched_terms:
                match_score += 3
                matched_terms.append(term)
                match_details.append(f"path:{term}")
        
        # Content matches (medium weight)
        if file_data['content'] and file_data['content'] != "[Binary or unreadable file]":
            content_lower = file_data['content'].lower()
            for term in search_terms:
                if term in content_lower and term not in matched_terms:
                    # Count occurrences for frequency bonus
                    count = content_lower.count(term)
                    score_bonus = min(count, 5)  # Cap at 5 occurrences
                    match_score += score_bonus
                    matched_terms.append(term)
                    match_details.append(f"content:{term}({count}x)")
        
        # File extension bonus for relevant file types
        ext_lower = file_data['extension'].lower()
        ext_bonuses = {
            '.py': 2,     # Python implementation files
            '.md': 2,     # Documentation files
            '.json': 1,   # Configuration files
            '.sh': 1,     # Script files
            '.yaml': 1,   # Configuration files
            '.yml': 1     # Configuration files
        }
        
        if ext_lower in ext_bonuses:
            match_score += ext_bonuses[ext_lower]
            match_details.append(f"ext_bonus:{ext_lower}")
        
        return match_score, matched_terms, match_details
    
    def retrieve(self, query: str, k: int = 5, filter_dict: Dict = None) -> List[Dict]:
        """Retrieve relevant files from Federation directory"""
        try:
            if not self.files_index:
                logger.warning("Federation Files: No files indexed")
                return []
            
            # Extract search terms from query
            search_terms = self._extract_search_terms(query)
            logger.info(f"Federation Files: Extracted search terms from '{query[:50]}...': {search_terms}")
            
            results = []
            
            # Score all files
            for filepath, file_data in self.files_index.items():
                match_score, matched_terms, match_details = self._score_file_match(file_data, search_terms)
                
                if match_score > 0:
                    # Create result entry
                    results.append({
                        'content': self._format_file_result(file_data, matched_terms, match_details),
                        'metadata': {
                            'type': 'federation_file',
                            'filepath': filepath,
                            'rel_path': file_data['rel_path'],
                            'filename': file_data['name'],
                            'extension': file_data['extension'],
                            'size': file_data['size'],
                            'modified': file_data['modified'].isoformat(),
                            'directory': file_data['directory'],
                            'match_score': match_score,
                            'matched_terms': matched_terms,
                            'match_details': match_details
                        },
                        'source': 'federation_files'
                    })
            
            # Sort by match score (highest first) and limit results
            results.sort(key=lambda x: x['metadata']['match_score'], reverse=True)
            
            logger.info(f"Federation Files: Found {len(results)} matches, returning top {k}")
            return results[:k]
            
        except Exception as e:
            logger.error(f"Federation Files: Error retrieving files: {e}")
            return []
    
    def _format_file_result(self, file_data: Dict, matched_terms: List[str], match_details: List[str]) -> str:
        """Format file information for result display"""
        content_preview = file_data['content_preview'] if file_data['content_preview'] else "[No content preview]"
        
        # Format file info
        result = f"Federation File: {file_data['rel_path']}\n"
        result += f"Type: {file_data['extension']} ({file_data['size']} bytes)\n"
        result += f"Modified: {file_data['modified'].strftime('%Y-%m-%d %H:%M')}\n"
        result += f"Matched Terms: {matched_terms}\n"
        result += f"Match Details: {match_details}\n"
        result += f"Content Preview:\n{content_preview}"
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about indexed files"""
        if not self.files_index:
            return {'error': 'No files indexed'}
        
        # Count by extension
        ext_counts = {}
        total_size = 0
        
        for file_data in self.files_index.values():
            ext = file_data['extension']
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
            total_size += file_data['size']
        
        return {
            'total_files': len(self.files_index),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'extensions': ext_counts,
            'load_time_seconds': self.load_time,
            'base_path': self.base_path
        }

# Test function
def test_federation_files_retriever():
    """Test the Federation Files Retriever"""
    print("Testing Federation Files Retriever...")
    
    base_path = "/Users/samuelatagana/Documents/Federation"
    retriever = FederationFilesRetriever(base_path)
    
    # Show stats
    stats = retriever.get_stats()
    print(f"Stats: {stats}")
    
    # Test queries
    test_queries = [
        "ChromaDB configuration and setup",
        "RAG implementation and testing",
        "MCP server configuration",
        "Knowledge Graph implementation",
        "Federation architecture"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = retriever.retrieve(query, k=3)
        print(f"Results: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"  {i+1}. {result['metadata']['rel_path']} (score: {result['metadata']['match_score']})")

if __name__ == "__main__":
    test_federation_files_retriever()