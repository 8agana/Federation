# 🚀 Federation Memory Browser

A Finder-style ChromaDB browser for Sam's federation memories with mobile export capability.

## Quick Start
```bash
# Test and launch the browser
python test_browser.py

# Or run directly
python federation_browser.py
```

## Features
✅ **Finder-Style Interface**
- Tree navigation sidebar
- Grid/List view switching
- Inspector panel for details
- Real-time search

✅ **Mobile Export (NEW!)**
- Optimized JSON format for mobile DT
- Context-aware summaries
- Key points extraction
- Quick reference section

✅ **Memory Sources**
- CC Memories
- DT Memories  
- Shared Federation
- Smart folders (Recent, Priority, Victories)

✅ **Search & Filter**
- Real-time search across all fields
- Collection filtering
- Tag-based navigation

## Mobile Export Format
Exports use DT's suggested format optimized for mobile context:
```json
{
  "context_package": {
    "purpose": "Mobile DT Context",
    "search_context": "your query"
  },
  "memories": [
    {
      "title": "Memory Title",
      "summary": "Concise summary",
      "key_points": ["Point 1", "Point 2"],
      "relevance": "Why this matters"
    }
  ],
  "quick_reference": {
    "current_projects": [...],
    "recent_breakthroughs": [...],
    "active_issues": [...]
  }
}
```

## Installation
```bash
pip install flet chromadb
```

## Directory Structure
```
ChromaDB_Browser/
├── federation_browser.py   # Main application
├── test_browser.py        # Test & launch script
├── mockup.html           # Original design mockup
├── exports/              # JSON exports directory
└── README.md            # This file
```

## Usage
1. Launch with `python federation_browser.py`
2. Select collection in sidebar
3. Search or browse memories
4. Click memory to see details
5. Export results with "📤 Export Results" button

## Keyboard Shortcuts
- `⌘K` - Focus search (coming soon)
- `⌘E` - Export current view (coming soon)

## Notes
- Exports are saved to `exports/` directory
- Mobile exports limited to 50 memories for performance
- Automatically extracts key points and summaries