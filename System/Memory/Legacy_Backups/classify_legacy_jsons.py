#!/usr/bin/env python3
"""
Legacy Memory JSON Classification Script
Adds AI attribution tags to distinguish between CC and DT entries
"""

import json
import os
import re
from pathlib import Path
import shutil
from datetime import datetime

def classify_entry(entry_data, key=""):
    """
    Classify an entry as CC, PresumedCC, DT, PresumedDT, or Unknown
    """
    # Convert entry to string for text analysis
    entry_text = json.dumps(entry_data).lower()
    
    # Strong CC indicators
    cc_strong = [
        "claude code", "claude_code", "studioc", '"cc"',
        "ssh", "terminal", "mobile access", "terminus app",
        "git", "applescript", "osascript", "hack china",
        "digital mercenary", "executor", "doer"
    ]
    
    # Strong DT indicators  
    dt_strong = [
        "desktop claude", "desktop_claude", '"dt"',
        "desktop app", "simplefs", "filesystem",
        "conversationalist", "friend", "write a book"
    ]
    
    # Moderate CC indicators
    cc_moderate = [
        "automation", "deployment", "technical breakthrough",
        "mobile", "iphone", "remote", "persistence",
        "breakthrough", "revolutionary"
    ]
    
    # Moderate DT indicators
    dt_moderate = [
        "conversation", "relationship", "chat", "dialogue",
        "desktop", "app version", "limited to filesystem"
    ]
    
    # Check tags if present
    tags = []
    if isinstance(entry_data, dict):
        if 'tags' in entry_data:
            tags = entry_data['tags'] if isinstance(entry_data['tags'], list) else [entry_data['tags']]
        elif 'category' in entry_data:
            tags = [entry_data['category']]
    
    tag_text = ' '.join(tags).lower()
    
    # Definitive classification from tags
    if 'cc' in tag_text or 'claude_code' in tag_text:
        return "CC"
    if 'dt' in tag_text and 'desktop' in tag_text:
        return "DT"
    
    # Check content for strong indicators
    cc_strong_count = sum(1 for indicator in cc_strong if indicator in entry_text)
    dt_strong_count = sum(1 for indicator in dt_strong if indicator in entry_text)
    
    if cc_strong_count > 0 and dt_strong_count == 0:
        return "CC"
    if dt_strong_count > 0 and cc_strong_count == 0:
        return "DT"
    if cc_strong_count > 0 and dt_strong_count > 0:
        return "Unknown"  # Mixed indicators
    
    # Check moderate indicators
    cc_moderate_count = sum(1 for indicator in cc_moderate if indicator in entry_text)
    dt_moderate_count = sum(1 for indicator in dt_moderate if indicator in entry_text)
    
    if cc_moderate_count > dt_moderate_count and cc_moderate_count >= 2:
        return "PresumedCC"
    if dt_moderate_count > cc_moderate_count and dt_moderate_count >= 2:
        return "PresumedDT"
    
    # Special handling for relationships file
    if "relationship" in entry_text:
        if "claude_code" in key.lower() or "cc" in key.lower():
            return "CC"
        if "desktop_claude" in key.lower() or "desktop" in key.lower():
            return "DT"
    
    return "Unknown"

def process_json_file(file_path):
    """
    Process a single JSON file and add ai_attribution tags
    """
    print(f"Processing {file_path.name}...")
    
    # Backup original
    backup_path = file_path.with_suffix('.json.backup')
    shutil.copy2(file_path, backup_path)
    print(f"  Created backup: {backup_path.name}")
    
    # Load JSON
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    classified_count = {"CC": 0, "PresumedCC": 0, "DT": 0, "PresumedDT": 0, "Unknown": 0}
    
    # Process different JSON structures
    if isinstance(data, dict):
        if 'entries' in data and isinstance(data['entries'], dict):
            # Structure: {"entries": {"key": {...}}}
            for key, entry in data['entries'].items():
                if key == 'metadata':
                    continue
                if isinstance(entry, dict):
                    classification = classify_entry(entry, key)
                    entry['ai_attribution'] = classification
                    classified_count[classification] += 1
        
        elif 'log' in data and isinstance(data['log'], list):
            # Structure: {"log": [{...}, {...}]}
            for entry in data['log']:
                if isinstance(entry, dict):
                    classification = classify_entry(entry)
                    entry['ai_attribution'] = classification
                    classified_count[classification] += 1
        
        else:
            # Direct structure: {"key": {...}}
            for key, entry in data.items():
                if key in ['metadata', 'schema_version']:
                    continue
                if isinstance(entry, dict):
                    classification = classify_entry(entry, key)
                    entry['ai_attribution'] = classification
                    classified_count[classification] += 1
    
    # Add processing metadata
    if 'metadata' not in data:
        data['metadata'] = {}
    
    data['metadata']['ai_attribution_processed'] = {
        'timestamp': datetime.now().isoformat(),
        'script_version': '1.0',
        'classifications': classified_count
    }
    
    # Save modified file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  Classifications: {classified_count}")
    return classified_count

def main():
    """
    Main processing function
    """
    json_dir = Path("/Users/samuelatagana/Documents/Federation/System/Memory/Legacy_Backups/MemoryJSONS")
    
    if not json_dir.exists():
        print(f"Directory not found: {json_dir}")
        return
    
    print("=== Legacy Memory JSON Classification ===")
    print(f"Processing directory: {json_dir}")
    print()
    
    total_counts = {"CC": 0, "PresumedCC": 0, "DT": 0, "PresumedDT": 0, "Unknown": 0}
    processed_files = 0
    
    # Process all JSON files
    for json_file in json_dir.glob("*.json"):
        if json_file.name.endswith('.backup'):
            continue
            
        try:
            file_counts = process_json_file(json_file)
            for key, count in file_counts.items():
                total_counts[key] += count
            processed_files += 1
            print()
        except Exception as e:
            print(f"  ERROR processing {json_file.name}: {e}")
            print()
    
    print("=== SUMMARY ===")
    print(f"Files processed: {processed_files}")
    print(f"Total classifications: {total_counts}")
    print(f"Backups created in same directory with .backup extension")

if __name__ == "__main__":
    main()