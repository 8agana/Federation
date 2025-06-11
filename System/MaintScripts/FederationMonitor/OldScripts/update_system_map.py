#!/usr/bin/env python3
"""
Federation System Map Updater
============================

Updates the "Directory Structure Overview" section in Federation_Map.md
with the actual current directory structure.

Features:
- Generates ASCII tree diagram from real directory structure
- Preserves manual comments and descriptions
- Ignores binary/system directories (ChromaDB UUIDs, etc.)
- Updates only the tree section, preserves rest of file

Usage:
    python3 update_system_map.py [--dry-run] [--max-depth=3]
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set

class SystemMapUpdater:
    def __init__(self, federation_root: str, max_depth: int = 3):
        self.federation_root = Path(federation_root)
        self.map_file = self.federation_root / "Federation_Map.md"
        self.max_depth = max_depth
        
        # Directories to ignore (binary/system directories)
        self.ignore_patterns = {
            '.DS_Store', '.git', '__pycache__', 'node_modules',
            # ChromaDB UUID directories (36-char hex with dashes)
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        }
        
        # Directory descriptions/comments
        self.dir_comments = {
            'Tasks': '# Active project tracking (until task system built)',
            'System': '# Core system components and utilities',
            'System/Memory': '# Shared memory systems and databases',
            'System/Memory/1_ChromaDBs': '# ChromaDB storage (binary files grouped)',
            'System/Memory/3_MemoryMCPs': '# Memory interface MCPs',
            'System/MaintScripts': '# Maintenance and admin scripts',
            'System/MaintScripts/FederationMonitor': '# Federation monitoring tools',
            'Documents': '# Documentation for the federation',
            'Documents/CC_DOCS': '# CC-specific docs',
            'Documents/DT_DOCS': '# DT-specific docs',
            'ExternalMCPs': '# Third-party MCPs we use',
            'LegacyMindMCPs': '# Our custom MCPs',
            'LegacyMindMCPs/core': '# Core MCP (always loaded)',
            'LegacyMindMCPs/shared': '# Shared utilities'
        }
    
    def should_ignore_directory(self, dir_name: str) -> bool:
        """Check if directory should be ignored."""
        for pattern in self.ignore_patterns:
            if pattern.startswith('^') and pattern.endswith('$'):
                # Regex pattern
                if re.match(pattern, dir_name):
                    return True
            elif dir_name == pattern:
                return True
        return False
    
    def generate_tree_structure(self, start_path: Path, prefix: str = "", depth: int = 0) -> List[str]:
        """Generate ASCII tree structure."""
        if depth > self.max_depth:
            return []
        
        tree_lines = []
        
        # Get directories, sorted
        try:
            dirs = [d for d in start_path.iterdir() 
                   if d.is_dir() and not self.should_ignore_directory(d.name)]
            dirs.sort(key=lambda x: x.name.lower())
        except PermissionError:
            return []
        
        for i, dir_path in enumerate(dirs):
            is_last = (i == len(dirs) - 1)
            
            # Create tree symbols
            if is_last:
                tree_symbol = "└── "
                next_prefix = prefix + "    "
            else:
                tree_symbol = "├── "
                next_prefix = prefix + "│   "
            
            # Get relative path for comment lookup
            rel_path = dir_path.relative_to(self.federation_root)
            rel_path_str = str(rel_path).replace('\\', '/')
            
            # Add comment if available
            comment = ""
            if rel_path_str in self.dir_comments:
                comment = f"  {self.dir_comments[rel_path_str]}"
            
            tree_lines.append(f"{prefix}{tree_symbol}{dir_path.name}/{comment}")
            
            # Recurse into subdirectories
            if depth < self.max_depth:
                subtree = self.generate_tree_structure(dir_path, next_prefix, depth + 1)
                tree_lines.extend(subtree)
        
        return tree_lines
    
    def update_map_file(self, dry_run: bool = False) -> bool:
        """Update the Directory Structure Overview section."""
        if not self.map_file.exists():
            print(f"Error: {self.map_file} does not exist")
            return False
        
        # Read existing file
        with open(self.map_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate new tree structure
        tree_lines = self.generate_tree_structure(self.federation_root)
        
        # Create new tree section
        new_tree = f"/Users/samuelatagana/Documents/Federation/\n" + "\n".join(tree_lines)
        
        # Find and replace the tree section
        pattern = r'(## Directory Structure Overview\n\n```\n)(.*?)(\n```)'
        
        def replace_tree(match):
            return f"{match.group(1)}{new_tree}{match.group(3)}"
        
        updated_content = re.sub(pattern, replace_tree, content, flags=re.DOTALL)
        
        if dry_run:
            print("DRY RUN - New tree structure would be:")
            print(new_tree)
            return True
        
        # Write updated file
        with open(self.map_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"Updated system map in {self.map_file}")
        return True

def main():
    parser = argparse.ArgumentParser(description='Update Federation system map')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without updating')
    parser.add_argument('--max-depth', type=int, default=3, help='Maximum directory depth')
    parser.add_argument('--federation-root', default='/Users/samuelatagana/Documents/Federation',
                       help='Federation root directory')
    
    args = parser.parse_args()
    
    updater = SystemMapUpdater(args.federation_root, args.max_depth)
    
    try:
        success = updater.update_map_file(dry_run=args.dry_run)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
