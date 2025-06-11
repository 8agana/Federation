#!/usr/bin/env python3
"""
Memory Health Monitor - Database diagnostics and health checks
Provides comprehensive health monitoring for ChromaDB memory systems
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import chromadb
from collections import defaultdict


class MemoryHealthMonitor:
    """Monitors health and performance of ChromaDB memory systems"""
    
    def __init__(self, db_path: str):
        """
        Initialize health monitor
        
        Args:
            db_path: Path to ChromaDB database
        """
        self.db_path = Path(db_path)
        self.client = chromadb.PersistentClient(path=str(db_path))
        
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific collection
        
        Args:
            collection_name: Name of the collection to analyze
            
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.client.get_collection(collection_name)
            
            # Get all items for analysis
            results = collection.get(limit=10000)
            
            if not results['ids']:
                return {
                    'collection': collection_name,
                    'total_memories': 0,
                    'status': 'empty'
                }
            
            # Basic counts
            total_memories = len(results['ids'])
            
            # Analyze metadata
            metadata_stats = self._analyze_metadata(results['metadatas'])
            
            # Analyze content
            content_stats = self._analyze_content(results['documents'])
            
            # Analyze timestamps
            time_stats = self._analyze_timestamps(results['metadatas'])
            
            # Check for duplicates
            duplicate_stats = self._check_duplicates(results)
            
            # Tag analysis
            tag_stats = self._analyze_tags(results['metadatas'])
            
            return {
                'collection': collection_name,
                'total_memories': total_memories,
                'metadata_stats': metadata_stats,
                'content_stats': content_stats,
                'time_stats': time_stats,
                'duplicate_stats': duplicate_stats,
                'tag_stats': tag_stats,
                'status': 'healthy'
            }
            
        except Exception as e:
            return {
                'collection': collection_name,
                'error': str(e),
                'status': 'error'
            }
    
    def _analyze_metadata(self, metadatas: List[Dict]) -> Dict[str, Any]:
        """Analyze metadata patterns and completeness"""
        field_counts = defaultdict(int)
        field_types = defaultdict(set)
        
        for metadata in metadatas:
            if metadata:
                for key, value in metadata.items():
                    field_counts[key] += 1
                    field_types[key].add(type(value).__name__)
        
        total_records = len(metadatas)
        
        return {
            'total_records': total_records,
            'field_coverage': {k: v/total_records for k, v in field_counts.items()},
            'field_types': {k: list(v) for k, v in field_types.items()},
            'most_common_fields': sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def _analyze_content(self, documents: List[str]) -> Dict[str, Any]:
        """Analyze content patterns and statistics"""
        if not documents:
            return {'status': 'no_content'}
        
        lengths = [len(doc) for doc in documents if doc]
        
        return {
            'total_documents': len(documents),
            'avg_length': sum(lengths) / len(lengths) if lengths else 0,
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0,
            'empty_documents': len([doc for doc in documents if not doc])
        }
    
    def _analyze_timestamps(self, metadatas: List[Dict]) -> Dict[str, Any]:
        """Analyze timestamp patterns"""
        timestamps = []
        
        for metadata in metadatas:
            if metadata:
                for field in ['timestamp', 'created_at', 'updated_at']:
                    if field in metadata:
                        try:
                            ts = datetime.fromisoformat(metadata[field].replace('Z', '+00:00'))
                            timestamps.append(ts)
                            break
                        except:
                            pass
        
        if not timestamps:
            return {'status': 'no_timestamps'}
        
        now = datetime.now()
        recent_count = len([ts for ts in timestamps if (now - ts).days <= 1])
        
        return {
            'total_with_timestamps': len(timestamps),
            'oldest': min(timestamps).isoformat(),
            'newest': max(timestamps).isoformat(),
            'recent_24h': recent_count
        }
    
    def _check_duplicates(self, results: Dict) -> Dict[str, Any]:
        """Check for duplicate content using hashes"""
        hashes = []
        
        for metadata in results.get('metadatas', []):
            if metadata and 'content_hash' in metadata:
                hashes.append(metadata['content_hash'])
        
        if not hashes:
            return {'status': 'no_hashes'}
        
        hash_counts = defaultdict(int)
        for h in hashes:
            hash_counts[h] += 1
        
        duplicates = {h: count for h, count in hash_counts.items() if count > 1}
        
        return {
            'total_hashed': len(hashes),
            'unique_hashes': len(hash_counts),
            'duplicates_found': len(duplicates),
            'duplicate_hashes': list(duplicates.keys())[:5]
        }
    
    def _analyze_tags(self, metadatas: List[Dict]) -> Dict[str, Any]:
        """Analyze tag usage patterns"""
        all_tags = []
        
        for metadata in metadatas:
            if metadata and 'tags' in metadata:
                tags_str = metadata['tags']
                if tags_str:
                    tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                    all_tags.extend(tags)
        
        if not all_tags:
            return {'status': 'no_tags'}
        
        tag_counts = defaultdict(int)
        for tag in all_tags:
            tag_counts[tag] += 1
        
        return {
            'total_tags': len(all_tags),
            'unique_tags': len(tag_counts),
            'most_common_tags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'avg_tags_per_memory': len(all_tags) / len(metadatas)
        }
    
    def check_database_health(self) -> Dict[str, Any]:
        """
        Comprehensive database health check
        
        Returns:
            Overall health status and recommendations
        """
        try:
            # Get all collections
            collections = self.client.list_collections()
            collection_stats = []
            
            total_memories = 0
            total_errors = 0
            
            for collection in collections:
                stats = self.get_collection_stats(collection.name)
                collection_stats.append(stats)
                
                if stats.get('status') == 'error':
                    total_errors += 1
                else:
                    total_memories += stats.get('total_memories', 0)
            
            # Calculate overall health score
            health_score = 1.0
            if total_errors > 0:
                health_score -= (total_errors / len(collections)) * 0.5
            
            if total_memories == 0:
                health_score = 0.5
            
            # Determine overall status
            if health_score >= 0.8:
                status = 'healthy'
            elif health_score >= 0.5:
                status = 'warning'
            else:
                status = 'critical'
            
            # Check disk usage
            disk_usage = self._check_disk_usage()
            
            return {
                'status': status,
                'health_score': health_score,
                'total_collections': len(collections),
                'total_memories': total_memories,
                'errors': total_errors,
                'collection_stats': collection_stats,
                'disk_usage': disk_usage,
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    def _check_disk_usage(self) -> Dict[str, Any]:
        """Check disk usage for the database"""
        try:
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(self.db_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
                        file_count += 1
            
            # Convert to MB
            size_mb = total_size / (1024 * 1024)
            
            return {
                'total_size_mb': round(size_mb, 2),
                'file_count': file_count,
                'database_path': str(self.db_path)
            }
            
        except Exception as e:
            return {
                'error': str(e)
            }