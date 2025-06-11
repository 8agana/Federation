#!/usr/bin/env python3
"""
Federation RAG V2 Search - Standalone App
All 5 specialized RAG tools in a dedicated interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import threading
import time
from typing import Dict, Optional
import json

# Set GROQ API key
os.environ['GROQ_API_KEY'] = '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'

# Add Federation RAG to path
sys.path.append('/Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/federation_rag')

# Import RAG V2
try:
    from cc_federation_rag_v2 import CCFederationRAGv2
    RAG_AVAILABLE = True
except Exception as e:
    print(f"Error importing RAG: {e}")
    RAG_AVAILABLE = False


class RAGSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Federation RAG V2 Search")
        self.root.geometry("1200x800")
        
        # Set style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Initialize RAG
        self.rag = None
        self.init_rag()
        
        # Tool descriptions
        self.tool_descriptions = {
            'query_daily': "🚀 Fast daily driver - Current context from memories + knowledge graph + notes",
            'query_history': "📜 Timeline explorer - Includes historical JSON data for evolution patterns", 
            'query_files': "🔍 Code hunter - Search Federation files and technical documentation",
            'query_full': "🧠 Deep research - Comprehensive search across all 6 sources",
            'query_auto': "🤖 Smart auto-routing - Automatically detects intent and uses best tool"
        }
        
        # Build UI
        self.setup_ui()
        
    def init_rag(self):
        """Initialize RAG engine"""
        if not RAG_AVAILABLE:
            return
            
        try:
            self.rag = CCFederationRAGv2()
            self.rag_status = "Ready"
        except Exception as e:
            print(f"RAG initialization error: {e}")
            self.rag = None
            self.rag_status = f"Error: {str(e)}"
    
    def setup_ui(self):
        """Setup the main UI"""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = ttk.Label(
            header_frame,
            text="🚀 Federation RAG V2 Search",
            font=('Helvetica', 24, 'bold')
        )
        title_label.pack(side='left')
        
        self.status_label = ttk.Label(
            header_frame,
            text=self.rag_status if self.rag else "RAG Unavailable",
            font=('Helvetica', 14),
            foreground='green' if self.rag else 'red'
        )
        self.status_label.pack(side='right')
        
        # Search section
        search_frame = ttk.LabelFrame(self.root, text="Search Query", padding=15)
        search_frame.pack(fill='x', padx=20, pady=10)
        
        # Query entry
        query_frame = ttk.Frame(search_frame)
        query_frame.pack(fill='x', pady=(0, 10))
        
        self.query_var = tk.StringVar()
        query_entry = ttk.Entry(
            query_frame,
            textvariable=self.query_var,
            font=('Helvetica', 16)
        )
        query_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        query_entry.bind('<Return>', lambda e: self.execute_search())
        
        ttk.Button(
            query_frame,
            text="🔍 Search",
            command=self.execute_search,
            style='Accent.TButton'
        ).pack(side='left')
        
        # Tool selection
        tool_frame = ttk.Frame(search_frame)
        tool_frame.pack(fill='x')
        
        ttk.Label(tool_frame, text="Tool:", font=('Helvetica', 14)).pack(side='left', padx=(0, 10))
        
        self.tool_var = tk.StringVar(value='query_auto')
        tool_combo = ttk.Combobox(
            tool_frame,
            textvariable=self.tool_var,
            values=['query_auto', 'query_daily', 'query_history', 'query_files', 'query_full'],
            state='readonly',
            font=('Helvetica', 14),
            width=20
        )
        tool_combo.pack(side='left', padx=(0, 20))
        tool_combo.bind('<<ComboboxSelected>>', self.on_tool_change)
        
        # Tool description
        self.tool_desc_label = ttk.Label(
            tool_frame,
            text=self.tool_descriptions['query_auto'],
            font=('Helvetica', 12),
            foreground='#555'
        )
        self.tool_desc_label.pack(side='left')
        
        # Results section
        results_frame = ttk.Frame(self.root)
        results_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))
        
        # Notebook for results
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Synthesis tab
        synthesis_frame = ttk.Frame(self.notebook)
        self.notebook.add(synthesis_frame, text='🤖 Answer')
        
        self.synthesis_text = scrolledtext.ScrolledText(
            synthesis_frame,
            wrap=tk.WORD,
            font=('Helvetica', 14),
            height=20
        )
        self.synthesis_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Context tab
        context_frame = ttk.Frame(self.notebook)
        self.notebook.add(context_frame, text='📚 Sources')
        
        self.context_text = scrolledtext.ScrolledText(
            context_frame,
            wrap=tk.WORD,
            font=('Courier', 12),
            height=20
        )
        self.context_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Stats tab
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text='📊 Stats')
        
        self.stats_text = scrolledtext.ScrolledText(
            stats_frame,
            wrap=tk.WORD,
            font=('Courier', 12),
            height=20
        )
        self.stats_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Control buttons
        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(
            controls_frame,
            text="📋 Copy Answer",
            command=self.copy_answer
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            controls_frame,
            text="💾 Save Results",
            command=self.save_results
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            controls_frame,
            text="🗑️ Clear",
            command=self.clear_results
        ).pack(side='left', padx=(0, 10))
        
        ttk.Button(
            controls_frame,
            text="ℹ️ About",
            command=self.show_about
        ).pack(side='right')
    
    def on_tool_change(self, event=None):
        """Update tool description"""
        tool = self.tool_var.get()
        self.tool_desc_label.config(text=self.tool_descriptions.get(tool, ""))
    
    def execute_search(self):
        """Execute RAG search"""
        if not self.rag:
            messagebox.showerror("Error", "RAG is not available")
            return
            
        query = self.query_var.get().strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a search query")
            return
        
        # Clear previous results
        self.clear_results()
        
        # Update status
        self.status_label.config(text="Searching...", foreground='blue')
        tool = self.tool_var.get()
        
        # Show searching message
        self.synthesis_text.insert('1.0', f"Searching with {tool}...")
        self.notebook.select(0)
        
        # Run search in background
        def search():
            try:
                # Get the method
                method = getattr(self.rag, tool)
                # Pass query as string, not dict
                result = method(query)
                
                # Update UI in main thread
                self.root.after(0, lambda: self.display_results(result))
            except Exception as e:
                error_result = {
                    'error': str(e),
                    'answer': f"Error: {str(e)}",
                    'contexts_found': 0,
                    'tool_used': tool
                }
                self.root.after(0, lambda: self.display_results(error_result))
        
        threading.Thread(target=search, daemon=True).start()
    
    def display_results(self, result: Dict):
        """Display search results"""
        # Clear previous
        self.synthesis_text.delete('1.0', tk.END)
        self.context_text.delete('1.0', tk.END)
        self.stats_text.delete('1.0', tk.END)
        
        if 'error' in result:
            self.status_label.config(text="Error", foreground='red')
            self.synthesis_text.insert('1.0', f"Error: {result['error']}")
            return
        
        # Update status
        contexts = result.get('contexts_found', 0)
        tool = result.get('tool_used', 'unknown')
        self.status_label.config(
            text=f"Found {contexts} contexts using {tool}",
            foreground='green'
        )
        
        # Display answer
        answer = result.get('answer', 'No answer provided')
        self.synthesis_text.insert('1.0', answer)
        
        # Display contexts
        self.display_contexts(result)
        
        # Display stats
        self.display_stats(result)
        
        # Store result for saving
        self.last_result = result
    
    def display_contexts(self, result: Dict):
        """Display source contexts"""
        contexts = result.get('source_metadata', [])
        if not contexts:
            self.context_text.insert('1.0', "No source contexts available")
            return
        
        # Group by source
        by_source = {}
        for ctx in contexts:
            source = ctx.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(ctx)
        
        # Display
        for source, items in by_source.items():
            self.context_text.insert(tk.END, f"\n{'='*60}\n")
            self.context_text.insert(tk.END, f"SOURCE: {source.upper()} ({len(items)} items)\n")
            self.context_text.insert(tk.END, f"{'='*60}\n\n")
            
            for i, item in enumerate(items, 1):
                metadata = item.get('metadata', {})
                
                if source == 'federation_files':
                    title = metadata.get('filename', 'Unknown')
                    info = metadata.get('rel_path', 'Unknown path')
                else:
                    title = metadata.get('title', f"Item {i}")
                    info = f"Created: {metadata.get('created_at', 'Unknown')}"
                
                self.context_text.insert(tk.END, f"{i}. {title}\n")
                self.context_text.insert(tk.END, f"   {info}\n\n")
    
    def display_stats(self, result: Dict):
        """Display statistics"""
        stats = result.get('retrieval_stats', {})
        
        self.stats_text.insert(tk.END, "SEARCH STATISTICS\n")
        self.stats_text.insert(tk.END, "="*40 + "\n\n")
        
        # General info
        self.stats_text.insert(tk.END, f"Tool: {result.get('tool_used', 'unknown')}\n")
        self.stats_text.insert(tk.END, f"Total Contexts: {result.get('contexts_found', 0)}\n")
        self.stats_text.insert(tk.END, f"Cache TTL: {result.get('cache_ttl', 'unknown')}\n\n")
        
        # Sources
        sources = result.get('sources_searched', [])
        self.stats_text.insert(tk.END, f"Sources Searched ({len(sources)}):\n")
        for source in sources:
            self.stats_text.insert(tk.END, f"  • {source}\n")
        
        # Performance
        self.stats_text.insert(tk.END, "\nRetrieval Performance:\n")
        total_time = 0
        for source, data in stats.items():
            count = data.get('count', 0)
            time_ms = data.get('time', 0) * 1000
            total_time += time_ms
            self.stats_text.insert(tk.END, f"  {source}: {count} items in {time_ms:.1f}ms\n")
        
        self.stats_text.insert(tk.END, f"\nTotal Time: {total_time:.1f}ms\n")
    
    def copy_answer(self):
        """Copy answer to clipboard"""
        answer = self.synthesis_text.get('1.0', tk.END).strip()
        if answer:
            self.root.clipboard_clear()
            self.root.clipboard_append(answer)
            self.status_label.config(text="Copied to clipboard!", foreground='green')
            self.root.after(2000, lambda: self.status_label.config(text="Ready", foreground='green'))
    
    def save_results(self):
        """Save results to file"""
        if not hasattr(self, 'last_result'):
            messagebox.showwarning("No Results", "No results to save")
            return
        
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(self.last_result, f, indent=2)
                else:
                    with open(filename, 'w') as f:
                        f.write(f"Query: {self.query_var.get()}\n")
                        f.write(f"Tool: {self.tool_var.get()}\n")
                        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("="*60 + "\n\n")
                        f.write("ANSWER:\n")
                        f.write(self.synthesis_text.get('1.0', tk.END))
                        f.write("\n\nSOURCES:\n")
                        f.write(self.context_text.get('1.0', tk.END))
                
                messagebox.showinfo("Saved", f"Results saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
    
    def clear_results(self):
        """Clear all results"""
        self.synthesis_text.delete('1.0', tk.END)
        self.context_text.delete('1.0', tk.END)
        self.stats_text.delete('1.0', tk.END)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Federation RAG V2 Search

A powerful search interface for the Federation knowledge system.

Features:
• 5 specialized search tools
• Smart auto-routing
• Natural language processing
• Multi-source retrieval
• LLM-powered synthesis

Sources:
• CC & DT Memories
• Knowledge Graph
• Obsidian Notes
• Federation Files
• Legacy JSON Archives

Version: 2.0
Part of the Federation AI System"""
        
        messagebox.showinfo("About", about_text)


def main():
    root = tk.Tk()
    app = RAGSearchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()