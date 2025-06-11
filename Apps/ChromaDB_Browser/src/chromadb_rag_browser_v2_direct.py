#!/usr/bin/env python3
"""
ChromaDB Memory Browser with Direct Federation RAG V2 Integration
Uses RAG tools directly without MCP server
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import chromadb
from datetime import datetime
import json
import uuid
from pathlib import Path
import threading
from functools import partial
import os
import sys
import time
from collections import deque
import re
import html
from typing import List, Dict, Any, Optional, Tuple

# Add Federation RAG to path
sys.path.append('/Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/federation_rag')

# Import parent class
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tkinter_memory_browser_v5_bigger import MemoryBrowserV5

# Import RAG V2 directly
try:
    from cc_federation_rag_v2 import CCFederationRAGv2
    RAG_AVAILABLE = True
    print("✓ RAG V2 imported successfully")
except ImportError as e:
    print(f"Warning: Could not import RAG V2: {e}")
    RAG_AVAILABLE = False
except Exception as e:
    print(f"Error during RAG V2 import: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    RAG_AVAILABLE = False

# v5 Schema domains and categories
V5_DOMAINS = ["identity", "technical", "session", "personal", "relationship", "operational", "creative", "historical"]
V5_CATEGORIES = ["core", "protocol", "solution", "context", "learning", "discovery", "guide", "analysis", "handoff"]


class DirectRAGClient:
    """Direct client for Federation RAG V2 tools"""
    
    def __init__(self):
        """Initialize direct RAG client"""
        if not RAG_AVAILABLE:
            raise ImportError("RAG V2 not available")
            
        # Initialize RAG engine
        print("Initializing Federation RAG V2...")
        self.rag = CCFederationRAGv2()
        
        # Tool descriptions
        self.tool_descriptions = {
            'query': "🚀 Fast daily driver - Current context from memories + knowledge graph + notes",
            'query_history': "📜 Timeline explorer - Includes historical JSON data for evolution patterns", 
            'query_files': "🔍 Code hunter - Search Federation files and technical documentation",
            'query_full': "🧠 Deep research - Comprehensive search across all 6 sources",
            'auto': "🤖 Smart auto-routing - Automatically detects intent and uses best tool"
        }
        
        # Map tool names to methods
        self.tool_methods = {
            'query': self.rag.rag_query,
            'query_history': self.rag.rag_query_history,
            'query_files': self.rag.rag_query_files,
            'query_full': self.rag.rag_query_full,
            'auto': self.rag.rag_auto
        }
    
    def query(self, query_text: str, tool: str = 'auto') -> Dict:
        """Execute RAG query with specified tool"""
        method = self.tool_methods.get(tool, self.rag.rag_auto)
        
        try:
            # Call the method with proper argument structure
            result = method({"query": query_text})
            return result
        except Exception as e:
            return {
                'error': str(e),
                'answer': f"Error executing query: {str(e)}",
                'contexts_found': 0,
                'sources_searched': [],
                'tool_used': tool
            }
    
    def get_sources(self) -> Dict:
        """Get available RAG sources"""
        try:
            return self.rag.rag_sources({})
        except Exception as e:
            return {'error': str(e)}
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            return self.rag.rag_cache_stats({})
        except Exception as e:
            return {'error': str(e)}
    
    def clear_cache(self, cache_type: Optional[str] = None) -> Dict:
        """Clear RAG cache"""
        try:
            args = {"cache_type": cache_type} if cache_type else {}
            return self.rag.rag_clear_cache(args)
        except Exception as e:
            return {'error': str(e)}


class RAGSearchPanel(ttk.Frame):
    """Dedicated panel for RAG search with all V2 tools"""
    
    def __init__(self, parent, memory_callback=None):
        super().__init__(parent)
        self.memory_callback = memory_callback
        
        # Initialize RAG client
        try:
            self.rag_client = DirectRAGClient()
            self.rag_available = True
            print("✓ RAG client initialized successfully")
        except Exception as e:
            print(f"RAG initialization failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.rag_client = None
            self.rag_available = False
        
        self.current_results = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the RAG search panel UI"""
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        title_label = ttk.Label(
            title_frame,
            text="🚀 Federation RAG V2 Search (Direct)",
            font=('Helvetica', 20, 'bold')
        )
        title_label.pack(side='left')
        
        # Status label
        self.status_label = ttk.Label(
            title_frame,
            text="Ready" if self.rag_available else "RAG Unavailable",
            font=('Helvetica', 12),
            foreground='gray' if self.rag_available else 'red'
        )
        self.status_label.pack(side='right')
        
        if not self.rag_available:
            error_label = ttk.Label(
                self,
                text="RAG V2 is not available. Please check dependencies.",
                font=('Helvetica', 14),
                foreground='red'
            )
            error_label.pack(padx=10, pady=20)
            return
        
        # Search frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=10, pady=5)
        
        # Search entry
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Helvetica', 14)
        )
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self.execute_search())
        
        # Tool selector
        self.tool_var = tk.StringVar(value='auto')
        tool_menu = ttk.OptionMenu(
            search_frame,
            self.tool_var,
            'auto',
            'auto',
            'query',
            'query_history',
            'query_files',
            'query_full',
            command=self.on_tool_change
        )
        tool_menu.pack(side='left', padx=(0, 5))
        
        # Search button
        search_btn = ttk.Button(
            search_frame,
            text="🔍 Search",
            command=self.execute_search
        )
        search_btn.pack(side='left')
        
        # Tool description
        self.tool_desc_var = tk.StringVar(value=self.rag_client.tool_descriptions['auto'])
        tool_desc = ttk.Label(
            self,
            textvariable=self.tool_desc_var,
            font=('Helvetica', 12),
            foreground='#2c3e50'
        )
        tool_desc.pack(fill='x', padx=10, pady=(0, 10))
        
        # Results notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Synthesis tab
        synthesis_frame = ttk.Frame(self.notebook)
        self.notebook.add(synthesis_frame, text='🤖 Synthesis')
        
        self.synthesis_text = scrolledtext.ScrolledText(
            synthesis_frame,
            wrap=tk.WORD,
            font=('Helvetica', 13),
            bg='#f0f8ff',
            height=15
        )
        self.synthesis_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Contexts tab
        contexts_frame = ttk.Frame(self.notebook)
        self.notebook.add(contexts_frame, text='📚 Source Contexts')
        
        self.contexts_text = scrolledtext.ScrolledText(
            contexts_frame,
            wrap=tk.WORD,
            font=('Courier', 11),
            bg='#f5f5f5',
            height=15
        )
        self.contexts_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Stats tab
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text='📊 Statistics')
        
        self.stats_text = scrolledtext.ScrolledText(
            stats_frame,
            wrap=tk.WORD,
            font=('Courier', 11),
            bg='#f5f5f5',
            height=15
        )
        self.stats_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Control buttons
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Button(
            controls_frame,
            text="📋 Copy Answer",
            command=self.copy_answer
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            controls_frame,
            text="🗑️ Clear Cache",
            command=self.clear_cache
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            controls_frame,
            text="📊 Cache Stats",
            command=self.show_cache_stats
        ).pack(side='left')
        
        ttk.Button(
            controls_frame,
            text="ℹ️ Show Sources",
            command=self.show_sources
        ).pack(side='left', padx=(5, 0))
    
    def on_tool_change(self, tool):
        """Update tool description when selection changes"""
        self.tool_desc_var.set(self.rag_client.tool_descriptions.get(tool, ""))
    
    def execute_search(self):
        """Execute RAG search with selected tool"""
        if not self.rag_available:
            messagebox.showerror("RAG Unavailable", "RAG V2 is not available")
            return
            
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search query")
            return
        
        tool = self.tool_var.get()
        self.status_label.config(text="Searching...", foreground='blue')
        self.notebook.select(0)  # Switch to synthesis tab
        
        # Clear previous results
        self.synthesis_text.delete(1.0, tk.END)
        self.contexts_text.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)
        
        # Show searching message
        self.synthesis_text.insert(1.0, f"Searching with {tool} tool...")
        
        # Run search in background
        def search():
            result = self.rag_client.query(query, tool)
            self.after(0, lambda: self.display_results(result))
        
        threading.Thread(target=search, daemon=True).start()
    
    def display_results(self, result: Dict):
        """Display RAG search results"""
        if 'error' in result:
            self.status_label.config(text="Error", foreground='red')
            self.synthesis_text.delete(1.0, tk.END)
            self.synthesis_text.insert(1.0, f"Error: {result['error']}")
            return
        
        # Update status
        contexts = result.get('contexts_found', 0)
        tool_used = result.get('tool_used', 'unknown')
        self.status_label.config(
            text=f"Found {contexts} contexts using {tool_used}",
            foreground='green'
        )
        
        # Display synthesis
        self.synthesis_text.delete(1.0, tk.END)
        answer = result.get('answer', 'No answer provided')
        self.synthesis_text.insert(1.0, answer)
        
        # Display contexts
        self.display_contexts(result)
        
        # Display stats
        self.display_stats(result)
        
        # Store results
        self.current_results = result.get('source_metadata', [])
    
    def display_contexts(self, result: Dict):
        """Display source contexts"""
        self.contexts_text.delete(1.0, tk.END)
        
        contexts = result.get('source_metadata', [])
        if not contexts:
            self.contexts_text.insert(1.0, "No source contexts available")
            return
        
        # Group by source
        by_source = {}
        for ctx in contexts:
            source = ctx.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(ctx)
        
        # Display grouped contexts
        for source, items in by_source.items():
            self.contexts_text.insert(tk.END, f"\n{'='*60}\n")
            self.contexts_text.insert(tk.END, f"SOURCE: {source.upper()} ({len(items)} items)\n")
            self.contexts_text.insert(tk.END, f"{'='*60}\n\n")
            
            for i, item in enumerate(items, 1):
                metadata = item.get('metadata', {})
                
                # Extract key fields based on source type
                if source == 'federation_files':
                    title = metadata.get('filename', 'Unknown file')
                    info = f"Path: {metadata.get('rel_path', 'Unknown')}"
                    extra = f"Modified: {metadata.get('modified', 'Unknown')}"
                else:
                    title = metadata.get('title') or metadata.get('memory_key', f"Memory {i}")
                    info = f"Type: {metadata.get('type', 'memory')}"
                    extra = f"Created: {metadata.get('created_at', 'Unknown')}"
                
                self.contexts_text.insert(tk.END, f"{i}. {title}\n")
                self.contexts_text.insert(tk.END, f"   {info}\n")
                self.contexts_text.insert(tk.END, f"   {extra}\n")
                
                # Add tags if present
                tags = metadata.get('tags', '')
                if tags:
                    self.contexts_text.insert(tk.END, f"   Tags: {tags}\n")
                
                self.contexts_text.insert(tk.END, "\n")
    
    def display_stats(self, result: Dict):
        """Display search statistics"""
        self.stats_text.delete(1.0, tk.END)
        
        stats = result.get('retrieval_stats', {})
        
        self.stats_text.insert(tk.END, "SEARCH STATISTICS\n")
        self.stats_text.insert(tk.END, "="*40 + "\n\n")
        
        # Tool and timing
        tool = result.get('tool_used', 'unknown')
        cache_ttl = result.get('cache_ttl', 'unknown')
        self.stats_text.insert(tk.END, f"Tool Used: {tool}\n")
        self.stats_text.insert(tk.END, f"Cache TTL: {cache_ttl}\n\n")
        
        # Sources searched
        sources = result.get('sources_searched', [])
        self.stats_text.insert(tk.END, f"Sources Searched ({len(sources)}):\n")
        for source in sources:
            self.stats_text.insert(tk.END, f"  • {source}\n")
        self.stats_text.insert(tk.END, "\n")
        
        # Retrieval stats
        self.stats_text.insert(tk.END, "Retrieval Performance:\n")
        total_time = 0
        total_contexts = 0
        
        for source, data in stats.items():
            count = data.get('count', 0)
            time_ms = data.get('time', 0) * 1000  # Convert to ms
            total_time += time_ms
            total_contexts += count
            
            self.stats_text.insert(tk.END, f"  {source}:\n")
            self.stats_text.insert(tk.END, f"    Contexts: {count}\n")
            self.stats_text.insert(tk.END, f"    Time: {time_ms:.1f}ms\n")
        
        self.stats_text.insert(tk.END, f"\nTotal Contexts: {total_contexts}\n")
        self.stats_text.insert(tk.END, f"Total Time: {total_time:.1f}ms\n")
        
        # Auto-routing info if present
        if tool == 'rag_auto':
            intent = result.get('auto_detected_intent', 'unknown')
            self.stats_text.insert(tk.END, f"\nAuto-Detected Intent: {intent}\n")
    
    def copy_answer(self):
        """Copy synthesis answer to clipboard"""
        answer = self.synthesis_text.get(1.0, tk.END).strip()
        if answer:
            self.clipboard_clear()
            self.clipboard_append(answer)
            self.status_label.config(text="Answer copied!", foreground='green')
            self.after(2000, lambda: self.status_label.config(text="Ready", foreground='gray'))
    
    def clear_cache(self):
        """Clear RAG cache"""
        if not self.rag_available:
            return
            
        tool = self.tool_var.get()
        if tool == 'auto':
            cache_type = None  # Clear all
        else:
            # Map tool names to cache types
            cache_map = {
                'query': 'daily',
                'query_history': 'history', 
                'query_files': 'files',
                'query_full': 'full'
            }
            cache_type = cache_map.get(tool)
        
        result = self.rag_client.clear_cache(cache_type)
        cache_name = cache_type or "all"
        messagebox.showinfo("Cache Cleared", f"Cleared {cache_name} cache")
    
    def show_cache_stats(self):
        """Show cache statistics"""
        if not self.rag_available:
            return
            
        stats = self.rag_client.get_cache_stats()
        
        # Format stats
        msg = "RAG Cache Statistics\n" + "="*30 + "\n\n"
        
        if 'error' in stats:
            msg += f"Error: {stats['error']}"
        else:
            cache_stats = stats.get('cache_stats', {})
            total = 0
            for cache_type, count in cache_stats.items():
                msg += f"{cache_type}: {count} cached queries\n"
                total += count
            
            msg += f"\nTotal: {total} cached queries"
        
        messagebox.showinfo("Cache Statistics", msg)
    
    def show_sources(self):
        """Show available RAG sources"""
        if not self.rag_available:
            return
            
        sources = self.rag_client.get_sources()
        
        msg = "Federation RAG V2 Sources\n" + "="*30 + "\n\n"
        
        if 'error' in sources:
            msg += f"Error: {sources['error']}"
        else:
            msg += f"Instance: {sources.get('instance', 'Unknown')}\n"
            msg += f"Version: {sources.get('version', 'Unknown')}\n\n"
            
            msg += "Available Retrievers:\n"
            for retriever in sources.get('available_retrievers', []):
                msg += f"  • {retriever}\n"
            
            msg += "\nSpecialized Tools:\n"
            tools = sources.get('specialized_tools', {})
            for tool, desc in tools.items():
                msg += f"  • {tool}: {desc}\n"
        
        messagebox.showinfo("RAG Sources", msg)


