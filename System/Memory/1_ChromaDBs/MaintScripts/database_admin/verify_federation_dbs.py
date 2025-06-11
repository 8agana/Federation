#!/usr/bin/env python3
"""
Verify Federation Databases
Quick check to see what was created
"""

import chromadb
from pathlib import Path

def verify_databases():
    base_path = Path("/Users/samuelatagana/Documents/Federation/Memory/ChromaDBs")
    
    print("🔍 Federation Database Verification")
    print("=" * 40)
    
    # Check CC Federation
    print("\n📊 CC Federation Database:")
    try:
        cc_client = chromadb.PersistentClient(
            path=str(base_path / "cc-federation")
        )
        cc_collections = cc_client.list_collections()
        print(f"  Location: {base_path / 'cc-federation'}")
        print(f"  Collections: {len(cc_collections)}")
        for col in cc_collections:
            print(f"    - {col.name}: {col.count()} items")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Check DT Federation
    print("\n📊 DT Federation Database:")
    try:
        dt_client = chromadb.PersistentClient(
            path=str(base_path / "dt-federation")
        )
        dt_collections = dt_client.list_collections()
        print(f"  Location: {base_path / 'dt-federation'}")
        print(f"  Collections: {len(dt_collections)}")
        for col in dt_collections:
            print(f"    - {col.name}: {col.count()} items")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n✅ Verification complete!")

if __name__ == "__main__":
    verify_databases()