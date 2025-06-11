#!/usr/bin/env python3
"""
Health Check Script - Verify all systems are accessible
Author: CCD
Created: 2025-06-09
"""

import subprocess
import sys
from pathlib import Path
import chromadb
import json

def check_mcp_servers():
    """Check if MCP servers are running"""
    print("🔍 Checking MCP Servers...")
    
    # Check for MCP processes
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True
    )
    
    mcp_processes = [line for line in result.stdout.split('\n') if 'mcp' in line.lower() and 'python' in line]
    
    if mcp_processes:
        print("✅ MCP servers found:")
        for proc in mcp_processes:
            parts = proc.split()
            if len(parts) > 10:
                cmd = ' '.join(parts[10:])[:80]
                print(f"   - {cmd}...")
    else:
        print("❌ No MCP servers running")
    
    return len(mcp_processes) > 0

def check_chromadb():
    """Check ChromaDB accessibility"""
    print("\n🔍 Checking ChromaDB...")
    
    try:
        client = chromadb.PersistentClient(
            path="/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation"
        )
        collection = client.get_collection("cc_memories")
        count = collection.count()
        print(f"✅ ChromaDB accessible - {count} memories stored")
        return True
    except Exception as e:
        print(f"❌ ChromaDB error: {e}")
        return False

def check_obsidian_vaults():
    """Check Obsidian vault accessibility"""
    print("\n🔍 Checking Obsidian Vaults...")
    
    vaults = {
        "Nerve Center": "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center",
        "SharedVault": "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault"
    }
    
    all_good = True
    for name, path in vaults.items():
        vault_path = Path(path)
        if vault_path.exists():
            note_count = len(list(vault_path.rglob("*.md")))
            print(f"✅ {name}: {note_count} notes")
        else:
            print(f"❌ {name}: Not found at {path}")
            all_good = False
    
    return all_good

def check_backup_scripts():
    """Check if backup scripts are present"""
    print("\n🔍 Checking Backup Scripts...")
    
    scripts = [
        "chromadb_emergency.py",
        "obsidian_emergency.py",
        "unified_search.py",
        "health_check.py"
    ]
    
    script_dir = Path(__file__).parent
    all_good = True
    
    for script in scripts:
        script_path = script_dir / script
        if script_path.exists():
            print(f"✅ {script}")
        else:
            print(f"❌ {script} - Missing")
            all_good = False
    
    return all_good

def main():
    """Run all health checks"""
    print("=" * 60)
    print("🏥 System Health Check")
    print("=" * 60)
    
    results = {
        "MCP Servers": check_mcp_servers(),
        "ChromaDB": check_chromadb(),
        "Obsidian Vaults": check_obsidian_vaults(),
        "Backup Scripts": check_backup_scripts()
    }
    
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    all_good = True
    for system, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {system}: {'Operational' if status else 'Issues Detected'}")
        if not status:
            all_good = False
    
    if not all_good:
        print("\n⚠️  Some systems need attention!")
        print("Use the backup scripts for manual access.")
    else:
        print("\n✅ All systems operational!")
    
    # Save results
    results_file = Path(__file__).parent / "last_health_check.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": subprocess.run(["date"], capture_output=True, text=True).stdout.strip(),
            "results": results
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")

if __name__ == "__main__":
    main()