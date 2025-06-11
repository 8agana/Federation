#!/usr/bin/env python3
"""
Export Federation Memories to JSON
Simple script to export all memories for viewing
"""

import chromadb
import json
from datetime import datetime
import os

def export_memories():
    base_path = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs"
    output_dir = "/Users/samuelatagana/Documents/Federation/Apps/ChromaDB_Browser/exports"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export CC memories
    try:
        print("Exporting CC memories...")
        cc_client = chromadb.PersistentClient(path=f"{base_path}/cc-federation")
        cc_collection = cc_client.get_collection("cc_memories")
        
        # Get all memories
        cc_results = cc_collection.get(limit=1000)
        
        cc_memories = []
        for i in range(len(cc_results['ids'])):
            cc_memories.append({
                'id': cc_results['ids'][i],
                'content': cc_results['documents'][i],
                'metadata': cc_results['metadatas'][i] if cc_results['metadatas'] else {},
            })
        
        # Save to file
        cc_file = os.path.join(output_dir, f"cc_memories_{timestamp}.json")
        with open(cc_file, 'w', encoding='utf-8') as f:
            json.dump(cc_memories, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported {len(cc_memories)} CC memories to {cc_file}")
        
    except Exception as e:
        print(f"✗ Error exporting CC memories: {e}")
    
    # Export DT memories
    try:
        print("\nExporting DT memories...")
        dt_client = chromadb.PersistentClient(path=f"{base_path}/dt-federation")
        dt_collection = dt_client.get_collection("dt_memories")
        
        # Get all memories
        dt_results = dt_collection.get(limit=1000)
        
        dt_memories = []
        for i in range(len(dt_results['ids'])):
            dt_memories.append({
                'id': dt_results['ids'][i],
                'content': dt_results['documents'][i],
                'metadata': dt_results['metadatas'][i] if dt_results['metadatas'] else {},
            })
        
        # Save to file
        dt_file = os.path.join(output_dir, f"dt_memories_{timestamp}.json")
        with open(dt_file, 'w', encoding='utf-8') as f:
            json.dump(dt_memories, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported {len(dt_memories)} DT memories to {dt_file}")
        
    except Exception as e:
        print(f"✗ Error exporting DT memories: {e}")
    
    # Create a simple HTML viewer
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Federation Memories - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .memory {{ 
            border: 1px solid #ddd; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px;
            background: #f9f9f9;
        }}
        .memory-header {{ 
            font-weight: bold; 
            color: #666;
            margin-bottom: 10px;
        }}
        .metadata {{ 
            font-size: 0.9em; 
            color: #888;
            margin-top: 10px;
        }}
        .search-box {{
            position: sticky;
            top: 0;
            background: white;
            padding: 10px 0;
            border-bottom: 1px solid #ddd;
            margin-bottom: 20px;
        }}
        input {{
            width: 100%;
            padding: 10px;
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <h1>Federation Memories Export</h1>
    <p>Exported at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    
    <div class="search-box">
        <input type="text" id="search" placeholder="Search memories..." onkeyup="filterMemories()">
    </div>
    
    <h2>CC Memories ({len(cc_memories) if 'cc_memories' in locals() else 0})</h2>
    <div id="cc-memories">
"""
    
    if 'cc_memories' in locals():
        for mem in cc_memories[:50]:  # First 50 for preview
            metadata_str = json.dumps(mem['metadata'], indent=2) if mem['metadata'] else "{}"
            html_content += f"""
        <div class="memory" data-content="{mem['content'].lower().replace('"', '&quot;')}">
            <div class="memory-header">{mem['id']}</div>
            <div>{mem['content'][:500]}{'...' if len(mem['content']) > 500 else ''}</div>
            <div class="metadata">
                <pre>{metadata_str}</pre>
            </div>
        </div>
"""
    
    html_content += """
    </div>
    
    <h2>DT Memories (""" + str(len(dt_memories) if 'dt_memories' in locals() else 0) + """)</h2>
    <div id="dt-memories">
"""
    
    if 'dt_memories' in locals():
        for mem in dt_memories[:50]:  # First 50 for preview
            metadata_str = json.dumps(mem['metadata'], indent=2) if mem['metadata'] else "{}"
            html_content += f"""
        <div class="memory" data-content="{mem['content'].lower().replace('"', '&quot;')}">
            <div class="memory-header">{mem['id']}</div>
            <div>{mem['content'][:500]}{'...' if len(mem['content']) > 500 else ''}</div>
            <div class="metadata">
                <pre>{metadata_str}</pre>
            </div>
        </div>
"""
    
    html_content += """
    </div>
    
    <script>
    function filterMemories() {
        const search = document.getElementById('search').value.toLowerCase();
        const memories = document.querySelectorAll('.memory');
        
        memories.forEach(memory => {
            const content = memory.getAttribute('data-content');
            if (content.includes(search)) {
                memory.style.display = 'block';
            } else {
                memory.style.display = 'none';
            }
        });
    }
    </script>
</body>
</html>
"""
    
    # Save HTML viewer
    html_file = os.path.join(output_dir, f"memories_viewer_{timestamp}.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✓ Created HTML viewer at {html_file}")
    print("\nYou can open the HTML file in your browser to view and search memories!")
    
    # Open in browser
    import webbrowser
    webbrowser.open(f"file://{os.path.abspath(html_file)}")

if __name__ == "__main__":
    export_memories()