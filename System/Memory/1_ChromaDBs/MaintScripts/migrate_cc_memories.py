#!/usr/bin/env python3
"""
Migrate CC memories from Claude_Home to Federation with proper dates
"""

import chromadb
import json
import hashlib
from datetime import datetime
import re
from tqdm import tqdm

def extract_original_date(memory_id, metadata, content):
    """Extract original date from various sources"""
    
    # 1. Check metadata for date fields
    date_fields = ['original_date', 'date', 'original_original_date', 'created_at']
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
        # Pattern: 20250528-29_chunk_1 or 20250530_2306_chunk_0
        match = re.search(r'(\d{8})', memory_id)
        if match:
            date_str = match.group(1)
            # Try to get time too
            time_match = re.search(r'(\d{8})_(\d{4})', memory_id)
            if time_match:
                return f"{time_match.group(1)}_{time_match.group(2)}00"
            return f"{date_str}_120000"
    
    # 3. Extract from content
    content_match = re.search(r'(May|June) (\d{1,2}), 2025', content[:200])
    if content_match:
        month_map = {'May': '05', 'June': '06'}
        month = month_map.get(content_match.group(1), '05')
        day = content_match.group(2).zfill(2)
        return f"2025{month}{day}_120000"
    
    # Default to earliest known CC date
    return "20250528_120000"

def clean_metadata(metadata, original_id):
    """Clean metadata while preserving essential fields"""
    
    # Essential fields to keep
    keep_fields = {
        'domain', 'category', 'priority', 'tags', 'memory_type',
        'participants', 'instance_id', 'significance', 'type',
        'title', 'conversation_id', 'message_count', 'refined_count',
        'chunk_index', 'chunk_total', 'context_type', 'conversation_date'
    }
    
    # Create clean metadata
    clean = {}
    for field in keep_fields:
        if field in metadata and metadata[field] is not None:
            clean[field] = metadata[field]
    
    # Add migration tracking
    clean['original_id'] = original_id
    clean['migration_version'] = '2.0'
    clean['migrated_at'] = datetime.now().isoformat()
    clean['migration_source_db'] = 'claude_home_cc'
    clean['source'] = 'migrated_from_claude_home'
    
    return clean

def migrate_cc_memories():
    """Migrate all CC memories"""
    
    print("🚀 CC MEMORY MIGRATION")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Connect to source
    old_db_path = "/Users/samuelatagana/Documents/Claude_Home/System/Memory/ChromaDB_Systems/CC_Individual/Databases/cc_chroma_db"
    old_client = chromadb.PersistentClient(path=old_db_path)
    old_collection = old_client.get_collection("cc_conversations")
    
    # Connect to destination
    fed_db_path = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation"
    fed_client = chromadb.PersistentClient(path=fed_db_path)
    fed_collection = fed_client.get_collection("cc_memories")
    
    # Get all memories
    print("\n📊 Fetching memories from old database...")
    old_count = old_collection.count()
    print(f"Found {old_count} memories to migrate")
    
    # Fetch in batches
    batch_size = 100
    all_memories = {'ids': [], 'documents': [], 'metadatas': [], 'embeddings': []}
    
    for offset in range(0, old_count, batch_size):
        batch = old_collection.get(
            limit=batch_size,
            offset=offset,
            include=['documents', 'metadatas', 'embeddings']
        )
        all_memories['ids'].extend(batch['ids'])
        all_memories['documents'].extend(batch['documents'])
        all_memories['metadatas'].extend(batch['metadatas'])
        if batch.get('embeddings') is not None:
            all_memories['embeddings'].extend(batch['embeddings'])
    
    print(f"✅ Fetched {len(all_memories['ids'])} memories")
    
    # Current count in Federation
    start_count = fed_collection.count()
    print(f"\n📈 Federation starting count: {start_count}")
    
    # Process and migrate
    print("\n🔄 Processing memories...")
    
    migration_log = {
        'start_time': datetime.now().isoformat(),
        'source_count': old_count,
        'migrations': []
    }
    
    # Prepare new memories
    new_ids = []
    new_documents = []
    new_metadatas = []
    new_embeddings = []
    
    for i in tqdm(range(len(all_memories['ids'])), desc="Processing"):
        old_id = all_memories['ids'][i]
        content = all_memories['documents'][i]
        metadata = all_memories['metadatas'][i]
        embedding = all_memories['embeddings'][i] if all_memories.get('embeddings') else None
        
        # Extract date and generate new ID
        date_time = extract_original_date(old_id, metadata, content)
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
        new_id = f"cc_{date_time}_{content_hash}"
        
        # Clean metadata
        clean_meta = clean_metadata(metadata, old_id)
        clean_meta['created_at'] = datetime.strptime(date_time[:15], '%Y%m%d_%H%M%S').isoformat()
        
        # Add to batch
        new_ids.append(new_id)
        new_documents.append(content)
        new_metadatas.append(clean_meta)
        if embedding is not None:
            new_embeddings.append(embedding)
        
        # Log migration
        migration_log['migrations'].append({
            'old_id': old_id,
            'new_id': new_id,
            'date_extracted': date_time
        })
    
    # Add to Federation in batches
    print("\n📥 Adding to Federation...")
    success_count = 0
    
    for i in tqdm(range(0, len(new_ids), batch_size), desc="Importing"):
        batch_end = min(i + batch_size, len(new_ids))
        
        try:
            if new_embeddings:
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
    
    # Final count
    final_count = fed_collection.count()
    
    # Save migration log
    migration_log['end_time'] = datetime.now().isoformat()
    migration_log['success_count'] = success_count
    migration_log['final_federation_count'] = final_count
    migration_log['memories_added'] = final_count - start_count
    
    with open('cc_migration_log.json', 'w') as f:
        json.dump(migration_log, f, indent=2)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ CC MIGRATION COMPLETE")
    print(f"Source memories: {old_count}")
    print(f"Successfully migrated: {success_count}")
    print(f"Federation count: {start_count} → {final_count} (+{final_count - start_count})")
    print(f"\nMigration log saved to: cc_migration_log.json")

if __name__ == "__main__":
    migrate_cc_memories()