#!/usr/bin/env python3
"""
Test migration approach on small sample before full migration
"""

import chromadb
import json
import hashlib
from datetime import datetime
import re

def extract_original_date(memory_id, metadata, content):
    """Extract original date from various sources"""
    
    # 1. Check metadata for date fields
    date_fields = ['original_date', 'date', 'original_original_date', 'created_at']
    for field in date_fields:
        if field in metadata and metadata[field]:
            # Parse date string
            try:
                if 'T' in str(metadata[field]):
                    dt = datetime.fromisoformat(metadata[field].replace('Z', '+00:00'))
                    return dt.strftime('%Y%m%d_%H%M%S')
                elif '-' in str(metadata[field]):
                    dt = datetime.strptime(metadata[field], '%Y-%m-%d')
                    return dt.strftime('%Y%m%d_120000')  # Default noon
            except:
                pass
    
    # 2. Parse from ID patterns
    if memory_id:
        # Pattern: 20250528-29_chunk_1
        match = re.search(r'(\d{8})', memory_id)
        if match:
            date_str = match.group(1)
            return f"{date_str}_120000"  # Default noon
        
        # Pattern: dt_20250601_202222_hash
        match = re.search(r'_(\d{8})_(\d{6})_', memory_id)
        if match:
            return f"{match.group(1)}_{match.group(2)}"
    
    # 3. Extract from content (if date mentioned)
    content_match = re.search(r'(May|June) (\d{1,2}), 2025', content[:200])
    if content_match:
        month_map = {'May': '05', 'June': '06'}
        month = month_map.get(content_match.group(1), '05')
        day = content_match.group(2).zfill(2)
        return f"2025{month}{day}_120000"
    
    # 4. Default to earliest known date for collection
    return "20250528_120000"  # Earliest CC date we know

def clean_metadata(metadata, original_id):
    """Clean metadata while preserving essential fields"""
    
    # Essential fields to keep
    keep_fields = {
        'domain', 'category', 'priority', 'tags', 'memory_type',
        'participants', 'instance_id', 'significance', 'type',
        'title', 'conversation_id', 'message_count', 'refined_count'
    }
    
    # Create clean metadata
    clean = {}
    for field in keep_fields:
        if field in metadata and metadata[field]:
            clean[field] = metadata[field]
    
    # Add migration tracking
    clean['original_id'] = original_id
    clean['migration_version'] = '2.0'
    clean['migrated_at'] = datetime.now().isoformat()
    clean['migration_source_db'] = 'claude_home'
    clean['source'] = 'migrated_from_claude_home'
    
    return clean

def test_migration_sample():
    """Test migration on a few memories"""
    
    print("🧪 TESTING MIGRATION APPROACH")
    print("=" * 60)
    
    # Connect to old CC database
    old_db_path = "/Users/samuelatagana/Documents/Claude_Home/System/Memory/ChromaDB_Systems/CC_Individual/Databases/cc_chroma_db"
    old_client = chromadb.PersistentClient(path=old_db_path)
    old_collection = old_client.get_collection("cc_conversations")
    
    # Get sample memories
    sample = old_collection.get(limit=5)
    
    print(f"\n📊 Testing on {len(sample['ids'])} sample memories\n")
    
    migrations = []
    
    for i in range(len(sample['ids'])):
        old_id = sample['ids'][i]
        content = sample['documents'][i]
        metadata = sample['metadatas'][i]
        embedding = sample['embeddings'][i] if sample['embeddings'] else None
        
        # Extract original date
        date_time = extract_original_date(old_id, metadata, content)
        
        # Generate new ID
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
        new_id = f"cc_{date_time}_{content_hash}"
        
        # Clean metadata
        clean_meta = clean_metadata(metadata, old_id)
        clean_meta['created_at'] = datetime.strptime(date_time, '%Y%m%d_%H%M%S').isoformat()
        
        migration = {
            'old_id': old_id,
            'new_id': new_id,
            'date_extracted': date_time,
            'content_preview': content[:100] + '...',
            'metadata_before': len(metadata),
            'metadata_after': len(clean_meta),
            'cleaned_fields': list(clean_meta.keys())
        }
        
        migrations.append(migration)
        
        print(f"Memory {i+1}:")
        print(f"  Old ID: {old_id}")
        print(f"  New ID: {new_id}")
        print(f"  Date extracted: {date_time[:8]}")
        print(f"  Metadata: {len(metadata)} → {len(clean_meta)} fields")
        print(f"  Content: {content[:50]}...")
        print()
    
    # Test connecting to Federation
    print("\n🔌 Testing Federation connection...")
    fed_db_path = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation"
    try:
        fed_client = chromadb.PersistentClient(path=fed_db_path)
        fed_collection = fed_client.get_collection("cc_memories")
        current_count = fed_collection.count()
        print(f"✅ Connected! Current count: {current_count}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    
    # Save test results
    with open('test_migration_results.json', 'w') as f:
        json.dump({
            'test_date': datetime.now().isoformat(),
            'samples_tested': len(migrations),
            'migrations': migrations,
            'date_extraction_working': all(m['date_extracted'] != '20250528_120000' for m in migrations[:3]),
            'metadata_cleaned': all(m['metadata_after'] < m['metadata_before'] for m in migrations)
        }, f, indent=2)
    
    print("\n✅ Test complete! Results saved to test_migration_results.json")
    print("\nDate extraction working:", "✅" if migrations[0]['date_extracted'] != '20250528_120000' else "❌")
    print("Metadata cleaning working:", "✅" if migrations[0]['metadata_after'] < migrations[0]['metadata_before'] else "❌")

if __name__ == "__main__":
    test_migration_sample()