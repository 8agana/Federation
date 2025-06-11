#!/usr/bin/env python3
"""
Federation Map Complete Rebuilder
=================================

Scans for changes and completely rebuilds Federation_Map.md from scratch.
If changes detected, backs up old file before writing new one.
"""

import os
import re
import sys
import argparse
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

class FederationRebuilder:
    def __init__(self, federation_root: str):
        self.federation_root = Path(federation_root)
        self.map_file = self.federation_root / "Federation_Map.md"
        self.backup_dir = self.federation_root / "System/MaintScripts/FederationMonitor/backups"
        
        # Files to ignore
        self.ignore_patterns = {
            '.DS_Store', '.git', '__pycache__', '*.pyc', '.env', 'node_modules',
            'venv', '.venv', 'env', '.env', 'virtualenv', '.virtualenv',
            '*.egg-info', 'dist', 'build', '.pytest_cache', '.coverage',
            '.mypy_cache', '.tox', '.nox', '__pycache__'
        }
        self.binary_extensions = {'.bin', '.sqlite3', '.db', '.data'}
        
        # Directory descriptions
        self.dir_comments = {
            'Documents': '# Documentation for the federation',
            'Documents/CC_DOCS': '# CC-specific docs', 
            'Documents/DT_DOCS': '# DT-specific docs',
            'System': '# Core system components and utilities',
            'System/ExternalMCPs': '# Third-party MCPs we use',
            'System/MaintScripts': '# Maintenance and admin scripts',
            'System/MaintScripts/FederationMonitor': '# Federation monitoring tools',
            'System/Memory': '# Shared memory systems and databases',
            'System/Memory/1_ChromaDBs': '# ChromaDB storage (binary files grouped)',
            'System/Memory/2_BridgeScripts': '# Bridge scripts for system integration',
            'System/Memory/3_MemoryMCPs': '# Memory interface MCPs',
            'System/TaskTracker': '# Task tracking system',
            'Tasks': '# Active project tracking (until task system built)'
        }
    
    def should_ignore_file(self, file_path: Path) -> bool:
        name = file_path.name
        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern:
                return True
        return False
    
    def should_ignore_directory(self, dir_name: str) -> bool:
        # Ignore ChromaDB UUID directories
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if re.match(uuid_pattern, dir_name):
            return True
        
        # Check if directory matches ignore patterns
        return dir_name in self.ignore_patterns
    
    def scan_current_files(self) -> Set[str]:
        current_files = set()
        for root, dirs, filenames in os.walk(self.federation_root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and not self.should_ignore_directory(d)]
            root_path = Path(root)
            
            for filename in filenames:
                file_path = root_path / filename
                if self.should_ignore_file(file_path):
                    continue
                rel_path = file_path.relative_to(self.federation_root)
                current_files.add(str(rel_path))
        return current_files
    
    def get_documented_files(self) -> Set[str]:
        if not self.map_file.exists():
            return set()
        
        documented = set()
        with open(self.map_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        registry_match = re.search(r'## Complete File Registry\n(.*?)(?=\n## |$)', content, re.DOTALL)
        if not registry_match:
            return set()
        
        registry_content = registry_match.group(1)
        sections = re.findall(r'### (/[^/\n]*(?:/[^/\n]*)*/?)\n(.*?)(?=\n### |$)', registry_content, re.DOTALL)
        
        for section_path, section_content in sections:
            file_entries = re.findall(r'- `([^`]+)` -', section_content)
            for filename in file_entries:
                if '(ChromaDB)' in filename:
                    continue
                if section_path == '/':
                    rel_path = filename
                else:
                    rel_path = f"{section_path.strip('/')}/{filename}"
                documented.add(rel_path)
        
        return documented
    
    def detect_changes(self) -> Tuple[Set[str], Set[str], Set[str]]:
        current_files = self.scan_current_files()
        documented_files = self.get_documented_files()
        added = current_files - documented_files
        removed = documented_files - current_files
        return current_files, added, removed
    
    def create_backup(self) -> str:
        if not self.map_file.exists():
            return ""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        backup_name = f"{timestamp}_Federation_Map.md"
        backup_path = self.backup_dir / backup_name
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.map_file, backup_path)
        return str(backup_path)
    
    def generate_tree_structure(self, start_path: Path, prefix: str = "", depth: int = 0, max_depth: int = 3) -> List[str]:
        if depth > max_depth:
            return []
        
        tree_lines = []
        try:
            dirs = [d for d in start_path.iterdir() 
                   if d.is_dir() and not self.should_ignore_directory(d.name)]
            dirs.sort(key=lambda x: x.name.lower())
        except PermissionError:
            return []
        
        for i, dir_path in enumerate(dirs):
            is_last = (i == len(dirs) - 1)
            tree_symbol = "└── " if is_last else "├── "
            next_prefix = prefix + ("    " if is_last else "│   ")
            
            rel_path = dir_path.relative_to(self.federation_root)
            rel_path_str = str(rel_path).replace('\\', '/')
            comment = f"  {self.dir_comments[rel_path_str]}" if rel_path_str in self.dir_comments else ""
            
            tree_lines.append(f"{prefix}{tree_symbol}{dir_path.name}/{comment}")
            
            if depth < max_depth:
                subtree = self.generate_tree_structure(dir_path, next_prefix, depth + 1, max_depth)
                tree_lines.extend(subtree)
        
        return tree_lines
    
    def group_chromadb_files(self, files: List[Dict]) -> List[Dict]:
        grouped = []
        chromadb_dirs = {}
        regular_files = []
        
        for file_info in files:
            if file_info['is_binary'] and any(pattern in file_info['path'] for pattern in ['chroma', 'data_level', 'header', 'length', 'link_lists']):
                path_parts = file_info['path'].split('/')
                if 'ChromaDBs' in path_parts:
                    db_name = None
                    for part in path_parts:
                        if 'federation' in part.lower():
                            db_name = part
                            break
                    
                    if db_name:
                        if db_name not in chromadb_dirs:
                            chromadb_dirs[db_name] = []
                        chromadb_dirs[db_name].append(file_info)
                        continue
            
            regular_files.append(file_info)
        
        for db_name, db_files in chromadb_dirs.items():
            file_count = len(db_files)
            total_size = sum(f['size'] for f in db_files)
            size_mb = total_size / (1024 * 1024)
            
            grouped.append({
                'name': f'{db_name}/ (ChromaDB)',
                'path': f'ChromaDBs/{db_name}/',
                'is_binary': True,
                'description': f'ChromaDB database files ({file_count} files, {size_mb:.1f}MB)',
                'size': total_size
            })
        
        return regular_files + grouped
    
    def generate_file_description(self, filename: str) -> str:
        if filename.endswith('.md'):
            if 'README' in filename.upper():
                return 'Documentation and setup instructions'
            elif 'implementation' in filename.lower():
                return 'Implementation documentation'
            elif 'checklist' in filename.lower():
                return 'Task checklist and progress tracking'
            elif 'architecture' in filename.lower():
                return 'System architecture documentation'
            elif 'roadmap' in filename.lower():
                return 'Development roadmap and planning'
            elif 'build' in filename.lower():
                return 'Build process documentation'
            else:
                return 'Documentation file'
        elif filename.endswith('.py'):
            if 'monitor' in filename.lower():
                return 'Monitoring and tracking system'
            elif 'initialize' in filename.lower():
                return 'Initialization script'
            elif 'verify' in filename.lower():
                return 'Verification and validation script'
            elif 'rebuild' in filename.lower():
                return 'Rebuild and regeneration script'
            elif 'audit' in filename.lower():
                return 'Audit and validation tool'
            else:
                return 'Python script'
        elif filename.endswith('.sh'):
            return 'Shell script'
        elif filename.endswith('.json'):
            return 'Configuration file'
        else:
            return 'System file'
    
    def generate_complete_map(self, current_files: Set[str]) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        # Organize files by directory
        file_structure = {}
        for file_path_str in current_files:
            file_path = Path(file_path_str)
            dir_key = str(file_path.parent) if str(file_path.parent) != '.' else '/'
            
            if dir_key not in file_structure:
                file_structure[dir_key] = []
            
            file_info = {
                'name': file_path.name,
                'path': file_path_str,
                'is_binary': file_path.suffix.lower() in self.binary_extensions,
                'size': 0
            }
            file_structure[dir_key].append(file_info)
        
        # Sort files within each directory
        for files in file_structure.values():
            files.sort(key=lambda x: x['name'].lower())
        
        # Generate tree structure
        tree_lines = self.generate_tree_structure(self.federation_root)
        tree_content = "/Users/samuelatagana/Documents/Federation/\n" + "\n".join(tree_lines)
        
        # Generate complete map content
        content = f"""# Federation Map
## Complete Directory Structure and File Registry

*Last Updated: {timestamp}*
*Purpose: Track all files and directories in the Federation structure*

---

## Directory Structure Overview

```
{tree_content}
```

---

## Complete File Registry

"""
        
        # Generate file registry sections
        for dir_path in sorted(file_structure.keys()):
            if dir_path == '/':
                section_title = '### /'
            else:
                section_title = f'### /{dir_path}/'
            
            files = file_structure[dir_path]
            if not files:
                continue
            
            content += f"{section_title}\n"
            
            # Group ChromaDB files if in ChromaDBs directory
            if 'ChromaDBs' in dir_path:
                files = self.group_chromadb_files(files)
            
            for file_info in files:
                filename = file_info['name']
                description = file_info.get('description', self.generate_file_description(filename))
                content += f"- `{filename}` - {description}\n"
            
            content += "\n"
        
        # Add footer
        content += f"""---

## Update Log

### {timestamp}
- Complete rebuild via rebuild_map.py
- Generated from current filesystem scan
- Eliminated any phantom entries

---

## Usage Guidelines

1. **This map is auto-generated** - do not edit manually
2. **Run rebuild_map.py** to update when changes detected
3. **Backups created automatically** when changes found
4. **File descriptions** are auto-generated based on filename patterns

---

## Quick Reference Paths

**Core Locations:**
- Documentation: `/Users/samuelatagana/Documents/Federation/Documents/`
- System Components: `/Users/samuelatagana/Documents/Federation/System/`
- Active Tasks: `/Users/samuelatagana/Documents/Federation/Tasks/`

**Key Files:**
- This Map: `/Users/samuelatagana/Documents/Federation/Federation_Map.md`
- Rebuild Script: `/Users/samuelatagana/Documents/Federation/System/MaintScripts/FederationMonitor/rebuild_map.py`

---

*This map is auto-generated from filesystem scan - reflects actual structure*"""
        
        return content
    
    def rebuild_map(self, force: bool = False, dry_run: bool = False, verbose: bool = False) -> bool:
        """Main rebuild process."""
        if verbose:
            print(f"🔍 Scanning Federation directory: {self.federation_root}")
        
        # Detect changes
        current_files, added, removed = self.detect_changes()
        
        has_changes = bool(added or removed)
        
        if verbose or has_changes:
            print(f"\n📊 CHANGE SUMMARY:")
            print(f"  Current files: {len(current_files)}")
            print(f"  Added: {len(added)}")
            print(f"  Removed: {len(removed)}")
            
            if added:
                print(f"\n📁 ADDED FILES:")
                for file_path in sorted(added):
                    print(f"  + {file_path}")
            
            if removed:
                print(f"\n🗑️ REMOVED FILES:")
                for file_path in sorted(removed):
                    print(f"  - {file_path}")
        
        if not has_changes and not force:
            print("✅ No changes detected - Federation_Map.md is current")
            return True
        
        if dry_run:
            print(f"\n🧪 DRY RUN - Would rebuild Federation_Map.md")
            if has_changes:
                print(f"  Would create backup and generate new map")
            return True
        
        # Create backup if changes detected
        backup_path = ""
        if has_changes and self.map_file.exists():
            backup_path = self.create_backup()
            if verbose:
                print(f"\n💾 Created backup: {backup_path}")
        
        # Generate new map content
        if verbose:
            print(f"\n🔄 Generating new Federation_Map.md...")
        
        new_content = self.generate_complete_map(current_files)
        
        # Write new file
        with open(self.map_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Federation_Map.md rebuilt successfully")
        if backup_path:
            print(f"   Backup saved: {Path(backup_path).name}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Rebuild Federation Map from scratch')
    parser.add_argument('--force', action='store_true', help='Rebuild even if no changes detected')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without doing it')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--federation-root', default='/Users/samuelatagana/Documents/Federation',
                       help='Federation root directory')
    
    args = parser.parse_args()
    
    rebuilder = FederationRebuilder(args.federation_root)
    
    try:
        success = rebuilder.rebuild_map(
            force=args.force, 
            dry_run=args.dry_run, 
            verbose=args.verbose
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
