#!/usr/bin/env python3
"""
Repair TaskTracker manifest by scanning all task directories
"""

import json
from pathlib import Path
from datetime import datetime

TASKS_ROOT = Path("/Users/samuelatagana/Documents/Federation/Tasks")
MANIFEST_PATH = TASKS_ROOT / "manifest.json"

def repair_manifest():
    """Scan all task directories and rebuild manifest"""
    print("🔧 Repairing TaskTracker manifest...")
    
    # Load existing manifest
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest = json.load(f)
    else:
        manifest = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "tasks": {},
            "total_tasks": 0
        }
    
    # Scan all directories in Tasks folder
    found_tasks = {}
    for task_dir in TASKS_ROOT.iterdir():
        if task_dir.is_dir() and task_dir.name.startswith("20"):
            # Check for index.json
            index_path = task_dir / "index.json"
            if index_path.exists():
                with open(index_path, 'r') as f:
                    index = json.load(f)
                
                task_id = index.get("task_id", task_dir.name)
                found_tasks[task_id] = {
                    "title": index.get("title", "Unknown"),
                    "created": index.get("created", "Unknown"),
                    "status": index.get("status", "unknown"),
                    "phase": index.get("phase", "unknown")
                }
                print(f"  ✅ Found: {task_id} - {index.get('title', 'Unknown')}")
    
    # Update manifest
    manifest["tasks"] = found_tasks
    manifest["total_tasks"] = len(found_tasks)
    manifest["updated"] = datetime.now().isoformat()
    manifest["repaired"] = True
    
    # Save repaired manifest
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Manifest repaired! Found {len(found_tasks)} tasks")
    return manifest

if __name__ == "__main__":
    repair_manifest()