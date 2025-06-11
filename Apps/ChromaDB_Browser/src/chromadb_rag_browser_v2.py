#!/usr/bin/env python3
"""
ChromaDB Memory Browser with Federation RAG V2 Integration
All 5 specialized RAG tools for optimal search performance
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
import time
from collections import deque
import re
import html
import requests
from typing import List, Dict, Any, Optional, Tuple

# RAG-specific imports
import hashlib
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.schema import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import parent class
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tkinter_memory_browser_v5_bigger import MemoryBrowserV5

# v5 Schema domains and categories
V5_DOMAINS = ["identity", "technical", "session", "personal", "relationship", "operational", "creative", "historical"]
V5_CATEGORIES = ["core", "protocol", "solution", "context", "learning", "discovery", "guide", "analysis", "handoff"]

class FederationRAGClient:
    """Client for Federation RAG V2 MCP tools"""
    
    def __init__(self):
        """Initialize RAG client with MCP endpoints"""
        # Get instance type from environment or default to CC
        self.instance = os.getenv('FEDERATION_INSTANCE', 'cc').lower()
        
        # MCP server endpoints
        self.base_url = f"http://localhost:{5100 if self.instance == 'cc' else 5101}"
        self.endpoints = {
            'query': '/rag_query',
            'query_history': '/rag_query_history', 
            'query_files': '/rag_query_files',
            'query_full': '/rag_query_full',
            'auto': '/rag_auto',
            'sources': '/rag_sources',
            'cache_stats': '/rag_cache_stats',
            'clear_cache': '/rag_clear_cache'
        }
        
        # Tool descriptions
        self.tool_descriptions = {
            'query': "🚀 Fast daily driver - Current context from memories + knowledge graph + notes",
            'query_history': "📜 Timeline explorer - Includes historical JSON data for evolution patterns", 
            'query_files': "🔍 Code hunter - Search Federation files and technical documentation",
            'query_full': "🧠 Deep research - Comprehensive search across all 6 sources",
            'auto': "🤖 Smart auto-routing - Automatically detects intent and uses best tool"
        }
        
        # Cache for results
        self.cache = {}
        self.cache_ttl = {
            'query': 300,      # 5 minutes
            'query_history': 3600,  # 1 hour
            'query_files': 1800,    # 30 minutes
            'query_full': 900,      # 15 minutes
            'auto': 600            # 10 minutes
        }
    
    def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make request to MCP server"""
        url = f"{self.base_url}{endpoint}"
        print(f"DEBUG: Making request to {url}")
        try:
            response = requests.post(
                url,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            print(f"DEBUG: Got response with {result.get('contexts_found', 0)} contexts")
            return result
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Request failed: {e}")
            return {
                'error': str(e),
                'answer': f"RAG service unavailable: {str(e)}\nURL: {url}",
                'contexts_found': 0,
                'sources_searched': [],
                'tool_used': endpoint
            }
    
    def _get_cache_key(self, tool: str, query: str) -> str:
        """Generate cache key"""
        return f"{tool}:{hashlib.md5(query.encode()).hexdigest()}"
    
    def _is_cache_valid(self, cache_key: str, ttl: int) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time, _ = self.cache[cache_key]
        return (time.time() - cached_time) < ttl
    
    def query(self, query: str, tool: str = 'auto', force_refresh: bool = False) -> Dict:
        """Execute RAG query with specified tool"""
        # Check cache unless force refresh
        cache_key = self._get_cache_key(tool, query)
        if not force_refresh and self._is_cache_valid(cache_key, self.cache_ttl.get(tool, 600)):
            _, cached_result = self.cache[cache_key]
            cached_result['from_cache'] = True
            return cached_result
        
        # Determine endpoint
        endpoint = self.endpoints.get(tool, self.endpoints['auto'])
        
        # Make request
        result = self._make_request(endpoint, {'query': query})
        
        # Cache result if successful
        if 'error' not in result:
            self.cache[cache_key] = (time.time(), result)
        
        return result
    
    def get_sources(self) -> Dict:
        """Get available RAG sources"""
        return self._make_request(self.endpoints['sources'], {})
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return self._make_request(self.endpoints['cache_stats'], {})
    
    def clear_cache(self, cache_type: Optional[str] = None) -> Dict:
        """Clear RAG cache"""
        data = {'cache_type': cache_type} if cache_type else {}
        return self._make_request(self.endpoints['clear_cache'], data)


class RAGSearchPanel(ttk.Frame):
    """Dedicated panel for RAG search with all V2 tools"""
    
    def __init__(self, parent, memory_callback=None):
        super().__init__(parent)
        self.memory_callback = memory_callback
        self.rag_client = FederationRAGClient()
        self.current_results = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the RAG search panel UI"""
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        title_label = ttk.Label(
            title_frame,
            text="🚀 Federation RAG V2 Search",
            font=('Helvetica', 20, 'bold')
        )
        title_label.pack(side='left')
        
        # Status label
        self.status_label = ttk.Label(
            title_frame,
            text="Ready",
            font=('Helvetica', 12),
            foreground='gray'
        )
        self.status_label.pack(side='right')
        
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
            text="🔄 Refresh",
            command=lambda: self.execute_search(force_refresh=True)
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
    
    def on_tool_change(self, tool):
        """Update tool description when selection changes"""
        self.tool_desc_var.set(self.rag_client.tool_descriptions.get(tool, ""))
    
    def execute_search(self, force_refresh=False):
        """Execute RAG search with selected tool"""
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
        
        # Run search in background
        def search():
            result = self.rag_client.query(query, tool, force_refresh)
            self.after(0, lambda: self.display_results(result))
        
        threading.Thread(target=search, daemon=True).start()
    
    def display_results(self, result: Dict):
        """Display RAG search results"""
        if 'error' in result:
            self.status_label.config(text="Error", foreground='red')
            self.synthesis_text.insert(1.0, f"Error: {result['error']}")
            return
        
        # Update status
        contexts = result.get('contexts_found', 0)
        tool_used = result.get('tool_used', 'unknown')
        cached = " (cached)" if result.get('from_cache') else ""
        self.status_label.config(
            text=f"Found {contexts} contexts using {tool_used}{cached}",
            foreground='green'
        )
        
        # Display synthesis
        answer = result.get('answer', 'No answer provided')
        self.synthesis_text.insert(1.0, answer)
        
        # Display contexts
        self.display_contexts(result)
        
        # Display stats
        self.display_stats(result)
        
        # Store results for potential memory browser integration
        self.current_results = result.get('source_metadata', [])
    
    def display_contexts(self, result: Dict):
        """Display source contexts"""
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
        stats = result.get('retrieval_stats', {})
        
        self.stats_text.insert(tk.END, "SEARCH STATISTICS\n")
        self.stats_text.insert(tk.END, "="*40 + "\n\n")
        
        # Tool and timing
        tool = result.get('tool_used', 'unknown')
        cache_ttl = result.get('cache_ttl', 'unknown')
        self.stats_text.insert(tk.END, f"Tool Used: {tool}\n")
        self.stats_text.insert(tk.END, f"Cache TTL: {cache_ttl}\n")
        self.stats_text.insert(tk.END, f"From Cache: {'Yes' if result.get('from_cache') else 'No'}\n\n")
        
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


class MemoryBrowserRAGV2(MemoryBrowserV5):
    """ChromaDB Memory Browser with Federation RAG V2"""
    
    def __init__(self, root):
        # Initialize parent
        super().__init__(root)
        
        # Update window title
        self.root.title("Federation Memory Browser - RAG V2 ENHANCED")
        
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
            rag_window.title("Federation RAG V2 Search")
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
        # Implementation depends on the specific metadata structure
        memory_id = result_metadata.get('id') or result_metadata.get('memory_id')
        if memory_id:
            # Find and display the memory
            for memory in self.all_memories:
                if memory.get('id') == memory_id:
                    self.show_memory_detail(memory)
                    break


def main():
    root = tk.Tk()
    app = MemoryBrowserRAGV2(root)
    root.mainloop()

if __name__ == "__main__":
    main()