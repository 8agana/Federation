#!/usr/bin/env python3
"""
Enhanced Federation Monitor with Change Detection
================================================

Enhanced version that explicitly tracks and reports:
- Files added since last run
- Files removed since last run  
- Directory structure changes
- Detailed change summary

Usage:
    python3 enhanced_monitor.py [--dry-run] [--verbose]
"""

import os
import re
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

class EnhancedFederationMonitor:
    def __init__(self, federation_root: str):
        self.federation_root = Path(federation_root)
        self.map_file = self.federation_root / "Federation_Map.md"
        
        # Files to ignore completely
        self.ignore_patterns = {
            '.DS_Store', '.git', '__pycache__', '*.pyc', '.env', 'node_modules'
        }
        
        # Binary file extensions to group together
        self.binary_extensions = {
            '.bin', '.sqlite3', '.db', '.data'
        }
        
        # Change tracking
        self.current_files: Set[str] = set()
        self.documented_files: Set[str] = set()
        self.added_files: List[str] = []
        self.removed_files: List[str] = []
        
    def should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored based on patterns."""
        name = file_path.name
        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern:
                return True
        return False
    
    def scan_current_files(self) -> Set[str]:
        """Scan current files and return set of relative paths."""
        current_files = set()
        
        for root, dirs, filenames in os.walk(self.federation_root):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            root_path = Path(root)
            
            for filename in filenames:
                file_path = root_path / filename
                
                if self.should_ignore_file(file_path):
                    continue
                
                rel_path = file_path.relative_to(self.federation_root)
                current_files.add(str(rel_path))
        
        return current_files
    
    def parse_documented_files(self) -> Set[str]:
        """Parse documented files from Federation_Map.md."""
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
    
    def detect_changes(self) -> Tuple[List[str], List[str]]:
        """Detect added and removed files."""
        self.current_files = self.scan_current_files()
        self.documented_files = self.parse_documented_files()
        
        added = sorted(list(self.current_files - self.documented_files))
        removed = sorted(list(self.documented_files - self.current_files))
        
        return added, removed
    
    def run_enhanced_monitor(self, dry_run: bool = False, verbose: bool = False) -> bool:
        """Run enhanced monitoring with change detection."""
        if verbose:
            print(f"Scanning Federation directory: {self.federation_root}")
        
        # Detect changes
        added, removed = self.detect_changes()
        
        # Report changes
        if added or removed:
            print("\n=== FEDERATION CHANGES DETECTED ===")
            
            if added:
                print(f"\n📁 ADDED FILES ({len(added)}):")
                for file_path in added:
                    print(f"  + {file_path}")
            
            if removed:
                print(f"\n🗑️  REMOVED FILES ({len(removed)}):")
                for file_path in removed:
                    print(f"  - {file_path}")
            
            print(f"\n📊 SUMMARY:")
            print(f"  Current files: {len(self.current_files)}")
            print(f"  Previously documented: {len(self.documented_files)}")
            print(f"  Net change: {len(self.current_files) - len(self.documented_files):+d}")
            
        else:
            print("✅ No file changes detected - documentation is current")
        
        if dry_run:
            print("\nDRY RUN - Would update Federation_Map.md")
            return True
        
        # Run the original federation monitor to actually update
        import subprocess
        monitor_script = self.federation_root / "System/MaintScripts/FederationMonitor/federation_monitor.py"
        
        try:
            result = subprocess.run([
                sys.executable, str(monitor_script), 
                "--verbose" if verbose else ""
            ], cwd=self.federation_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"\n✅ Federation_Map.md updated successfully")
                return True
            else:
                print(f"\n❌ Error updating map: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error running federation_monitor.py: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Enhanced Federation monitoring with change detection')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without updating')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--federation-root', default='/Users/samuelatagana/Documents/Federation',
                       help='Federation root directory')
    
    args = parser.parse_args()
    
    monitor = EnhancedFederationMonitor(args.federation_root)
    
    try:
        success = monitor.run_enhanced_monitor(dry_run=args.dry_run, verbose=args.verbose)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
