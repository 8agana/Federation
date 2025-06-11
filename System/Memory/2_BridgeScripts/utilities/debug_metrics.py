#!/usr/bin/env python3
"""
Debug the shared metrics to understand timestamp issues
"""

import sys
from pathlib import Path
from datetime import datetime
import chromadb

# Connect directly to shared DB
shared_db_path = Path("/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/shared-federation")
client = chromadb.PersistentClient(path=str(shared_db_path))
collection = client.get_collection("token_metrics")

# Get all entries
results = collection.get(
    limit=10,
    include=["metadatas", "documents"]
)

print("🔍 Debugging Token Metrics Collection")
print("=" * 60)
print(f"Total entries: {collection.count()}")
print("\nRecent entries:")

for i, (id, doc, meta) in enumerate(zip(results["ids"], results["documents"], results["metadatas"])):
    print(f"\nEntry {i+1}:")
    print(f"  ID: {id}")
    print(f"  Doc: {doc}")
    print(f"  Metadata:")
    for key, value in meta.items():
        print(f"    {key}: {value}")
    
    # Check timestamp format
    if "timestamp" in meta:
        ts = meta["timestamp"]
        if isinstance(ts, str):
            print(f"    Timestamp type: string (ISO format)")
            # Try to parse it
            try:
                dt = datetime.fromisoformat(ts)
                print(f"    Parsed datetime: {dt}")
                print(f"    Unix timestamp: {dt.timestamp()}")
            except:
                print(f"    Failed to parse timestamp")
        else:
            print(f"    Timestamp type: {type(ts)} value: {ts}")
            # If it's a float, convert to datetime
            if isinstance(ts, (int, float)):
                dt = datetime.fromtimestamp(ts)
                print(f"    As datetime: {dt}")

# Test query with proper timestamp
print("\n" + "=" * 60)
print("Testing timestamp queries...")

# Current time
now = datetime.now()
print(f"Current time: {now}")
print(f"Current unix timestamp: {now.timestamp()}")

# One hour ago
one_hour_ago = now.timestamp() - 3600
print(f"One hour ago timestamp: {one_hour_ago}")

# Try query
query_results = collection.get(
    where={"timestamp": {"$gte": one_hour_ago}},
    limit=100
)

print(f"\nQuery results for last hour: {len(query_results['ids'])} entries")