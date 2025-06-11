#!/usr/bin/env python3
"""
Federation Map Auditor
======================

Audits Federation_Map.md to find:
- Files documented but don't exist (phantoms)
- Files that exist but aren't documented (missing)
- Detailed comparison for debugging

Usage:
    python3 audit_map.py [--show-all]
"""

import os
import re
import argparse
from pathlib import Path
from typing import Set

class FederationAuditor:
    def __init__(self, federation_root: str):
        self.federation_root = Path(federation_root)
        self.map_file = self.federation_root / "Federation_Map.md"
        
        # Files to ignore
        self.ignore_patterns = {
            '.DS_Store', '.git', '__pycache__', '*.pyc', '.env', 'node_modules'
        }
    
    def should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        name = file_path.name
        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern:
                return True
        return False
    
    def get_actual_files(self) -> Set[str]:
        """Get set of files that actually exist."""
        actual_files = set()
        
        for root, dirs, filenames in os.walk(self.federation_root):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            root_path = Path(root)
            
            for filename in filenames:
                file_path = root_path / filename
                
                if self.should_ignore_file(file_path):
                    continue
                
                rel_path = file_path.relative_to(self.federation_root)
                actual_files.add(str(rel_path))
        
        return actual_files
    
    def get_documented_files(self) -> Set[str]:
        """Get set of files documented in Federation_Map.md."""
        if not self.map_file.exists():
            return set()
        
        documented = set()
        
        with open(self.map_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract file registry section
        registry_match = re.search(
            r'## Complete File Registry\n(.*?)(?=\n## |$)', 
            content, 
            re.DOTALL
        )
        
        if not registry_match:
            return set()
        
        registry_content = registry_match.group(1)
        
        # Parse each directory section
        sections = re.findall(
            r'### (/[^/\n]*(?:/[^/\n]*)*/?)\n(.*?)(?=\n### |$)',
            registry_content,
            re.DOTALL
        )
        
        for section_path, section_content in sections:
            # Extract file entries
            file_entries = re.findall(r'- `([^`]+)` -', section_content)
            
            for filename in file_entries:
                # Skip grouped entries like "cc-federation/ (ChromaDB)"
                if '(ChromaDB)' in filename:
                    continue
                    
                # Reconstruct relative path
                if section_path == '/':
                    rel_path = filename
                else:
                    rel_path = f"{section_path.strip('/')}/{filename}"
                
                documented.add(rel_path)
        
        return documented
    
    def audit_federation(self, show_all: bool = False) -> bool:
        """Perform audit and show results."""
        print(f"🔍 Auditing Federation directory: {self.federation_root}")
        print()
        
        actual_files = self.get_actual_files()
        documented_files = self.get_documented_files()
        
        phantoms = documented_files - actual_files  # In map but don't exist
        missing = actual_files - documented_files   # Exist but not in map
        
        print(f"📊 AUDIT SUMMARY:")
        print(f"  Actual files found: {len(actual_files)}")
        print(f"  Documented files: {len(documented_files)}")
        print(f"  Phantom entries: {len(phantoms)}")
        print(f"  Missing entries: {len(missing)}")
        print()
        
        has_issues = bool(phantoms or missing)
        
        if phantoms:
            print(f"👻 PHANTOM FILES ({len(phantoms)}) - Documented but don't exist:")
            for phantom in sorted(phantoms):
                print(f"  - {phantom}")
            print()
        
        if missing:
            print(f"❓ MISSING FILES ({len(missing)}) - Exist but not documented:")
            for missing_file in sorted(missing):
                print(f"  + {missing_file}")
            print()
        
        if not has_issues:
            print("✅ Perfect sync - All documented files exist and all existing files are documented")
        
        if show_all:
            print(f"\n📋 ALL ACTUAL FILES ({len(actual_files)}):")
            for file_path in sorted(actual_files):
                status = "✅" if file_path in documented_files else "❌"
                print(f"  {status} {file_path}")
        
        return not has_issues

def main():
    parser = argparse.ArgumentParser(description='Audit Federation Map accuracy')
    parser.add_argument('--show-all', action='store_true', help='Show all files with status')
    parser.add_argument('--federation-root', default='/Users/samuelatagana/Documents/Federation',
                       help='Federation root directory')
    
    args = parser.parse_args()
    
    auditor = FederationAuditor(args.federation_root)
    
    try:
        is_clean = auditor.audit_federation(show_all=args.show_all)
        exit_code = 0 if is_clean else 1
        return exit_code
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
