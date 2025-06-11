#!/usr/bin/env python3
"""
Federation Directory Monitor and Documentation Updater
======================================================

Monitors the Federation directory structure and automatically updates
Federation_Map.md when changes are detected.

Features:
- Scans entire Federation directory tree
- Compares against existing documentation
- Preserves manual descriptions and formatting
- Groups related files logically
- Filters out system files
- Adds timestamped update log entries

Usage:
    python3 federation_monitor.py [--dry-run] [--verbose]
    
    --dry-run   : Show what would be changed without updating
    --verbose   : Show detailed scanning information
"""

import os
import re
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

class FederationMonitor:
    def __init__(self, federation_root: str):
        self.federation_root = Path(federation_root)
        self.map_file = self.federation_root / "Federation_Map.md"
        
        # Files to ignore completely
        self.ignore_patterns = {
            '.DS_Store',
            '.git',
            '__pycache__',
            '*.pyc',
            '.env',
            'node_modules'
        }
        
        # Binary file extensions to group together
        self.binary_extensions = {
            '.bin', '.sqlite3', '.db', '.data'
        }
        
        # Current state
        self.current_files: Dict[str, Dict] = {}
        self.documented_files: Dict[str, str] = {}
        
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
    
    def scan_directory_structure(self) -> Dict[str, Dict]:
        """Scan the Federation directory and catalog all files."""
        files = {}
        
        for root, dirs, filenames in os.walk(self.federation_root):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            root_path = Path(root)
            rel_root = root_path.relative_to(self.federation_root)
            
            for filename in filenames:
                file_path = root_path / filename
                
                if self.should_ignore_file(file_path):
                    continue
                
                rel_path = file_path.relative_to(self.federation_root)
                dir_key = str(rel_root) if str(rel_root) != '.' else '/'
                
                if dir_key not in files:
                    files[dir_key] = {'files': [], 'description': ''}
                
                files[dir_key]['files'].append({
                    'name': filename,
                    'path': str(rel_path),
                    'is_binary': file_path.suffix.lower() in self.binary_extensions,
                    'size': file_path.stat().st_size if file_path.exists() else 0,
                    'modified': file_path.stat().st_mtime if file_path.exists() else 0
                })
        
        # Sort files within each directory
        for dir_data in files.values():
            dir_data['files'].sort(key=lambda x: x['name'].lower())
        
        return files
    
    def parse_existing_map(self) -> Dict[str, str]:
        """Parse the existing Federation_Map.md to extract documented files."""
        if not self.map_file.exists():
            return {}
        
        documented = {}
        
        with open(self.map_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract file registry section
        registry_match = re.search(
            r'## Complete File Registry\n(.*?)(?=\n## |$)', 
            content, 
            re.DOTALL
        )
        
        if not registry_match:
            return {}
        
        registry_content = registry_match.group(1)
        
        # Parse each directory section
        sections = re.findall(
            r'### (/[^/\n]*(?:/[^/\n]*)*/?)\n(.*?)(?=\n### |$)',
            registry_content,
            re.DOTALL
        )
        
        for section_path, section_content in sections:
            # Extract file entries
            file_entries = re.findall(
                r'- `([^`]+)` - (.+)',
                section_content
            )
            
            for filename, description in file_entries:
                documented[f"{section_path.rstrip('/')}/{filename}"] = description
        
        return documented
    
    def group_chromadb_files(self, files: List[Dict]) -> List[Dict]:
        """Group ChromaDB binary files logically."""
        grouped = []
        chromadb_dirs = {}
        regular_files = []
        
        for file_info in files:
            if file_info['is_binary'] and any(
                pattern in file_info['path'] 
                for pattern in ['chroma', 'data_level', 'header', 'length', 'link_lists']
            ):
                # Extract ChromaDB directory
                path_parts = file_info['path'].split('/')
                if len(path_parts) >= 3 and 'ChromaDBs' in path_parts:
                    db_name = None
                    for i, part in enumerate(path_parts):
                        if 'federation' in part.lower():
                            db_name = part
                            break
                    
                    if db_name:
                        if db_name not in chromadb_dirs:
                            chromadb_dirs[db_name] = []
                        chromadb_dirs[db_name].append(file_info)
                        continue
            
            regular_files.append(file_info)
        
        # Add grouped ChromaDB entries
        for db_name, db_files in chromadb_dirs.items():
            file_count = len(db_files)
            total_size = sum(f['size'] for f in db_files)
            size_mb = total_size / (1024 * 1024)
            
            grouped.append({
                'name': f'{db_name}/ (ChromaDB)',
                'path': f'ChromaDBs/{db_name}/',
                'is_binary': True,
                'description': f'ChromaDB database files ({file_count} files, {size_mb:.1f}MB)',
                'size': total_size,
                'modified': max(f['modified'] for f in db_files)
            })
        
        return regular_files + grouped
    
    def generate_file_description(self, file_info: Dict) -> str:
        """Generate a description for a new file based on its name and type."""
        filename = file_info['name']
        
        # Common patterns
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
            else:
                return 'Python script'
        
        elif filename.endswith('.json'):
            return 'Configuration file'
        
        elif file_info['is_binary']:
            return 'Binary data file'
        
        else:
            return 'System file'
    
    def generate_updated_map(self, current_files: Dict, documented_files: Dict) -> str:
        """Generate updated Federation_Map.md content."""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        # Start with header
        content = f"""# Federation Map
## Complete Directory Structure and File Registry

*Last Updated: {timestamp}*
*Purpose: Track all files and directories in the Federation structure*

---

## Directory Structure Overview

```
/Users/samuelatagana/Documents/Federation/
├── Documents/                  # Documentation for the federation
│   ├── CC_DOCS/               # CC-specific docs
│   ├── DT_DOCS/               # DT-specific docs
│   └── Memory/                
│       └── SystemDocumentation/
├── Tasks/                     # Active project tracking (until task system built)
│   └── YYYYMMDD_HHMM_ProjectName/  # Date-prefixed project folders
│       └── YYYYMMDD_HHMM_SubTask/  # Nested subtasks
├── ExternalMCPs/              # Third-party MCPs we use
│   ├── github/
│   ├── brave-search/
│   └── filesystem/
├── Memory/                    # Shared memory systems
│   ├── ChromaDB/
│   └── Archives/
└── LegacyMindMCPs/           # Our custom MCPs
    ├── core/                  # Core MCP (always loaded)
    │   ├── src/
    │   │   ├── memory/
    │   │   ├── coordination/
    │   │   ├── communication/
    │   │   └── system/
    │   ├── tests/
    │   ├── package.json
    │   └── README.md
    ├── web_intelligence/      # Web Intelligence MCP
    ├── photography/           # Photography MCP
    ├── terminal_control/      # Terminal Control MCP
    ├── command_center/        # Visual Dashboard MCP
    ├── system_maintenance/    # System Health MCP
    └── shared/               # Shared utilities
        ├── token_monitor/
        ├── memory_interface/
        └── wake_scripts/
```

---

## Complete File Registry

"""
        
        # Generate file registry sections
        for dir_path in sorted(current_files.keys()):
            if dir_path == '/':
                section_title = '### /'
            else:
                section_title = f'### /{dir_path}/'
            
            dir_data = current_files[dir_path]
            files = dir_data['files']
            
            if not files:
                continue
            
            content += f"{section_title}\n"
            
            # Group ChromaDB files if in ChromaDBs directory
            if 'ChromaDBs' in dir_path:
                files = self.group_chromadb_files(files)
            
            for file_info in files:
                filename = file_info['name']
                file_key = f"/{dir_path}/{filename}".replace('//', '/').replace('///', '/')
                
                # Use existing description if available, otherwise generate one
                if file_key in documented_files:
                    description = documented_files[file_key]
                elif 'description' in file_info:
                    description = file_info['description']
                else:
                    description = self.generate_file_description(file_info)
                
                content += f"- `{filename}` - {description}\n"
            
            content += "\n"
        
        # Add footer sections
        content += self.get_footer_content()
        
        return content
    
    def get_footer_content(self) -> str:
        """Get the footer content for the map."""
        return """---

## Update Log

### 2025-06-08
- Automated update via federation_monitor.py
- Detected and documented new files
- Updated file registry with current structure

---

## Usage Guidelines

1. **Update this map whenever:**
   - A new file is created
   - A file is moved or renamed
   - A directory is added or removed
   - External MCPs are added

2. **File Entry Format:**
   ```
   - `filename.ext` - Brief description of purpose
   ```

3. **Directory Entry Format:**
   ```
   ### /Path/To/Directory/
   - `file1.md` - Description
   - `file2.py` - Description
   ```

4. **Keep entries alphabetical within each directory**

5. **Add entries to Update Log with date and changes**

---

## Quick Reference Paths

**Core Locations:**
- Documentation: `/Users/samuelatagana/Documents/Federation/Documents/`
- Legacy Mind MCPs: `/Users/samuelatagana/Documents/Federation/LegacyMindMCPs/`
- External MCPs: `/Users/samuelatagana/Documents/Federation/ExternalMCPs/`
- Shared Memory: `/Users/samuelatagana/Documents/Federation/Memory/`

**Key Files:**
- This Map: `/Users/samuelatagana/Documents/Federation/Federation_Map.md`

---

*This map is the source of truth for the Federation file structure*"""
    
    def run_monitor(self, dry_run: bool = False, verbose: bool = False) -> bool:
        """Run the monitoring process."""
        if verbose:
            print(f"Scanning Federation directory: {self.federation_root}")
        
        # Scan current structure
        self.current_files = self.scan_directory_structure()
        
        if verbose:
            total_files = sum(len(data['files']) for data in self.current_files.values())
            print(f"Found {total_files} files in {len(self.current_files)} directories")
        
        # Parse existing documentation
        self.documented_files = self.parse_existing_map()
        
        if verbose:
            print(f"Existing map documents {len(self.documented_files)} files")
        
        # Generate updated content
        updated_content = self.generate_updated_map(self.current_files, self.documented_files)
        
        if dry_run:
            print("DRY RUN - Would update Federation_Map.md with:")
            print(updated_content[:1000] + "..." if len(updated_content) > 1000 else updated_content)
            return True
        
        # Write updated map
        with open(self.map_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        if verbose:
            print(f"Updated {self.map_file}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Monitor Federation directory and update map')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without updating')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--federation-root', default='/Users/samuelatagana/Documents/Federation',
                       help='Federation root directory')
    
    args = parser.parse_args()
    
    monitor = FederationMonitor(args.federation_root)
    
    try:
        success = monitor.run_monitor(dry_run=args.dry_run, verbose=args.verbose)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
