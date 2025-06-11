#!/usr/bin/env python3
"""
Initialize CC and DT Federation ChromaDB Databases
Created: 2025-06-08
Purpose: Set up clean database architecture for Legacy Mind Federation
"""

import chromadb
from chromadb.config import Settings
import os
import json
from datetime import datetime
from pathlib import Path


class FederationDBInitializer:
    """Initialize federation databases for CC and DT"""
    
    def __init__(self):
        self.base_path = Path("/Users/samuelatagana/Documents/Federation/Memory/ChromaDBs")
        self.cc_path = self.base_path / "cc-federation"
        self.dt_path = self.base_path / "dt-federation"
        
    def initialize_cc_federation(self):
        """Initialize CC's federation database"""
        print("🔨 Initializing CC Federation Database...")
        
        # Create client
        client = chromadb.PersistentClient(
            path=str(self.cc_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Define collections
        collections = {
            "cc_memories": {
                "description": "CC's personal memory storage",
                "metadata": {"instance": "cc", "version": "v5", "type": "memories"}
            },
            "cc_context": {
                "description": "Active context and session data",
                "metadata": {"instance": "cc", "version": "v5", "type": "context"}
            },
            "cc_tasks": {
                "description": "Task chains and project tracking",
                "metadata": {"instance": "cc", "version": "v5", "type": "tasks"}
            },
            "cc_shared": {
                "description": "Memories marked for federation sharing",
                "metadata": {"instance": "cc", "version": "v5", "type": "shared", "federation": True}
            }
        }
        
        # Create collections
        for name, config in collections.items():
            try:
                collection = client.create_collection(
                    name=name,
                    metadata=config["metadata"]
                )
                print(f"  ✅ Created collection: {name}")
                
                # Add initial system memory
                collection.add(
                    documents=[f"Federation database initialized for {name}"],
                    metadatas=[{
                        "instance_id": "cc",
                        "federation_id": "cc-federation",
                        "created_by": "system",
                        "created_at": datetime.now().isoformat(),
                        "domain": "operational",
                        "category": "core",
                        "memory_type": "static",
                        "priority": 1,
                        "federation_visible": False,
                        "is_private": True,
                        "title": "Database Initialization",
                        "tags": "system, initialization, federation"
                    }],
                    ids=[f"{name}_init_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
                )
                
            except Exception as e:
                if "already exists" in str(e):
                    print(f"  ⚠️  Collection {name} already exists")
                else:
                    print(f"  ❌ Error creating {name}: {e}")
        
        print("✨ CC Federation Database initialized!\n")
        return client
    
    def initialize_dt_federation(self):
        """Initialize DT's federation database"""
        print("🔨 Initializing DT Federation Database...")
        
        # Create client
        client = chromadb.PersistentClient(
            path=str(self.dt_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Define collections (parallel to CC)
        collections = {
            "dt_memories": {
                "description": "DT's personal memory storage",
                "metadata": {"instance": "dt", "version": "v5", "type": "memories"}
            },
            "dt_context": {
                "description": "Active context and session data",
                "metadata": {"instance": "dt", "version": "v5", "type": "context"}
            },
            "dt_tasks": {
                "description": "Task chains and project tracking",
                "metadata": {"instance": "dt", "version": "v5", "type": "tasks"}
            },
            "dt_shared": {
                "description": "Memories marked for federation sharing",
                "metadata": {"instance": "dt", "version": "v5", "type": "shared", "federation": True}
            }
        }
        
        # Create collections
        for name, config in collections.items():
            try:
                collection = client.create_collection(
                    name=name,
                    metadata=config["metadata"]
                )
                print(f"  ✅ Created collection: {name}")
                
                # Add initial system memory
                collection.add(
                    documents=[f"Federation database initialized for {name}"],
                    metadatas=[{
                        "instance_id": "dt",
                        "federation_id": "dt-federation",
                        "created_by": "system",
                        "created_at": datetime.now().isoformat(),
                        "domain": "operational",
                        "category": "core",
                        "memory_type": "static",
                        "priority": 1,
                        "federation_visible": False,
                        "is_private": True,
                        "title": "Database Initialization",
                        "tags": "system, initialization, federation"
                    }],
                    ids=[f"{name}_init_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
                )
                
            except Exception as e:
                if "already exists" in str(e):
                    print(f"  ⚠️  Collection {name} already exists")
                else:
                    print(f"  ❌ Error creating {name}: {e}")
        
        print("✨ DT Federation Database initialized!\n")
        return client
    
    def verify_databases(self):
        """Verify both databases are properly initialized"""
        print("🔍 Verifying Federation Databases...")
        
        # Check CC
        try:
            cc_client = chromadb.PersistentClient(path=str(self.cc_path))
            cc_collections = cc_client.list_collections()
            print(f"\n📊 CC Federation Database:")
            print(f"  Path: {self.cc_path}")
            print(f"  Collections: {len(cc_collections)}")
            for col in cc_collections:
                count = col.count()
                print(f"    - {col.name}: {count} items")
        except Exception as e:
            print(f"  ❌ CC Database Error: {e}")
        
        # Check DT
        try:
            dt_client = chromadb.PersistentClient(path=str(self.dt_path))
            dt_collections = dt_client.list_collections()
            print(f"\n📊 DT Federation Database:")
            print(f"  Path: {self.dt_path}")
            print(f"  Collections: {len(dt_collections)}")
            for col in dt_collections:
                count = col.count()
                print(f"    - {col.name}: {count} items")
        except Exception as e:
            print(f"  ❌ DT Database Error: {e}")
        
        print("\n✅ Verification complete!")
    
    def create_test_memories(self):
        """Create some test memories to verify functionality"""
        print("\n🧪 Creating test memories...")
        
        # CC test memory
        cc_client = chromadb.PersistentClient(path=str(self.cc_path))
        cc_memories = cc_client.get_collection("cc_memories")
        
        cc_memories.add(
            documents=["This is CC's first test memory in the federation database"],
            metadatas=[{
                "instance_id": "cc",
                "federation_id": "cc-federation",
                "created_by": "cc",
                "created_at": datetime.now().isoformat(),
                "domain": "technical",
                "category": "learning",
                "memory_type": "reference",
                "priority": 2,
                "federation_visible": True,
                "is_private": False,
                "shared_with": "dt,all",
                "title": "First Federation Test",
                "tags": "test, federation, first"
            }],
            ids=[f"cc_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
        )
        print("  ✅ Created CC test memory")
        
        # DT test memory
        dt_client = chromadb.PersistentClient(path=str(self.dt_path))
        dt_memories = dt_client.get_collection("dt_memories")
        
        dt_memories.add(
            documents=["This is DT's first test memory in the federation database"],
            metadatas=[{
                "instance_id": "dt",
                "federation_id": "dt-federation",
                "created_by": "dt",
                "created_at": datetime.now().isoformat(),
                "domain": "technical",
                "category": "learning",
                "memory_type": "reference",
                "priority": 2,
                "federation_visible": True,
                "is_private": False,
                "shared_with": "cc,all",
                "title": "First Federation Test",
                "tags": "test, federation, first"
            }],
            ids=[f"dt_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"]
        )
        print("  ✅ Created DT test memory")
        
        print("\n🎉 Test memories created!")


def main():
    """Main initialization function"""
    print("🚀 Legacy Mind Federation Database Initializer")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    initializer = FederationDBInitializer()
    
    # Initialize databases
    initializer.initialize_cc_federation()
    initializer.initialize_dt_federation()
    
    # Verify setup
    initializer.verify_databases()
    
    # Create test data
    response = input("\nCreate test memories? (y/n): ")
    if response.lower() == 'y':
        initializer.create_test_memories()
    
    print("\n✨ Federation databases ready for Legacy Mind!")
    print("\nNext steps:")
    print("1. Update MCP servers to use these databases")
    print("2. Test federation search functionality")
    print("3. Build migration tools for existing data")
    print("4. Implement cross-instance queries")


if __name__ == "__main__":
    main()