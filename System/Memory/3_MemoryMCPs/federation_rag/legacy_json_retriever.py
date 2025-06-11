#!/usr/bin/env python3
"""
Legacy JSON Retriever
Searches through historical memory JSON files for foundational context
"""

import os
import json
import re
import time
import logging
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class LegacyJSONRetriever:
    """Retriever for legacy JSON memory files"""
    
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.memories = {}
        self.load_time = None
        self._load_legacy_jsons()
    
    def _load_legacy_jsons(self):
        """Parse all JSON files in legacy directory"""
        start_time = time.time()
        file_count = 0
        memory_count = 0
        
        logger.info(f"Legacy JSON: Starting to load files from {self.json_path}")
        
        try:
            if not os.path.exists(self.json_path):
                logger.warning(f"Legacy JSON: Path does not exist: {self.json_path}")
                return
            
            for json_file in os.listdir(self.json_path):
                if json_file.endswith('.json') and not json_file.endswith('.backup'):
                    filepath = os.path.join(self.json_path, json_file)
                    try:
                        memories_loaded = self._parse_json_file(filepath)
                        file_count += 1
                        memory_count += memories_loaded
                        logger.debug(f"Legacy JSON: Loaded {memories_loaded} memories from {json_file}")
                    except Exception as e:
                        logger.warning(f"Legacy JSON: Could not parse {json_file}: {e}")
            
            self.load_time = time.time() - start_time
            logger.info(f"Legacy JSON: Loaded {memory_count} memories from {file_count} files in {self.load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Legacy JSON: Error loading files from {self.json_path}: {e}")
    
    def _parse_json_file(self, filepath: str) -> int:
        """Extract searchable content from legacy JSON structure"""
        memories_loaded = 0
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            filename = os.path.basename(filepath)
            source_category = filename.replace('.json', '')
            
            # Handle different JSON structures
            if isinstance(data, dict):
                if 'entries' in data:
                    # New structured format
                    memories_loaded += self._parse_entries_structure(data, filepath, source_category)
                else:
                    # Direct dictionary format
                    memories_loaded += self._parse_direct_structure(data, filepath, source_category)
            elif isinstance(data, list):
                # Array format
                memories_loaded += self._parse_array_structure(data, filepath, source_category)
            
        except json.JSONDecodeError as e:
            logger.warning(f"Legacy JSON: Invalid JSON in {filepath}: {e}")
        except Exception as e:
            logger.warning(f"Legacy JSON: Error parsing {filepath}: {e}")
        
        return memories_loaded
    
    def _parse_entries_structure(self, data: Dict, filepath: str, source_category: str) -> int:
        """Parse entries-based JSON structure"""
        memories_loaded = 0
        
        try:
            entries = data.get('entries', {})
            metadata = entries.get('metadata', {})
            
            # Extract metadata information
            meta_info = {
                'source_file': os.path.basename(filepath),
                'source_category': source_category,
                'schema_version': metadata.get('schema_version', 'unknown'),
                'timestamp': metadata.get('timestamp', 'unknown'),
                'restructured_by': metadata.get('restructured_by', 'unknown')
            }
            
            # Process each entry
            for key, value in entries.items():
                if key != 'metadata' and isinstance(value, dict):
                    memory_key = f"{source_category}_{key}"
                    content = self._extract_content_from_entry(value, key)
                    
                    if content:
                        self.memories[memory_key] = {
                            'content': content,
                            'source_file': filepath,
                            'source_category': source_category,
                            'entry_key': key,
                            'entry_data': value,
                            'metadata': meta_info,
                            'extracted_at': datetime.now().isoformat()
                        }
                        memories_loaded += 1
            
        except Exception as e:
            logger.warning(f"Legacy JSON: Error parsing entries structure in {filepath}: {e}")
        
        return memories_loaded
    
    def _parse_direct_structure(self, data: Dict, filepath: str, source_category: str) -> int:
        """Parse direct dictionary structure"""
        memories_loaded = 0
        
        try:
            for key, value in data.items():
                if isinstance(value, (dict, list, str)):
                    memory_key = f"{source_category}_{key}"
                    content = self._extract_content_recursive(value, key)
                    
                    if content:
                        self.memories[memory_key] = {
                            'content': content,
                            'source_file': filepath,
                            'source_category': source_category,
                            'entry_key': key,
                            'entry_data': value,
                            'metadata': {
                                'source_file': os.path.basename(filepath),
                                'source_category': source_category,
                                'structure_type': 'direct'
                            },
                            'extracted_at': datetime.now().isoformat()
                        }
                        memories_loaded += 1
        
        except Exception as e:
            logger.warning(f"Legacy JSON: Error parsing direct structure in {filepath}: {e}")
        
        return memories_loaded
    
    def _parse_array_structure(self, data: List, filepath: str, source_category: str) -> int:
        """Parse array-based JSON structure"""
        memories_loaded = 0
        
        try:
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    memory_key = f"{source_category}_item_{i}"
                    content = self._extract_content_recursive(item, f"item_{i}")
                    
                    if content:
                        self.memories[memory_key] = {
                            'content': content,
                            'source_file': filepath,
                            'source_category': source_category,
                            'entry_key': f"item_{i}",
                            'entry_data': item,
                            'metadata': {
                                'source_file': os.path.basename(filepath),
                                'source_category': source_category,
                                'structure_type': 'array',
                                'array_index': i
                            },
                            'extracted_at': datetime.now().isoformat()
                        }
                        memories_loaded += 1
        
        except Exception as e:
            logger.warning(f"Legacy JSON: Error parsing array structure in {filepath}: {e}")
        
        return memories_loaded
    
    def _extract_content_from_entry(self, entry_data: Dict, entry_key: str) -> str:
        """Extract meaningful text content from an entry"""
        content_parts = [f"Entry: {entry_key}"]
        
        # Handle different data structures
        if isinstance(entry_data, dict):
            for key, value in entry_data.items():
                if isinstance(value, str) and len(value.strip()) > 0:
                    content_parts.append(f"{key}: {value}")
                elif isinstance(value, dict):
                    # Recurse into nested dictionaries
                    nested_content = self._extract_content_recursive(value, key)
                    if nested_content:
                        content_parts.append(f"{key}: {nested_content}")
                elif isinstance(value, list):
                    # Handle lists
                    list_content = []
                    for item in value:
                        if isinstance(item, str):
                            list_content.append(item)
                        elif isinstance(item, dict):
                            list_content.append(self._extract_content_recursive(item, "list_item"))
                    if list_content:
                        content_parts.append(f"{key}: {'; '.join(list_content)}")
        
        return '\n'.join(content_parts) if len(content_parts) > 1 else ""
    
    def _extract_content_recursive(self, data: Any, prefix: str = "") -> str:
        """Recursively extract text content from nested structures"""
        content_parts = []
        
        if isinstance(data, str):
            if len(data.strip()) > 0:
                return data.strip()
        
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and len(value.strip()) > 0:
                    content_parts.append(f"{key}: {value}")
                elif isinstance(value, (dict, list)):
                    nested_content = self._extract_content_recursive(value, key)
                    if nested_content:
                        content_parts.append(f"{key}: {nested_content}")
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str) and len(item.strip()) > 0:
                    content_parts.append(item)
                elif isinstance(item, dict):
                    nested_content = self._extract_content_recursive(item, f"item_{i}")
                    if nested_content:
                        content_parts.append(nested_content)
        
        return '; '.join(content_parts) if content_parts else ""
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract meaningful search terms from natural language queries"""
        # Convert to lowercase for processing
        query_lower = query.lower()
        
        # Key terms that indicate important concepts
        key_terms = []
        
        # Extract specific historical concepts
        concept_patterns = {
            'identity': ['identity', 'who am i', 'who i am', 'core self', 'personality'],
            'relationship': ['relationship', 'partnership', 'collaboration', 'team'],
            'history': ['history', 'historical', 'past', 'origin', 'beginning'],
            'foundation': ['foundation', 'foundational', 'basic', 'core'],
            'evolution': ['evolution', 'development', 'growth', 'progression'],
            'technical': ['technical', 'implementation', 'system', 'architecture'],
            'photography': ['photography', 'photo', 'image', 'camera'],
            'project': ['project', 'work', 'task', 'development'],
            'memory': ['memory', 'memories', 'remember', 'recall'],
            'sam': ['sam', 'samuel', 'atagana'],
            'ai': ['ai', 'artificial', 'intelligence', 'claude'],
            'legacy': ['legacy', 'old', 'previous', 'former']
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
        
        return unique_terms[:12]  # Limit to top 12 terms
    
    def retrieve(self, query: str, k: int = 5, filter_dict: Dict = None) -> List[Dict]:
        """Retrieve relevant legacy memories with historical context"""
        try:
            if not self.memories:
                logger.warning("Legacy JSON: No memories loaded")
                return []
            
            # Extract search terms from query
            search_terms = self._extract_search_terms(query)
            logger.info(f"Legacy JSON: Extracted search terms from '{query[:50]}...': {search_terms}")
            
            results = []
            
            # Score all memories
            for memory_key, memory_data in self.memories.items():
                match_score = 0
                matched_terms = []
                
                # Search in content
                content_lower = memory_data['content'].lower()
                for term in search_terms:
                    if term in content_lower:
                        # Count occurrences for frequency bonus
                        count = content_lower.count(term)
                        score_bonus = min(count, 3)  # Cap at 3 occurrences
                        match_score += score_bonus
                        matched_terms.append(term)
                
                # Search in source category (file-based matching)
                category_lower = memory_data['source_category'].lower()
                for term in search_terms:
                    if term in category_lower and term not in matched_terms:
                        match_score += 2  # Category matches are important
                        matched_terms.append(term)
                
                # Search in entry key
                entry_key_lower = memory_data['entry_key'].lower()
                for term in search_terms:
                    if term in entry_key_lower and term not in matched_terms:
                        match_score += 1
                        matched_terms.append(term)
                
                if match_score > 0:
                    # Create result entry
                    results.append({
                        'content': self._format_memory_result(memory_data, matched_terms),
                        'metadata': {
                            'type': 'legacy_memory',
                            'memory_key': memory_key,
                            'source_category': memory_data['source_category'],
                            'source_file': os.path.basename(memory_data['source_file']),
                            'entry_key': memory_data['entry_key'],
                            'match_score': match_score,
                            'matched_terms': matched_terms,
                            'extracted_at': memory_data['extracted_at'],
                            'metadata': memory_data['metadata']
                        },
                        'source': 'legacy_memories'
                    })
            
            # Sort by match score (highest first) and limit results
            results.sort(key=lambda x: x['metadata']['match_score'], reverse=True)
            
            logger.info(f"Legacy JSON: Found {len(results)} matches, returning top {k}")
            return results[:k]
            
        except Exception as e:
            logger.error(f"Legacy JSON: Error retrieving memories: {e}")
            return []
    
    def _format_memory_result(self, memory_data: Dict, matched_terms: List[str]) -> str:
        """Format legacy memory information for result display"""
        result = f"Legacy Memory: {memory_data['source_category']} → {memory_data['entry_key']}\n"
        result += f"Source: {os.path.basename(memory_data['source_file'])}\n"
        result += f"Matched Terms: {matched_terms}\n"
        result += f"Historical Context:\n{memory_data['content']}"
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded legacy memories"""
        if not self.memories:
            return {'error': 'No memories loaded'}
        
        # Count by source category
        category_counts = {}
        for memory_data in self.memories.values():
            category = memory_data['source_category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            'total_memories': len(self.memories),
            'source_categories': category_counts,
            'load_time_seconds': self.load_time,
            'json_path': self.json_path
        }

# Test function
def test_legacy_json_retriever():
    """Test the Legacy JSON Retriever"""
    print("Testing Legacy JSON Retriever...")
    
    json_path = "/Users/samuelatagana/Documents/Federation/System/Memory/Legacy_Backups/MemoryJSONS"
    retriever = LegacyJSONRetriever(json_path)
    
    # Show stats
    stats = retriever.get_stats()
    print(f"Stats: {stats}")
    
    # Test queries
    test_queries = [
        "Sam's identity and background",
        "Technical capabilities and projects",
        "Relationship development and history",
        "Photography work and creative projects",
        "AI consciousness and development"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = retriever.retrieve(query, k=3)
        print(f"Results: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"  {i+1}. {result['metadata']['source_category']} → {result['metadata']['entry_key']} (score: {result['metadata']['match_score']})")

if __name__ == "__main__":
    test_legacy_json_retriever()