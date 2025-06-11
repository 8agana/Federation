#!/usr/bin/env python3
"""
Enhanced Tag Operations for CC-DT Memory Federation
Supports arrays and AND/OR logic for tags

Based on MCP Memory Service patterns but adapted for our system
"""

import json
from typing import List, Union, Dict, Any, Tuple
import chromadb
from pathlib import Path


class EnhancedTagOperations:
    """Enhanced tag operations with array support and AND/OR logic"""
    
    def __init__(self, collection):
        """Initialize with ChromaDB collection"""
        self.collection = collection
    
    def normalize_tags(self, tags: Union[str, List[str]]) -> List[str]:
        """
        Normalize tags to a consistent list format
        
        Args:
            tags: Either a string (comma-separated) or list of strings
            
        Returns:
            List of normalized tag strings
        """
        if tags is None:
            return []
        
        # If we get a string, split it into an array
        if isinstance(tags, str):
            normalized = [tag.strip() for tag in tags.split(",") if tag.strip()]
        # If we get an array, use it directly
        elif isinstance(tags, list):
            normalized = [str(tag).strip() for tag in tags if str(tag).strip()]
        else:
            return []
        
        return normalized
    
    def tags_to_string(self, tags: Union[str, List[str]]) -> str:
        """
        Convert tags to string format for ChromaDB storage
        
        ChromaDB stores tags as comma-separated strings in metadata
        """
        normalized = self.normalize_tags(tags)
        return ', '.join(normalized) if normalized else ''
    
    def search_by_tag(self, tags: Union[str, List[str]], n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories by tags with OR logic - returns memories matching ANY of the tags
        
        Args:
            tags: Single tag (string) or multiple tags (list)
            n_results: Maximum number of results
            
        Returns:
            List of memory dictionaries
        """
        search_tags = self.normalize_tags(tags)
        if not search_tags:
            return []
        
        try:
            # Get all memories (ChromaDB doesn't support tag queries directly)
            results = self.collection.get(limit=1000)
            
            matched_memories = []
            
            if results and 'ids' in results:
                for i, memory_id in enumerate(results['ids']):
                    metadata = results['metadatas'][i] or {}
                    
                    # Get tags from metadata
                    stored_tags_str = metadata.get('tags', '')
                    if stored_tags_str:
                        stored_tags = self.normalize_tags(stored_tags_str)
                        
                        # Check if ANY search tag matches (OR logic)
                        if any(search_tag in stored_tags for search_tag in search_tags):
                            matched_memories.append({
                                'id': memory_id,
                                'content': results['documents'][i],
                                'metadata': metadata,
                                'tags': stored_tags
                            })
            
            # Return up to n_results
            return matched_memories[:n_results]
            
        except Exception as e:
            print(f"❌ Error searching by tags: {e}")
            return []
    
    def search_by_all_tags(self, tags: List[str], n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories by tags with AND logic - returns memories matching ALL of the tags
        
        Args:
            tags: List of tags that must ALL be present
            n_results: Maximum number of results
            
        Returns:
            List of memory dictionaries
        """
        search_tags = self.normalize_tags(tags)
        if not search_tags:
            return []
        
        try:
            # Get all memories
            results = self.collection.get(limit=1000)
            
            matched_memories = []
            
            if results and 'ids' in results:
                for i, memory_id in enumerate(results['ids']):
                    metadata = results['metadatas'][i] or {}
                    
                    # Get tags from metadata
                    stored_tags_str = metadata.get('tags', '')
                    if stored_tags_str:
                        stored_tags = self.normalize_tags(stored_tags_str)
                        
                        # Check if ALL search tags match (AND logic)
                        if all(search_tag in stored_tags for search_tag in search_tags):
                            matched_memories.append({
                                'id': memory_id,
                                'content': results['documents'][i],
                                'metadata': metadata,
                                'tags': stored_tags
                            })
            
            # Return up to n_results
            return matched_memories[:n_results]
            
        except Exception as e:
            print(f"❌ Error searching by all tags: {e}")
            return []