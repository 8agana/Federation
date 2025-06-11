#!/usr/bin/env python3
"""Simple Memory Browser - Basic GUI to verify memory loading"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import chromadb

class SimpleMemoryBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Memory Browser")
        self.root.geometry("800x600")
        
        # ChromaDB setup
        base_path = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs"
        self.collections = {}
        
        try:
            cc_client = chromadb.PersistentClient(path=f"{base_path}/cc-federation")
            self.collections['cc'] = cc_client.get_collection("cc_memories")
            print(f"Loaded CC: {self.collections['cc'].count()} memories")
        except Exception as e:
            print(f"CC Error: {e}")
            
        try:
            dt_client = chromadb.PersistentClient(path=f"{base_path}/dt-federation")
            self.collections['dt'] = dt_client.get_collection("dt_memories")
            print(f"Loaded DT: {self.collections['dt'].count()} memories")
        except Exception as e:
            print(f"DT Error: {e}")
        
        # UI
        self.setup_ui()
        self.load_memories()
    
    def setup_ui(self):
        # List
        list_frame = ttk.Frame(self.root)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.memory_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.memory_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.memory_list.yview)
        
        self.memory_list.bind('<<ListboxSelect>>', self.on_select)
        
        # Details
        self.details_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50)
        self.details_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status
        self.status_label = ttk.Label(self.root, text="Loading...")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_memories(self):
        self.memories = []
        
        for name, collection in self.collections.items():
            if collection:
                try:
                    results = collection.get(limit=100)
                    for i in range(len(results['ids'])):
                        self.memories.append({
                            'id': results['ids'][i],
                            'content': results['documents'][i],
                            'metadata': results['metadatas'][i] or {},
                            'collection': name
                        })
                        # Add to list
                        title = results['metadatas'][i].get('title', results['ids'][i])
                        self.memory_list.insert(tk.END, f"[{name.upper()}] {title}")
                except Exception as e:
                    print(f"Error loading {name}: {e}")
        
        self.status_label.config(text=f"Loaded {len(self.memories)} memories")
    
    def on_select(self, event):
        selection = self.memory_list.curselection()
        if selection:
            idx = selection[0]
            memory = self.memories[idx]
            
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, f"ID: {memory['id']}\n")
            self.details_text.insert(tk.END, f"Collection: {memory['collection']}\n")
            self.details_text.insert(tk.END, f"Metadata: {memory['metadata']}\n")
            self.details_text.insert(tk.END, f"\nContent:\n{memory['content']}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleMemoryBrowser(root)
    root.mainloop()