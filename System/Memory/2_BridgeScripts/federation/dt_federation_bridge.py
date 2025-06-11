#!/usr/bin/env python3
"""
DT Federation Bridge Script
Layer 2 bridge between Layer 1 (federation databases) and Layer 3 (MCP servers)

Implements all 5 Memory Evolution features:
1. Natural Language Time Parsing
2. Hash-Based Content IDs  
3. Enhanced Tag Operations
4. Database Health Monitoring
5. API Standardization
"""

import chromadb
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
import json

# Add utilities to path
sys.path.append(str(Path(__file__).parent.parent / "utilities"))
from time_parser import parse_time_expression, extract_time_from_query
from content_hasher import generate_content_hash, hash_memory_id, generate_short_hash
from tag_operations import EnhancedTagOperations



class DTFederationBridge:
    """Bridge to DT's federation memory system with all Memory Evolution features"""
    
    def __init__(self):
        # Connect to Layer 1 federation database
        self.db_path = Path("/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/dt-federation")
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"DT federation database not found at {self.db_path}")
        
        # Connect to ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        
        # Get main memory collection
        try:
            self.memory_collection = self.client.get_collection("dt_memories")
            print(f"🌉 DT Federation Bridge connected to: {self.db_path}", file=sys.stderr)
            print(f"📚 Memory collection has {self.memory_collection.count()} memories", file=sys.stderr)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to dt_memories collection: {e}")
        
        # Initialize enhanced tag operations
        self.tag_ops = EnhancedTagOperations(self.memory_collection)
    
    def remember(self, content: str, title: str = None, tags: Union[str, List[str]] = None, 
                metadata: Dict[str, Any] = None) -> str:
        """
        Store a memory in federation database with all v5 features
        
        Returns:
            Memory ID or "DUPLICATE:{existing_id}" if duplicate found
        """
        timestamp = datetime.now()
        
        # Generate content hash (Feature 2: Hash-Based Content IDs)
        content_hash = generate_content_hash(content, metadata)
        memory_id = f"dt_{timestamp.strftime('%Y%m%d_%H%M%S')}_{content_hash[:8]}"
        
        # Check for duplicates
        try:
            all_results = self.memory_collection.get(limit=1000)
            if all_results and 'metadatas' in all_results:
                for i, existing_meta in enumerate(all_results['metadatas']):
                    if existing_meta and existing_meta.get('content_hash') == content_hash:
                        existing_id = all_results['ids'][i]
                        print(f'⚠️  Duplicate content detected! Hash: {content_hash[:8]}...', file=sys.stderr)
                        return f"DUPLICATE:{existing_id}"
        except Exception as e:
            print(f'⚠️  Duplicate check failed: {e}', file=sys.stderr)
        
        # Prepare v5 metadata (Feature 5: API Standardization)
        memory_metadata = {
            # Core fields
            "instance_id": "dt",
            "federation_id": "dt-federation",
            "created_by": "dt",
            "created_at": timestamp.isoformat(),
            "updated_at": timestamp.isoformat(),
            "version": 1,
            
            # Content classification
            "domain": metadata.get("domain", "technical") if metadata else "technical",
            "category": metadata.get("category", "memory") if metadata else "memory", 
            "memory_type": metadata.get("memory_type", "living") if metadata else "living",
            
            # Importance
            "priority": metadata.get("priority", 1) if metadata else 1,
            "significance": metadata.get("significance", 1.0) if metadata else 1.0,
            "confidence": metadata.get("confidence", 1.0) if metadata else 1.0,
            
            # Federation
            "federation_visible": metadata.get("federation_visible", True) if metadata else True,
            "is_private": metadata.get("is_private", False) if metadata else False,
            "shared_with": metadata.get("shared_with", "") if metadata else "",
            
            # Content
            "title": title or "",
            "tags": self.tag_ops.tags_to_string(tags),
            "content_hash": content_hash,
            "hash_short": content_hash[:8],
            
            # System
            "source": "dt_federation_bridge",
            "type": "memory"
        }
        
        # Add any additional metadata
        if metadata:
            for key, value in metadata.items():
                if key not in memory_metadata:
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        memory_metadata[key] = value
                    elif isinstance(value, list):
                        memory_metadata[key] = ", ".join(str(item) for item in value)
                    elif isinstance(value, dict):
                        memory_metadata[key] = json.dumps(value)
                    else:
                        memory_metadata[key] = str(value)
        
        try:
            self.memory_collection.add(
                documents=[content],
                metadatas=[memory_metadata],
                ids=[memory_id]
            )
            
            print(f"✅ Stored memory: {memory_id}", file=sys.stderr)
            return memory_id
            
        except Exception as e:
            print(f"❌ Failed to store memory: {e}", file=sys.stderr)
            raise
    
    def recall(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search memories with natural language time parsing (Feature 1)
        
        Args:
            query: Search query (may include time expressions)
            n_results: Maximum number of results
            
        Returns:
            List of memory dictionaries with standardized format
        """
        # Extract time expressions from query (Feature 1: Natural Language Time Parsing)
        time_result = extract_time_from_query(query)
        cleaned_query = time_result["cleaned_query"]
        start_ts = time_result["start_timestamp"]
        end_ts = time_result["end_timestamp"]
        
        try:
            # Search with semantic query
            if cleaned_query.strip():
                results = self.memory_collection.query(
                    query_texts=[cleaned_query],
                    n_results=n_results
                )
            else:
                # If only time expression, get recent memories
                results = self.memory_collection.get(limit=n_results)
                # Convert get results to query format
                if results['ids']:
                    results = {
                        'documents': [results['documents']],
                        'metadatas': [results['metadatas']],
                        'ids': [results['ids']],
                        'distances': [[0.0] * len(results['ids'])]
                    }
                else:
                    return []
            
            # Filter by time if time expression was found
            memories = []
            for i in range(len(results['documents'][0])):
                metadata = results['metadatas'][0][i] or {}
                
                # Check time filter
                if start_ts is not None or end_ts is not None:
                    created_at = metadata.get('created_at')
                    if created_at:
                        try:
                            created_timestamp = datetime.fromisoformat(created_at.replace('Z', '+00:00')).timestamp()
                            
                            # Apply time filter
                            if start_ts and created_timestamp < start_ts:
                                continue
                            if end_ts and created_timestamp > end_ts:
                                continue
                        except:
                            pass  # Skip time filtering for invalid timestamps
                
                memories.append({
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': metadata,
                    'distance': results['distances'][0][i] if 'distances' in results else 0.0,
                    'relevance_score': 1.0 - results['distances'][0][i] if 'distances' in results else 1.0
                })
            
            return memories[:n_results]
            
        except Exception as e:
            print(f"❌ Recall failed: {e}", file=sys.stderr)
            return []
    
    def update_memory(self, memory_id: str, content: str = None, metadata: Dict[str, Any] = None,
                     version_comment: str = None) -> bool:
        """
        Update existing memory (living documents feature)
        
        Args:
            memory_id: ID of memory to update
            content: New content (optional)
            metadata: New/updated metadata (optional)
            version_comment: Comment about the update
            
        Returns:
            True if successful
        """
        try:
            # Get existing memory
            existing = self.memory_collection.get(ids=[memory_id])
            if not existing['ids']:
                print(f"❌ Memory {memory_id} not found", file=sys.stderr)
                return False
            
            existing_metadata = existing['metadatas'][0] or {}
            existing_content = existing['documents'][0]
            
            # Prepare updated data
            updated_content = content if content is not None else existing_content
            updated_metadata = existing_metadata.copy()
            
            # Update metadata
            if metadata:
                updated_metadata.update(metadata)
            
            # Update system fields
            updated_metadata['updated_at'] = datetime.now().isoformat()
            updated_metadata['version'] = updated_metadata.get('version', 1) + 1
            
            if version_comment:
                updated_metadata['version_comment'] = version_comment
            
            # Update content hash if content changed
            if content is not None:
                new_hash = generate_content_hash(updated_content, updated_metadata)
                updated_metadata['content_hash'] = new_hash
                updated_metadata['hash_short'] = new_hash[:8]
            
            # Perform update
            self.memory_collection.update(
                ids=[memory_id],
                documents=[updated_content],
                metadatas=[updated_metadata]
            )
            
            print(f"✅ Updated memory: {memory_id}", file=sys.stderr)
            return True
            
        except Exception as e:
            print(f"❌ Update memory failed: {e}", file=sys.stderr)
            return False
    
    def search_by_tags(self, tags: Union[str, List[str]], n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories by tags (Feature 3: Enhanced Tag Operations)
        
        Uses OR logic - returns memories matching ANY of the tags
        """
        return self.tag_ops.search_by_tag(tags, n_results)
    
    def search_by_all_tags(self, tags: List[str], n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories by tags with AND logic (Feature 3: Enhanced Tag Operations)
        
        Returns memories matching ALL of the tags
        """
        return self.tag_ops.search_by_all_tags(tags, n_results)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform system health check (Feature 4: Database Health Monitoring)
        
        Returns:
            Dictionary with health statistics and status
        """
        try:
            # Get all memories for analysis
            all_memories = self.memory_collection.get()
            total_count = len(all_memories['ids'])
            
            # Check recent activity (last 24 hours)
            recent_count = 0
            cutoff = datetime.now() - timedelta(hours=24)
            
            hash_counts = {}
            version_counts = {}
            domain_counts = {}
            
            for i, metadata in enumerate(all_memories.get('metadatas', [])):
                if not metadata:
                    continue
                
                # Count recent memories
                created_at = metadata.get('created_at')
                if created_at:
                    try:
                        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if created > cutoff:
                            recent_count += 1
                    except:
                        pass
                
                # Count by content hash (duplicate detection)
                content_hash = metadata.get('content_hash')
                if content_hash:
                    hash_counts[content_hash] = hash_counts.get(content_hash, 0) + 1
                
                # Count by version (living document tracking)
                version = metadata.get('version', 1)
                version_counts[version] = version_counts.get(version, 0) + 1
                
                # Count by domain
                domain = metadata.get('domain', 'unknown')
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            # Find duplicates
            duplicates = {h: count for h, count in hash_counts.items() if count > 1}
            
            # Calculate health score
            health_score = 1.0
            if total_count == 0:
                health_score = 0.0
            elif duplicates:
                health_score -= len(duplicates) * 0.1
            
            health_score = max(0.0, min(1.0, health_score))
            
            return {
                'status': 'healthy' if health_score > 0.8 else 'warning' if health_score > 0.5 else 'critical',
                'health_score': health_score,
                'total_memories': total_count,
                'recent_24h': recent_count,
                'duplicates_found': len(duplicates),
                'duplicate_hashes': list(duplicates.keys())[:5],  # Show first 5
                'version_distribution': version_counts,
                'domain_distribution': domain_counts,
                'collection_name': 'dt_memories',
                'database_path': str(self.db_path),
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'health_score': 0.0,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive memory statistics (Feature 5: API Standardization)
        
        Returns:
            Standardized statistics dictionary
        """
        health = self.health_check()
        
        return {
            'total_memories': health['total_memories'],
            'recent_24h': health['recent_24h'],
            'health_status': health['status'],
            'health_score': health['health_score'],
            'duplicates_count': health['duplicates_found'],
            'version_stats': health['version_distribution'],
            'domain_stats': health['domain_distribution'],
            'collection': health['collection_name'],
            'instance': 'dt',
            'federation_id': 'dt-federation'
        }
    



# Test and example usage
if __name__ == "__main__":
    try:
        # Initialize bridge
        bridge = DTFederationBridge()
        
        print("🧠 DT Federation Bridge Test")
        print("=" * 50)
        
        # Test health check
        health = bridge.health_check()
        print(f"\n📊 Health Status: {health['status']}")
        print(f"📈 Total Memories: {health['total_memories']}")
        print(f"🕐 Recent (24h): {health['recent_24h']}")
        
        # Test basic remember/recall
        test_memory = "Testing DT federation bridge with all Memory Evolution features."
        memory_id = bridge.remember(
            content=test_memory,
            title="DT Bridge Test",
            tags=["test", "bridge", "federation", "dt"],
            metadata={"domain": "technical", "priority": 2}
        )
        print(f"✅ Stored test memory: {memory_id}")
        
        # Test recall with time parsing
        results = bridge.recall("bridge test from today", n_results=3)
        print(f"🔍 Recall results: {len(results)} memories found")
        
        print("\n✅ DT Federation Bridge ready for Layer 3 integration!")
        
    except Exception as e:
        print(f"❌ Bridge test failed: {e}")
        import traceback
        traceback.print_exc()