class MemoryBrowserRAGV2Direct(MemoryBrowserV5):
    """ChromaDB Memory Browser with Direct Federation RAG V2"""
    
    def __init__(self, root):
        # Initialize parent
        super().__init__(root)
        
        # Update window title
        self.root.title("Federation Memory Browser - RAG V2 DIRECT")
        
        # Add RAG panel
        self.add_rag_panel()
    
    def add_rag_panel(self):
        """Add the RAG V2 panel to the interface"""
        # Create a new tab in the main interface
        if hasattr(self, 'notebook'):
            # If using notebook layout
            self.rag_panel = RAGSearchPanel(self.notebook, self.load_memory_from_result)
            self.notebook.add(self.rag_panel, text="🚀 RAG V2 Search")
        else:
            # Add as a separate window
            rag_window = tk.Toplevel(self.root)
            rag_window.title("Federation RAG V2 Search (Direct)")
            rag_window.geometry("1000x700")
            
            self.rag_panel = RAGSearchPanel(rag_window, self.load_memory_from_result)
            self.rag_panel.pack(fill='both', expand=True)
            
            # Add menu item to show RAG window
            if hasattr(self, 'menubar'):
                tools_menu = None
                for menu in self.menubar.winfo_children():
                    if menu.cget('text') == 'Tools':
                        tools_menu = menu
                        break
                
                if tools_menu:
                    tools_menu.add_separator()
                    tools_menu.add_command(
                        label="Federation RAG V2 Search",
                        command=lambda: rag_window.deiconify()
                    )
    
    def load_memory_from_result(self, result_metadata: Dict):
        """Load a memory from RAG result metadata"""
        # This would integrate with the memory browser to show the full memory
        memory_id = result_metadata.get('id') or result_metadata.get('memory_id')
        if memory_id:
            # Find and display the memory
            for memory in self.all_memories:
                if memory.get('id') == memory_id:
                    self.show_memory_detail(memory)
                    break


def main():
    # Set GROQ API key if not already set
    if not os.getenv('GROQ_API_KEY'):
        os.environ['GROQ_API_KEY'] = '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'
    
    root = tk.Tk()
    app = MemoryBrowserRAGV2Direct(root)
    root.mainloop()

if __name__ == "__main__":
    main()