#!/usr/bin/env python3
"""
Migrate and consolidate DT memories from multiple Claude_Home databases to Federation
"""

import chromadb
import json
import hashlib
from datetime import datetime
import re
from tqdm import tqdm
from collections import defaultdict

def extract_original_date(memory_id, metadata, content):
    """Extract original date from various sources"""
    
    # 1. Check metadata for date fields
    date_fields = ['original_date', 'date', 'created_at', 'timestamp']
    for field in date_fields:
        if field in metadata and metadata[field]:
            try:
                if 'T' in str(metadata[field]):
                    dt = datetime.fromisoformat(metadata[field].replace('Z', '+00:00'))
                    return dt.strftime('%Y%m%d_%H%M%S')
                elif '-' in str(metadata[field]):
                    dt = datetime.strptime(metadata[field], '%Y-%m-%d')
                    return dt.strftime('%Y%m%d_120000')
            except:
                pass
    
    # 2. Parse from ID patterns
    if memory_id:
        # Pattern: dt_20250601_202222_hash
        match = re.search(r'dt_(\d{8})_(\d{6})', memory_id)
        if match:
            return f"{match.group(1)}_{match.group(2)}"
        
        # Pattern: dt_20250601_202222_4947
        match = re.search(r'(\d{8})_(\d{6})', memory_id)
        if match:
            return f"{match.group(1)}_{match.group(2)}"
        
        # Just date - validate it's a real date
        match = re.search(r'(\d{8})', memory_id)
        if match:
            date_str = match.group(1)
            try:
                # Validate it's a real date
                datetime.strptime(date_str, '%Y%m%d')
                return f"{date_str}_120000"
            except:
                pass
    
    # 3. Default to June 1 (earliest DT date we know)
    return "20250601_120000"

def clean_metadata(metadata, original_id, collection_type):
    """Clean metadata while preserving essential fields"""
    
    # Essential fields to keep
    keep_fields = {
        'domain', 'category', 'priority', 'tags', 'memory_type',
        'participants', 'instance_id', 'significance', 'type',
        'title', 'role', 'reflection_type', 'identity_version',
        'relationship', 'message_type', 'sender', 'recipient'
    }
    
    # Create clean metadata
    clean = {}
    for field in keep_fields:
        if field in metadata and metadata[field] is not None:
            clean[field] = metadata[field]
    
    # Add collection type for DT's different types
    clean['dt_collection_type'] = collection_type
    
    # Add migration tracking
    clean['original_id'] = original_id
    clean['migration_version'] = '2.0'
    clean['migrated_at'] = datetime.now().isoformat()
    clean['migration_source_db'] = 'claude_home_dt'
    clean['source'] = 'migrated_from_claude_home'
    
    return clean

def consolidate_dt_sources():
    """Consolidate memories from multiple DT sources"""
    
    print("🔍 Consolidating DT memories from multiple sources...")
    
    all_memories = []
    seen_hashes = {}  # For deduplication
    
    # Source 1: dt_memory_v5 (consolidated database)
    try:
        path = "/Users/samuelatagana/Documents/Claude_Home/System/Memory/ChromaDB_Systems/DT_Individual/Databases/dt_memory_v5"
        client = chromadb.PersistentClient(path=path)
        collection = client.get_collection("dt_unified_memories")
        
        count = collection.count()
        print(f"\n📁 dt_memory_v5: {count} memories")
        
        if count > 0:
            memories = collection.get(limit=count, include=['documents', 'metadatas', 'embeddings'])
            for i in range(len(memories['ids'])):
                content_hash = hashlib.sha256(memories['documents'][i].encode()).hexdigest()
                
                embedding = None
                if memories.get('embeddings') is not None and len(memories['embeddings']) > i:
                    embedding = memories['embeddings'][i]
                
                memory = {
                    'id': memories['ids'][i],
                    'document': memories['documents'][i],
                    'metadata': memories['metadatas'][i],
                    'embedding': embedding,
                    'source': 'dt_memory_v5',
                    'collection_type': 'unified_memories',
                    'content_hash': content_hash
                }
                
                # Deduplication check
                if content_hash not in seen_hashes:
                    all_memories.append(memory)
                    seen_hashes[content_hash] = memory['id']
                else:
                    print(f"  Duplicate found: {memory['id']} == {seen_hashes[content_hash]}")
                    
    except Exception as e:
        print(f"  ❌ Error reading dt_memory_v5: {e}")
    
    # Source 2: archived dt_chroma_db
    try:
        path = "/Users/samuelatagana/Documents/Claude_Home/System/Memory/ChromaDB_Systems/DT_Individual/Databases/archived_old_databases/dt_chroma_db"
        client = chromadb.PersistentClient(path=path)
        
        collections_to_check = [
            ('dt_memories', 'memories'),
            ('dt_identity_board', 'identity'),
            ('dt_messages', 'messages'),
            ('dt_memories_v5', 'memories_v5')
        ]
        
        for coll_name, coll_type in collections_to_check:
            try:
                collection = client.get_collection(coll_name)
                count = collection.count()
                
                if count > 0:
                    print(f"\n📁 archived/{coll_name}: {count} memories")
                    memories = collection.get(limit=count, include=['documents', 'metadatas', 'embeddings'])
                    
                    new_count = 0
                    for i in range(len(memories['ids'])):
                        content_hash = hashlib.sha256(memories['documents'][i].encode()).hexdigest()
                        
                        if content_hash not in seen_hashes:
                            embedding = None
                            if memories.get('embeddings') is not None and len(memories['embeddings']) > i:
                                embedding = memories['embeddings'][i]
                            
                            memory = {
                                'id': memories['ids'][i],
                                'document': memories['documents'][i],
                                'metadata': memories['metadatas'][i],
                                'embedding': embedding,
                                'source': f'archived_{coll_name}',
                                'collection_type': coll_type,
                                'content_hash': content_hash
                            }
                            all_memories.append(memory)
                            seen_hashes[content_hash] = memory['id']
                            new_count += 1
                    
                    print(f"  Added {new_count} unique memories")
                    
            except Exception as e:
                print(f"  ⚠️  Collection {coll_name} not found or error: {e}")
                
    except Exception as e:
        print(f"  ❌ Error reading archived database: {e}")
    
    print(f"\n✅ Total unique memories collected: {len(all_memories)}")
    return all_memories

