#!/usr/bin/env python3
"""
Shared Federation Bridge Script
Enables cross-instance memory operations between CC and DT

Key Features:
- Federation-wide search across both instances
- Shared memory coordination
- Cross-instance health monitoring
- Unified statistics and reporting
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
from content_hasher import generate_content_hash, hash_memory_id
from tag_operations import EnhancedTagOperations
from api_standards import APIStandardizer

# Import individual bridges
from .cc_federation_bridge import CCFederationBridge
from .dt_federation_bridge import DTFederationBridge


class SharedFederationBridge:
    """Coordinates memory operations across CC and DT federation instances"""
    
    def __init__(self):
        """Initialize connections to both federation databases"""
        try:
            # Initialize instance bridges
            self.cc_bridge = CCFederationBridge()
            self.dt_bridge = DTFederationBridge()
            
            print(f"🌐 Shared Federation Bridge initialized", file=sys.stderr)
            print(f"   CC: {self.cc_bridge.memory_collection.count()} memories", file=sys.stderr)
            print(f"   DT: {self.dt_bridge.memory_collection.count()} memories", file=sys.stderr)
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize shared federation bridge: {e}")
    
    def search_other_instance(self, query: str, from_instance: str, 
                             n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search ONLY the other instance's memories
        
        Args:
            query: Search query (may include time expressions)
            from_instance: The instance making the request ('cc' or 'dt')
            n_results: Maximum results
            
        Returns:
            List of memories from the OTHER instance only
        """
        # Determine target instance
        target_instance = 'dt' if from_instance == 'cc' else 'cc'
        target_bridge = self.dt_bridge if target_instance == 'dt' else self.cc_bridge
        
        try:
            # Search only the target instance
            results = target_bridge.recall(query, n_results)
            
            # Filter out private memories
            filtered_results = []
            for memory in results:
                metadata = memory.get('metadata', {})
                if not metadata.get('is_private', False):
                    # Add source instance info
                    memory['source_instance'] = target_instance
                    filtered_results.append(memory)
            
            return filtered_results
            
        except Exception as e:
            print(f"Error searching {target_instance}: {e}", file=sys.stderr)
            return []
    
    def federation_search(self, query: str, instances: List[str] = None, 
                         n_results: int = 10) -> Dict[str, Any]:
        """
        Search across federation instances
        
        Args:
            query: Search query (may include time expressions)
            instances: List of instances to search ['cc', 'dt'] (default: both)
            n_results: Maximum results per instance
            
        Returns:
            Federation search results with instance attribution
        """
        if instances is None:
            instances = ['cc', 'dt']
        
        # Extract time expressions once for consistency
        time_result = extract_time_from_query(query)
        cleaned_query = time_result["cleaned_query"]
        
        federation_results = {
            'query': query,
            'cleaned_query': cleaned_query,
            'time_expression': time_result.get('time_expression'),
            'instances_searched': instances,
            'results': {},
            'total_found': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Search each requested instance
        if 'cc' in instances:
            try:
                cc_results = self.cc_bridge.recall(query, n_results)
                federation_results['results']['cc'] = {
                    'memories': cc_results,
                    'count': len(cc_results),
                    'status': 'success'
                }
                federation_results['total_found'] += len(cc_results)
            except Exception as e:
                federation_results['results']['cc'] = {
                    'memories': [],
                    'count': 0,
                    'status': 'error',
                    'error': str(e)
                }
        
        if 'dt' in instances:
            try:
                dt_results = self.dt_bridge.recall(query, n_results)
                federation_results['results']['dt'] = {
                    'memories': dt_results,
                    'count': len(dt_results),
                    'status': 'success'
                }
                federation_results['total_found'] += len(dt_results)
            except Exception as e:
                federation_results['results']['dt'] = {
                    'memories': [],
                    'count': 0,
                    'status': 'error',
                    'error': str(e)
                }
        
        return federation_results
    
    def share_memory(self, memory_id: str, from_instance: str, to_instance: str) -> Dict[str, Any]:
        """
        Share a memory from one instance to another
        
        Args:
            memory_id: ID of memory to share
            from_instance: Source instance ('cc' or 'dt')
            to_instance: Target instance ('cc' or 'dt')
            
        Returns:
            Result of sharing operation
        """
        try:
            # Get source bridge
            source_bridge = self.cc_bridge if from_instance == 'cc' else self.dt_bridge
            target_bridge = self.dt_bridge if to_instance == 'dt' else self.cc_bridge
            
            # Get memory from source
            source_collection = source_bridge.memory_collection
            memory_data = source_collection.get(ids=[memory_id])
            
            if not memory_data['ids']:
                return APIStandardizer.standardize_error_response(
                    f"Memory {memory_id} not found in {from_instance}",
                    operation='share_memory'
                )
            
            # Extract memory content and metadata
            content = memory_data['documents'][0]
            metadata = memory_data['metadatas'][0] or {}
            
            # Check if memory is shareable
            if metadata.get('is_private', False):
                return APIStandardizer.standardize_error_response(
                    f"Memory {memory_id} is marked as private",
                    operation='share_memory'
                )
            
            # Update metadata for target instance
            shared_metadata = metadata.copy()
            shared_metadata['shared_from'] = from_instance
            shared_metadata['shared_at'] = datetime.now().isoformat()
            shared_metadata['original_id'] = memory_id
            shared_metadata['shared_with'] = to_instance
            
            # Store in target instance
            new_id = target_bridge.remember(
                content=content,
                title=metadata.get('title', ''),
                tags=metadata.get('tags', ''),
                metadata=shared_metadata
            )
            
            return APIStandardizer.standardize_success_response(
                data={
                    'original_id': memory_id,
                    'new_id': new_id,
                    'from_instance': from_instance,
                    'to_instance': to_instance
                },
                operation='share_memory',
                message=f"Memory shared from {from_instance} to {to_instance}"
            )
            
        except Exception as e:
            return APIStandardizer.standardize_error_response(
                str(e),
                operation='share_memory',
                context={'memory_id': memory_id, 'from': from_instance, 'to': to_instance}
            )
    
    def federation_health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check across all federation instances
        
        Returns:
            Federation-wide health report
        """
        health_report = {
            'federation_status': 'unknown',
            'instances': {},
            'total_memories': 0,
            'total_recent_24h': 0,
            'overall_health_score': 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Check CC health
        try:
            cc_health = self.cc_bridge.health_check()
            health_report['instances']['cc'] = cc_health
            health_report['total_memories'] += cc_health.get('total_memories', 0)
            health_report['total_recent_24h'] += cc_health.get('recent_24h', 0)
        except Exception as e:
            health_report['instances']['cc'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # Check DT health
        try:
            dt_health = self.dt_bridge.health_check()
            health_report['instances']['dt'] = dt_health
            health_report['total_memories'] += dt_health.get('total_memories', 0)
            health_report['total_recent_24h'] += dt_health.get('recent_24h', 0)
        except Exception as e:
            health_report['instances']['dt'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # Calculate overall health score
        health_scores = []
        for instance_data in health_report['instances'].values():
            if 'health_score' in instance_data:
                health_scores.append(instance_data['health_score'])
        
        if health_scores:
            health_report['overall_health_score'] = sum(health_scores) / len(health_scores)
            
            if health_report['overall_health_score'] >= 0.8:
                health_report['federation_status'] = 'healthy'
            elif health_report['overall_health_score'] >= 0.5:
                health_report['federation_status'] = 'warning'
            else:
                health_report['federation_status'] = 'critical'
        else:
            health_report['federation_status'] = 'error'
        
        return health_report
    
    def get_federation_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics across the federation
        
        Returns:
            Unified federation statistics
        """
        try:
            cc_stats = self.cc_bridge.get_memory_stats()
            dt_stats = self.dt_bridge.get_memory_stats()
            
            return {
                'federation_id': 'legacy-mind-federation',
                'total_memories': cc_stats['total_memories'] + dt_stats['total_memories'],
                'recent_24h': cc_stats['recent_24h'] + dt_stats['recent_24h'],
                'instances': {
                    'cc': cc_stats,
                    'dt': dt_stats
                },
                'health_summary': {
                    'cc': cc_stats['health_status'],
                    'dt': dt_stats['health_status']
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def sync_shared_memories(self) -> Dict[str, Any]:
        """
        Synchronize memories marked for federation sharing
        
        Returns:
            Sync operation results
        """
        sync_results = {
            'cc_to_dt': {'count': 0, 'memories': []},
            'dt_to_cc': {'count': 0, 'memories': []},
            'errors': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Get CC memories marked for sharing
            cc_all = self.cc_bridge.memory_collection.get(limit=1000)
            for i, metadata in enumerate(cc_all.get('metadatas', [])):
                if metadata and metadata.get('federation_visible', False) and not metadata.get('is_private', False):
                    # Check if already shared
                    if 'shared_to_dt' not in metadata:
                        memory_id = cc_all['ids'][i]
                        result = self.share_memory(memory_id, 'cc', 'dt')
                        if result['success']:
                            sync_results['cc_to_dt']['count'] += 1
                            sync_results['cc_to_dt']['memories'].append(memory_id)
                            # Mark as shared
                            metadata['shared_to_dt'] = datetime.now().isoformat()
                            self.cc_bridge.memory_collection.update(
                                ids=[memory_id],
                                metadatas=[metadata]
                            )
            
            # Get DT memories marked for sharing
            dt_all = self.dt_bridge.memory_collection.get(limit=1000)
            for i, metadata in enumerate(dt_all.get('metadatas', [])):
                if metadata and metadata.get('federation_visible', False) and not metadata.get('is_private', False):
                    # Check if already shared
                    if 'shared_to_cc' not in metadata:
                        memory_id = dt_all['ids'][i]
                        result = self.share_memory(memory_id, 'dt', 'cc')
                        if result['success']:
                            sync_results['dt_to_cc']['count'] += 1
                            sync_results['dt_to_cc']['memories'].append(memory_id)
                            # Mark as shared
                            metadata['shared_to_cc'] = datetime.now().isoformat()
                            self.dt_bridge.memory_collection.update(
                                ids=[memory_id],
                                metadatas=[metadata]
                            )
            
        except Exception as e:
            sync_results['errors'].append(str(e))
        
        return sync_results


# Test and example usage
if __name__ == "__main__":
    try:
        # Initialize shared bridge
        bridge = SharedFederationBridge()
        
        print("🌐 Shared Federation Bridge Test")
        print("=" * 50)
        
        # Test federation health
        health = bridge.federation_health_check()
        print(f"\n📊 Federation Status: {health['federation_status']}")
        print(f"📈 Total Memories: {health['total_memories']}")
        print(f"🕐 Recent (24h): {health['total_recent_24h']}")
        print(f"💯 Overall Health Score: {health['overall_health_score']:.2f}")
        
        # Test federation search
        print("\n🔍 Testing Federation Search:")
        results = bridge.federation_search("bridge test", n_results=5)
        print(f"Total found across instances: {results['total_found']}")
        for instance, data in results['results'].items():
            print(f"  {instance.upper()}: {data['count']} memories")
        
        # Test federation stats
        print("\n📊 Federation Statistics:")
        stats = bridge.get_federation_stats()
        print(f"Total federation memories: {stats['total_memories']}")
        print(f"Recent activity (24h): {stats['recent_24h']}")
        
        print("\n✅ Shared Federation Bridge ready for Layer 3 integration!")
        
    except Exception as e:
        print(f"❌ Shared bridge test failed: {e}")
        import traceback
        traceback.print_exc()