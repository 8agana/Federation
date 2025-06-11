#!/usr/bin/env python3
"""
Minimal Memory Viewer - Super simple GUI that won't hang
Just search and view, no fancy features
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import chromadb
import threading

class MinimalMemoryViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Federation Memory Viewer - Minimal")
        self.root.geometry("1000x700")
        
        # Load collections
        base_path = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs"
        self.collections = {}
        
        try:
            cc_client = chromadb.PersistentClient(path=f"{base_path}/cc-federation")
            self.collections['cc'] = cc_client.get_collection("cc_memories")
            cc_count = self.collections['cc'].count()
        except:
            cc_count = 0
            
        try:
            dt_client = chromadb.PersistentClient(path=f"{base_path}/dt-federation")
            self.collections['dt'] = dt_client.get_collection("dt_memories")
            dt_count = self.collections['dt'].count()
        except:
            dt_count = 0
        
        # Simple UI
        self.setup_ui(cc_count, dt_count)
        
    def setup_ui(self, cc_count, dt_count):
        # Top frame - search
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text=f"CC: {cc_count} | DT: {dt_count}", 
                 font=('Helvetica', 12)).pack(side=tk.LEFT)
        
        ttk.Label(top_frame, text="Search:", font=('Helvetica', 14)).pack(side=tk.LEFT, padx=(20, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=40, font=('Helvetica', 14))
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<Return>', lambda e: self.search())
        
        ttk.Button(top_frame, text="Search", command=self.search).pack(side=tk.LEFT)
        
        # Collection selection
        self.collection_var = tk.StringVar(value='all')
        ttk.Radiobutton(top_frame, text="All", variable=self.collection_var, value='all').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(top_frame, text="CC", variable=self.collection_var, value='cc').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(top_frame, text="DT", variable=self.collection_var, value='dt').pack(side=tk.LEFT, padx=5)
        
        # Results list
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=('Helvetica', 12))
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_listbox.yview)
        
        self.results_listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # Content display
        content_frame = ttk.LabelFrame(self.root, text="Memory Content", padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, height=15, font=('Helvetica', 12))
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # Status
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Store results
        self.current_results = []
    
    def search(self):
        query = self.search_var.get().strip()
        if not query:
            self.status_label.config(text="Please enter a search query")
            return
        
        self.status_label.config(text="Searching...")
        self.results_listbox.delete(0, tk.END)
        self.content_text.delete(1.0, tk.END)
        
        # Run search in thread
        def do_search():
            results = []
            collection = self.collection_var.get()
            
            collections_to_search = []
            if collection == 'all':
                collections_to_search = list(self.collections.items())
            elif collection in self.collections and self.collections[collection]:
                collections_to_search = [(collection, self.collections[collection])]
            
            for name, coll in collections_to_search:
                try:
                    res = coll.query(
                        query_texts=[query],
                        n_results=20
                    )
                    
                    for i in range(len(res['ids'][0])):
                        results.append({
                            'id': res['ids'][0][i],
                            'content': res['documents'][0][i],
                            'metadata': res['metadatas'][0][i] if res['metadatas'] else {},
                            'distance': res['distances'][0][i] if res['distances'] else None,
                            'collection': name
                        })
                except Exception as e:
                    print(f"Search error in {name}: {e}")
            
            # Sort by relevance
            results.sort(key=lambda x: x.get('distance', 999))
            
            # Update UI in main thread
            self.root.after(0, lambda: self.display_results(results))
        
        threading.Thread(target=do_search, daemon=True).start()
    
    def display_results(self, results):
        self.current_results = results
        self.results_listbox.delete(0, tk.END)
        
        if results:
            for i, res in enumerate(results):
                title = res['metadata'].get('title', res['id'])
                preview = res['content'][:60] + "..." if len(res['content']) > 60 else res['content']
                display = f"[{res['collection'].upper()}] {title} - {preview}"
                self.results_listbox.insert(tk.END, display)
            
            self.status_label.config(text=f"Found {len(results)} results")
        else:
            self.status_label.config(text="No results found")
    
    def on_select(self, event):
        selection = self.results_listbox.curselection()
        if selection and self.current_results:
            idx = selection[0]
            if idx < len(self.current_results):
                memory = self.current_results[idx]
                self.display_memory(memory)
    
    def display_memory(self, memory):
        self.content_text.delete(1.0, tk.END)
        
        # Header info
        self.content_text.insert(tk.END, f"ID: {memory['id']}\n", 'bold')
        self.content_text.insert(tk.END, f"Collection: {memory['collection'].upper()}\n\n", 'bold')
        
        # Metadata
        metadata = memory.get('metadata', {})
        if metadata:
            self.content_text.insert(tk.END, "Metadata:\n", 'bold')
            for key, value in metadata.items():
                self.content_text.insert(tk.END, f"  {key}: {value}\n")
            self.content_text.insert(tk.END, "\n")
        
        # Content
        self.content_text.insert(tk.END, "Content:\n", 'bold')
        self.content_text.insert(tk.END, memory['content'])
        
        # Configure tags
        self.content_text.tag_config('bold', font=('Helvetica', 12, 'bold'))

def main():
    root = tk.Tk()
    app = MinimalMemoryViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()