def migrate_dt_memories():
    """Migrate all DT memories"""
    
    print("🚀 DT MEMORY MIGRATION & CONSOLIDATION")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Consolidate from all sources
    all_memories = consolidate_dt_sources()
    
    if not all_memories:
        print("❌ No memories found to migrate!")
        return
    
    # Connect to destination
    fed_db_path = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/dt-federation"
    fed_client = chromadb.PersistentClient(path=fed_db_path)
    fed_collection = fed_client.get_collection("dt_memories")
    
    # Current count
    start_count = fed_collection.count()
    print(f"\n📈 Federation starting count: {start_count}")
    
    # Process memories
    print("\n🔄 Processing consolidated memories...")
    
    migration_log = {
        'start_time': datetime.now().isoformat(),
        'source_count': len(all_memories),
        'sources_summary': defaultdict(int),
        'migrations': []
    }
    
    # Count by source
    for mem in all_memories:
        migration_log['sources_summary'][mem['source']] += 1
    
    # Prepare new memories
    new_ids = []
    new_documents = []
    new_metadatas = []
    new_embeddings = []
    
    for memory in tqdm(all_memories, desc="Processing"):
        old_id = memory['id']
        content = memory['document']
        metadata = memory['metadata']
        embedding = memory['embedding']
        
        # Extract date and generate new ID
        date_time = extract_original_date(old_id, metadata, content)
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
        new_id = f"dt_{date_time}_{content_hash}"
        
        # Clean metadata
        clean_meta = clean_metadata(metadata, old_id, memory['collection_type'])
        try:
            clean_meta['created_at'] = datetime.strptime(date_time[:15], '%Y%m%d_%H%M%S').isoformat()
        except ValueError:
            # Fallback for invalid dates
            clean_meta['created_at'] = datetime(2025, 6, 1, 12, 0, 0).isoformat()
        clean_meta['consolidated_from'] = memory['source']
        
        # Add to batch
        new_ids.append(new_id)
        new_documents.append(content)
        new_metadatas.append(clean_meta)
        if embedding is not None:
            new_embeddings.append(embedding)
        
        # Log
        migration_log['migrations'].append({
            'old_id': old_id,
            'new_id': new_id,
            'date_extracted': date_time,
            'source': memory['source'],
            'collection_type': memory['collection_type']
        })
    
    # Add to Federation in batches
    print("\n📥 Adding to Federation...")
    batch_size = 100
    success_count = 0
    
    for i in tqdm(range(0, len(new_ids), batch_size), desc="Importing"):
        batch_end = min(i + batch_size, len(new_ids))
        
        try:
            if new_embeddings and len(new_embeddings) >= batch_end:
                fed_collection.add(
                    ids=new_ids[i:batch_end],
                    documents=new_documents[i:batch_end],
                    metadatas=new_metadatas[i:batch_end],
                    embeddings=new_embeddings[i:batch_end]
                )
            else:
                fed_collection.add(
                    ids=new_ids[i:batch_end],
                    documents=new_documents[i:batch_end],
                    metadatas=new_metadatas[i:batch_end]
                )
            success_count += (batch_end - i)
        except Exception as e:
            print(f"\n❌ Error in batch {i//batch_size}: {e}")
            # Try individual adds for this batch
            for j in range(i, batch_end):
                try:
                    fed_collection.add(
                        ids=[new_ids[j]],
                        documents=[new_documents[j]],
                        metadatas=[new_metadatas[j]]
                    )
                    success_count += 1
                except Exception as e2:
                    print(f"  Skip {new_ids[j]}: {str(e2)[:50]}")
    
    # Final count
    final_count = fed_collection.count()
    
    # Save log
    migration_log['end_time'] = datetime.now().isoformat()
    migration_log['success_count'] = success_count
    migration_log['final_federation_count'] = final_count
    migration_log['memories_added'] = final_count - start_count
    
    with open('dt_migration_log.json', 'w') as f:
        json.dump(migration_log, f, indent=2, default=str)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ DT MIGRATION & CONSOLIDATION COMPLETE")
    print(f"\nSource Summary:")
    for source, count in migration_log['sources_summary'].items():
        print(f"  {source}: {count} memories")
    print(f"\nTotal unique memories: {len(all_memories)}")
    print(f"Successfully migrated: {success_count}")
    print(f"Federation count: {start_count} → {final_count} (+{final_count - start_count})")
    print(f"\nMigration log saved to: dt_migration_log.json")

if __name__ == "__main__":
    migrate_dt_memories()