#!/usr/bin/env python3
"""
Obsidian Emergency Access Script
Direct access to notes when MCP is down
Author: CCD
Created: 2025-06-09
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import re

# Vault paths
NERVE_CENTER = "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center"
SHARED_VAULT = "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault"

def search_notes(vault_path, query, max_results=20):
    """Search all notes in vault for query"""
    vault = Path(vault_path)
    if not vault.exists():
        print(f"❌ Vault not found: {vault_path}")
        return
    
    print(f"\n🔍 Searching for '{query}' in {vault.name}...\n")
    
    results = []
    for md_file in vault.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
            if query.lower() in content.lower():
                # Get context around match
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if query.lower() in line.lower():
                        preview = line.strip()[:100]
                        results.append({
                            'path': md_file,
                            'title': md_file.stem,
                            'folder': md_file.parent.name,
                            'preview': preview,
                            'line': i + 1
                        })
                        if len(results) >= max_results:
                            break
                
        except Exception as e:
            continue
    
    # Display results
    print(f"Found {len(results)} matches:\n")
    for i, result in enumerate(results[:max_results]):
        print(f"{i+1}. {result['title']}")
        print(f"   Folder: {result['folder']}")
        print(f"   Line {result['line']}: {result['preview']}...")
        print(f"   Path: {result['path']}")
        print()

def read_note(title, folder=None, vault_path=NERVE_CENTER):
    """Read a specific note"""
    vault = Path(vault_path)
    
    # Search for note
    found = None
    for md_file in vault.rglob("*.md"):
        if md_file.stem == title:
            if folder is None or folder in str(md_file):
                found = md_file
                break
    
    if not found:
        print(f"❌ Note '{title}' not found")
        return
    
    try:
        content = found.read_text(encoding='utf-8')
        print(f"\n📄 {title}")
        print(f"Folder: {found.parent.name}")
        print(f"Path: {found}")
        print("-" * 60)
        print(content)
    except Exception as e:
        print(f"❌ Failed to read note: {e}")

def create_note(title, content, folder="🧠 Knowledge", vault_path=NERVE_CENTER):
    """Create a new note"""
    vault = Path(vault_path)
    folder_path = vault / folder
    
    # Create folder if needed
    folder_path.mkdir(parents=True, exist_ok=True)
    
    # Create note
    note_path = folder_path / f"{title}.md"
    
    if note_path.exists():
        print(f"❌ Note already exists: {note_path}")
        return
    
    try:
        note_path.write_text(content, encoding='utf-8')
        print(f"✅ Note created: {note_path}")
    except Exception as e:
        print(f"❌ Failed to create note: {e}")def list_notes(folder=None, vault_path=NERVE_CENTER):
    """List all notes in folder"""
    vault = Path(vault_path)
    
    if folder:
        search_path = vault / folder
        if not search_path.exists():
            print(f"❌ Folder not found: {folder}")
            return
    else:
        search_path = vault
    
    print(f"\n📁 Notes in {search_path}:\n")
    
    notes = []
    for md_file in search_path.rglob("*.md"):
        # Get relative path from search path
        rel_path = md_file.relative_to(search_path)
        notes.append({
            'title': md_file.stem,
            'folder': rel_path.parent,
            'path': md_file
        })
    
    # Sort by folder then title
    notes.sort(key=lambda x: (str(x['folder']), x['title']))
    
    current_folder = None
    for note in notes:
        if note['folder'] != current_folder:
            current_folder = note['folder']
            print(f"\n📂 {current_folder}/" if str(current_folder) != "." else "\n📂 Root")
        print(f"  📄 {note['title']}")

def create_daily_note(summary="", vault_path=NERVE_CENTER):
    """Create today's daily note"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""# {today}

## Summary
{summary}

## Key Events

## Reflections

## Tomorrow

---
Created: {datetime.now().strftime("%Y-%m-%d %H:%M")}
Author: CCD (Emergency Access)
"""
    
    create_note(today, content, "💭 Daily Notes", vault_path)

def main():
    parser = argparse.ArgumentParser(description="Obsidian Emergency Access")
    parser.add_argument('--vault', choices=['nerve', 'shared'], default='nerve',
                        help='Which vault to use (nerve=Nerve Center, shared=SharedVault)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search notes')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('-n', '--number', type=int, default=20, help='Max results')
    
    # Read command
    read_parser = subparsers.add_parser('read', help='Read a note')
    read_parser.add_argument('title', help='Note title')
    read_parser.add_argument('-f', '--folder', help='Folder to search in')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a note')
    create_parser.add_argument('title', help='Note title')
    create_parser.add_argument('content', help='Note content')
    create_parser.add_argument('-f', '--folder', default='🧠 Knowledge', help='Target folder')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List notes')
    list_parser.add_argument('folder', nargs='?', help='Folder to list')
    
    # Daily command
    daily_parser = subparsers.add_parser('daily', help='Create daily note')
    daily_parser.add_argument('summary', nargs='?', default='', help='Day summary')
    
    args = parser.parse_args()
    
    # Select vault
    vault = NERVE_CENTER if args.vault == 'nerve' else SHARED_VAULT
    
    if args.command == 'search':
        search_notes(vault, args.query, args.number)
    elif args.command == 'read':
        read_note(args.title, args.folder, vault)
    elif args.command == 'create':
        create_note(args.title, args.content, args.folder, vault)
    elif args.command == 'list':
        list_notes(args.folder, vault)
    elif args.command == 'daily':
        create_daily_note(args.summary, vault)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()