#!/usr/bin/env python3
"""
ChromaDB Memory Browser - Bigger Text Version
Based on v5 with increased font sizes for better readability
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

# v5 Schema domains and categories
V5_DOMAINS = ["identity", "technical", "session", "personal", "relationship", "operational", "creative", "historical"]
V5_CATEGORIES = ["core", "protocol", "solution", "context", "learning", "discovery", "guide", "analysis", "handoff"]

class MemoryBrowserV5:
    def __init__(self, root):
        self.root = root
        self.root.title("Federation Memory Browser v5 - BIGGER TEXT")
        self.root.geometry("1900x1200")  # Larger window
        
        # Make window resizable
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Initialize ChromaDB clients
        self.init_chromadb()
        
        # Current state
        self.selected_collection = "all"
        self.all_memories = []
        self.filtered_memories = []
        self.current_memory = None
        
        # Pagination
        self.page_size = 100
        self.current_page = 0
        self.total_pages = 0
        
        # Sorting
        self.sort_column = "Date"
        self.sort_reverse = True
        
        # Memory cache for performance
        self.memory_cache = {}
        self.cache_size = 500
        self.cache_queue = deque(maxlen=self.cache_size)
        
        # v5 filter states
        self.priority_filter = tk.StringVar(value="all")
        self.domain_filter = tk.StringVar(value="all")
        self.essential_only = tk.BooleanVar(value=False)
        self.needs_review_only = tk.BooleanVar(value=False)
        
        # Create UI
        self.create_widgets()
        
        # Configure styles for font sizes
        self.configure_styles()
        
        # Load initial memories
        self.load_memories()
    
    def init_chromadb(self):
        """Initialize ChromaDB connections"""
        base_path = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs"
        
        self.clients = {}
        self.collections = {}
        
        # CC Federation Database
        try:
            self.clients['cc'] = chromadb.PersistentClient(
                path=f"{base_path}/cc-federation"
            )
            # Use the correct collection name
            self.collections['cc'] = self.clients['cc'].get_collection("cc_memories")
            print(f"✓ Loaded CC Federation collection with {self.collections['cc'].count()} memories")
        except Exception as e:
            print(f"✗ Could not load CC Federation collection: {e}")
        
        # DT Federation Database
        try:
            self.clients['dt'] = chromadb.PersistentClient(
                path=f"{base_path}/dt-federation"
            )
            self.collections['dt'] = self.clients['dt'].get_collection("dt_memories")
            print(f"✓ Loaded DT Federation collection with {self.collections['dt'].count()} memories")
        except Exception as e:
            print(f"✗ Could not load DT Federation collection: {e}")
        
    
    def configure_styles(self):
        """Configure ttk styles for MUCH larger fonts"""
        style = ttk.Style()
        
        # Configure fonts - BIGGER SIZES
        default_font = ('Helvetica', 18)  # Increased from 12
        heading_font = ('Helvetica', 22, 'bold')  # Increased from 14
        tree_font = ('Helvetica', 16)  # For tree views
        
        # Configure styles
        style.configure('Heading.TLabel', font=heading_font)
        style.configure('TLabel', font=default_font)
        style.configure('TButton', font=default_font)
        style.configure('Treeview', font=tree_font, rowheight=40)  # Increased row height
        style.configure('Treeview.Heading', font=heading_font)
        style.configure('TCheckbutton', font=default_font)
        style.configure('TCombobox', font=default_font)
        style.configure('TEntry', font=default_font)
    
    def create_widgets(self):
        """Create the main UI with v5 enhancements"""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.rowconfigure(1, weight=1)
        main_container.columnconfigure(0, weight=1)
        
        # Top toolbar with v5 controls
        self.create_toolbar(main_container)
        
        # Main content area
        content_frame = ttk.Frame(main_container)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=0)
        content_frame.columnconfigure(2, weight=2)
        
        # Left panel - Collections and filters
        self.create_left_panel(content_frame)
        
        # Center panel - Memory list
        self.create_center_panel(content_frame)
        
        # Right panel - Memory details
        self.create_right_panel(content_frame)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_toolbar(self, parent):
        """Create toolbar with v5 features"""
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Search box
        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_memories())
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=25, font=('Helvetica', 18))
        search_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # v5 Filter Controls
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
        
        # Priority filter
        ttk.Label(toolbar, text="Priority:").pack(side=tk.LEFT, padx=(0, 5))
        priority_combo = ttk.Combobox(toolbar, textvariable=self.priority_filter, width=12, 
                                     values=["all", "3-Core", "2-Important", "1-Useful", "0-Archive"],
                                     state="readonly", font=('Helvetica', 16))
        priority_combo.pack(side=tk.LEFT, padx=(0, 10))
        priority_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_memories())
        
        # Domain filter
        ttk.Label(toolbar, text="Domain:").pack(side=tk.LEFT, padx=(0, 5))
        domain_values = ["all"] + V5_DOMAINS
        domain_combo = ttk.Combobox(toolbar, textvariable=self.domain_filter, width=14,
                                   values=domain_values, state="readonly", font=('Helvetica', 16))
        domain_combo.pack(side=tk.LEFT, padx=(0, 10))
        domain_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_memories())
        
        # Boolean filters
        essential_check = ttk.Checkbutton(toolbar, text="Essential Only", 
                                         variable=self.essential_only,
                                         command=self.filter_memories)
        essential_check.pack(side=tk.LEFT, padx=(0, 10))
        
        review_check = ttk.Checkbutton(toolbar, text="Needs Review", 
                                      variable=self.needs_review_only,
                                      command=self.filter_memories)
        review_check.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
        
        # Action buttons
        ttk.Button(toolbar, text="➕ New", 
                  command=self.create_memory_dialog).pack(side=tk.LEFT, padx=5)
        
        self.update_btn = ttk.Button(toolbar, text="✏️ Update", 
                                    command=self.update_memory_dialog, state='disabled')
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(toolbar, text="🗑️ Delete", 
                                    command=self.delete_memory, state='disabled')
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(toolbar, text="🔄 Refresh", 
                  command=self.refresh_all).pack(side=tk.LEFT, padx=5)
    
    def create_left_panel(self, parent):
        """Create left panel with collections tree"""
        left_frame = ttk.Frame(parent, width=300)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.rowconfigure(0, weight=1)
        
        # Collections tree
        tree_frame = ttk.LabelFrame(left_frame, text="Collections", padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.collections_tree = ttk.Treeview(tree_frame, selectmode='browse', height=20)
        self.collections_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add collections
        self.collections_tree.insert('', 'end', 'all', text='📚 All Memories')
        
        fed_node = self.collections_tree.insert('', 'end', 'federation', text='Federation')
        self.collections_tree.insert(fed_node, 'end', 'cc', text='🧠 CC Memories')
        self.collections_tree.insert(fed_node, 'end', 'dt', text='🖥️ DT Memories')
        
        # Add v5 smart folders
        smart_node = self.collections_tree.insert('', 'end', 'smart', text='Smart Folders')
        self.collections_tree.insert(smart_node, 'end', 'living', text='🌱 Living Memories')
        self.collections_tree.insert(smart_node, 'end', 'core', text='⭐ Core (Priority 3)')
        self.collections_tree.insert(smart_node, 'end', 'review', text='🔍 Needs Review')
        self.collections_tree.insert(smart_node, 'end', 'recent', text='🕐 Recent (24h)')
        
        # Expand all
        self.collections_tree.item('federation', open=True)
        self.collections_tree.item('smart', open=True)
        
        # Bind selection
        self.collections_tree.bind('<<TreeviewSelect>>', self.on_collection_select)
        
        # Select "All" by default
        self.collections_tree.selection_set('all')
    
    def create_center_panel(self, parent):
        """Create center panel with memory list"""
        center_frame = ttk.Frame(parent)
        center_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        center_frame.rowconfigure(0, weight=1)
        center_frame.columnconfigure(0, weight=1)
        
        # Memory list with v5 columns
        list_frame = ttk.LabelFrame(center_frame, text="Memories", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with scrollbar
        tree_scroll = ttk.Scrollbar(list_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.memory_tree = ttk.Treeview(list_frame, yscrollcommand=tree_scroll.set, selectmode='browse')
        tree_scroll.config(command=self.memory_tree.yview)
        
        # Define columns for v5 metadata
        self.memory_tree['columns'] = ('Date', 'Title', 'Domain', 'Priority', 'Flags', 'Version', 'Collection')
        
        # Format columns
        self.memory_tree.column("#0", width=0, stretch=tk.NO)
        self.memory_tree.column("Date", width=140, minwidth=120)
        self.memory_tree.column("Title", width=320, minwidth=250)
        self.memory_tree.column("Domain", width=120, minwidth=100)
        self.memory_tree.column("Priority", width=90, minwidth=80)
        self.memory_tree.column("Flags", width=120, minwidth=100)
        self.memory_tree.column("Version", width=70, minwidth=60)
        self.memory_tree.column("Collection", width=100, minwidth=80)
        
        # Create headings
        self.memory_tree.heading("#0", text="", anchor=tk.W)
        self.memory_tree.heading("Date", text="Date", anchor=tk.W, command=lambda: self.sort_by_column("Date"))
        self.memory_tree.heading("Title", text="Title", anchor=tk.W, command=lambda: self.sort_by_column("Title"))
        self.memory_tree.heading("Domain", text="Domain", anchor=tk.W, command=lambda: self.sort_by_column("Domain"))
        self.memory_tree.heading("Priority", text="Priority", anchor=tk.CENTER, command=lambda: self.sort_by_column("Priority"))
        self.memory_tree.heading("Flags", text="Flags", anchor=tk.CENTER)
        self.memory_tree.heading("Version", text="Ver", anchor=tk.CENTER, command=lambda: self.sort_by_column("Version"))
        self.memory_tree.heading("Collection", text="Source", anchor=tk.W, command=lambda: self.sort_by_column("Collection"))
        
        # Configure row colors for priorities
        self.memory_tree.tag_configure('priority3', background='#4a1f1f', foreground='#ffffff')  # Dark red for core
        self.memory_tree.tag_configure('priority2', background='#4a3319', foreground='#ffffff')  # Dark orange for important
        self.memory_tree.tag_configure('priority1', background='#1f334a', foreground='#ffffff')  # Dark blue for useful
        self.memory_tree.tag_configure('priority0', background='#2d2d2d', foreground='#cccccc')  # Dark grey for archive
        
        self.memory_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection
        self.memory_tree.bind('<<TreeviewSelect>>', self.on_memory_select)
        
        # Pagination controls
        page_frame = ttk.Frame(center_frame)
        page_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.prev_btn = ttk.Button(page_frame, text="← Previous", command=self.prev_page, state='disabled')
        self.prev_btn.pack(side=tk.LEFT)
        
        self.page_label = ttk.Label(page_frame, text="Page 1 of 1")
        self.page_label.pack(side=tk.LEFT, padx=20)
        
        self.next_btn = ttk.Button(page_frame, text="Next →", command=self.next_page, state='disabled')
        self.next_btn.pack(side=tk.LEFT)
    
    def create_right_panel(self, parent):
        """Create right panel with memory details and v5 metadata"""
        right_frame = ttk.Frame(parent)
        right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        
        # Details frame
        details_frame = ttk.LabelFrame(right_frame, text="Memory Details", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for organized display
        self.details_notebook = ttk.Notebook(details_frame)
        self.details_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Content tab
        content_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(content_frame, text="Content")
        
        # Use MUCH larger font for content
        self.content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, 
                                                     font=('Helvetica', 20), height=18)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # v5 Metadata tab
        metadata_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(metadata_frame, text="v5 Metadata")
        
        # Metadata display with grid layout
        self.metadata_frame = ttk.Frame(metadata_frame)
        self.metadata_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Raw JSON tab
        json_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(json_frame, text="Raw JSON")
        
        self.json_text = scrolledtext.ScrolledText(json_frame, wrap=tk.WORD, 
                                                   font=('Courier', 18), height=18)
        self.json_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Update Memory", 
                  command=self.update_memory_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy ID", 
                  command=self.copy_memory_id).pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_bar = ttk.Label(parent, text="Ready", relief=tk.SUNKEN, font=('Helvetica', 16))
        self.status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def load_memories(self):
        """Load memories from all collections"""
        self.set_status("Loading memories...")
        self.all_memories = []
        
        # Load from each collection
        for collection_name, collection in self.collections.items():
            if collection:
                try:
                    results = collection.get(limit=5000)  # Increased limit for v5
                    
                    for i in range(len(results['ids'])):
                        memory = {
                            'id': results['ids'][i],
                            'content': results['documents'][i],
                            'metadata': results['metadatas'][i] or {},
                            'collection': collection_name
                        }
                        self.all_memories.append(memory)
                except Exception as e:
                    print(f"Error loading {collection_name}: {e}")
        
        self.set_status(f"Loaded {len(self.all_memories)} memories")
        self.filter_memories()
    
    def sort_by_column(self, column):
        """Sort memories by the selected column"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = True if column == "Date" else False
        
        self.update_memory_list()
    
    def get_memory_date(self, memory):
        """Extract the most relevant date from a memory"""
        metadata = memory.get('metadata', {})
        
        # Try different date fields in order of preference
        date_fields = ['timestamp', 'created_at', 'last_updated', 'date', 'created']
        
        for field in date_fields:
            if field in metadata and metadata[field]:
                try:
                    # Handle ISO format dates
                    if isinstance(metadata[field], str):
                        # Remove timezone info for parsing
                        date_str = metadata[field].replace('Z', '+00:00')
                        dt = datetime.fromisoformat(date_str)
                        # Make timezone-naive for consistent comparison
                        if dt.tzinfo:
                            dt = dt.replace(tzinfo=None)
                        return dt
                    elif isinstance(metadata[field], (int, float)):
                        # Unix timestamp
                        return datetime.fromtimestamp(metadata[field])
                except:
                    continue
        
        # If no date found, return a very old date
        return datetime(1970, 1, 1)
    
    def filter_memories(self):
        """Apply filters to memories with v5 support"""
        search_term = self.search_var.get().lower()
        
        # Start with selected collection
        if self.selected_collection == "all":
            filtered = self.all_memories.copy()
        elif self.selected_collection in ["cc", "dt"]:
            filtered = [m for m in self.all_memories if m['collection'] == self.selected_collection]
        elif self.selected_collection == "living":
            filtered = [m for m in self.all_memories if m['metadata'].get('memory_type') == 'living']
        elif self.selected_collection == "core":
            filtered = [m for m in self.all_memories if m['metadata'].get('priority') == 3]
        elif self.selected_collection == "review":
            filtered = [m for m in self.all_memories if m['metadata'].get('needs_review') == True]
        elif self.selected_collection == "recent":
            # Get memories from last 24 hours
            cutoff = datetime.now().timestamp() - (24 * 60 * 60)
            filtered = []
            for m in self.all_memories:
                for field in ['created_at', 'last_updated', 'timestamp']:
                    if field in m['metadata']:
                        try:
                            ts = datetime.fromisoformat(m['metadata'][field].replace('Z', '+00:00')).timestamp()
                            if ts > cutoff:
                                filtered.append(m)
                                break
                        except:
                            continue
        else:
            filtered = self.all_memories.copy()
        
        # Apply priority filter
        priority_val = self.priority_filter.get()
        if priority_val != "all":
            priority_num = int(priority_val[0])  # Extract number from "3-Core" etc
            filtered = [m for m in filtered if m['metadata'].get('priority') == priority_num]
        
        # Apply domain filter
        if self.domain_filter.get() != "all":
            filtered = [m for m in filtered if m['metadata'].get('domain') == self.domain_filter.get()]
        
        # Apply boolean filters
        if self.essential_only.get():
            filtered = [m for m in filtered if m['metadata'].get('is_essential') == True]
        
        if self.needs_review_only.get():
            filtered = [m for m in filtered if m['metadata'].get('needs_review') == True]
        
        # Apply search
        if search_term:
            search_filtered = []
            for memory in filtered:
                # Search in content
                if search_term in memory['content'].lower():
                    search_filtered.append(memory)
                    continue
                
                # Search in metadata
                metadata_str = json.dumps(memory['metadata']).lower()
                if search_term in metadata_str:
                    search_filtered.append(memory)
            
            filtered = search_filtered
        
        self.filtered_memories = filtered
        
        # Update pagination
        self.total_pages = max(1, (len(self.filtered_memories) + self.page_size - 1) // self.page_size)
        self.current_page = 0
        
        self.update_memory_list()
        self.set_status(f"Showing {len(self.filtered_memories)} memories")
    
    def update_memory_list(self):
        """Update the memory list display with v5 enhancements"""
        # Clear current items
        for item in self.memory_tree.get_children():
            self.memory_tree.delete(item)
        
        # Sort memories before display
        sorted_memories = self.filtered_memories.copy()
        
        if self.sort_column == "Date":
            sorted_memories.sort(key=lambda m: self.get_memory_date(m), reverse=self.sort_reverse)
        elif self.sort_column == "Title":
            sorted_memories.sort(key=lambda m: m['metadata'].get('title', m['content'][:50]).lower(), reverse=self.sort_reverse)
        elif self.sort_column == "Domain":
            sorted_memories.sort(key=lambda m: m['metadata'].get('domain', 'unknown'), reverse=self.sort_reverse)
        elif self.sort_column == "Priority":
            sorted_memories.sort(key=lambda m: m['metadata'].get('priority', 0), reverse=self.sort_reverse)
        elif self.sort_column == "Version":
            sorted_memories.sort(key=lambda m: m['metadata'].get('version', 1), reverse=self.sort_reverse)
        elif self.sort_column == "Collection":
            sorted_memories.sort(key=lambda m: m['collection'], reverse=self.sort_reverse)
        
        # Update filtered memories with sorted version
        self.filtered_memories = sorted_memories
        
        # Calculate page boundaries
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.filtered_memories))
        
        # Add memories for current page
        for i in range(start_idx, end_idx):
            memory = self.filtered_memories[i]
            metadata = memory['metadata']
            
            # Extract date
            date_obj = self.get_memory_date(memory)
            date_str = date_obj.strftime('%Y-%m-%d %H:%M')
            
            # Extract title
            title = metadata.get('title', '')
            if not title:
                # Try to extract from content
                content_preview = memory['content'][:100]
                title = content_preview.split('\n')[0][:50]
            
            # Domain and category
            domain = metadata.get('domain', 'unknown')
            category = metadata.get('category', '')
            domain_cat = f"{domain}/{category}" if category else domain
            
            # Priority
            priority = metadata.get('priority', 0)
            priority_str = f"{priority}"
            
            # Build flags string with emojis
            flags = []
            if metadata.get('is_essential'):
                flags.append('⭐')
            if metadata.get('needs_review'):
                flags.append('⚠️')
            if metadata.get('federation_visible'):
                flags.append('🔗')
            if metadata.get('memory_type') == 'living':
                flags.append('🔄')
            flags_str = ' '.join(flags)
            
            # Version
            version = metadata.get('version', 1)
            version_str = f"v{version}"
            
            # Collection
            collection = memory['collection'].upper()
            
            # Determine row tag based on priority
            tag = f'priority{priority}'
            
            # Insert item with date
            self.memory_tree.insert('', 'end', iid=memory['id'],
                                   values=(date_str, title, domain_cat, priority_str, flags_str, version_str, collection),
                                   tags=(tag,))
        
        # Update pagination controls
        self.page_label.config(text=f"Page {self.current_page + 1} of {self.total_pages}")
        self.prev_btn.config(state='normal' if self.current_page > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_page < self.total_pages - 1 else 'disabled')
    
    def on_collection_select(self, event):
        """Handle collection selection"""
        selection = self.collections_tree.selection()
        if selection:
            self.selected_collection = selection[0]
            self.filter_memories()
    
    def on_memory_select(self, event):
        """Handle memory selection with v5 metadata display"""
        selection = self.memory_tree.selection()
        if selection:
            memory_id = selection[0]
            
            # Find the memory
            memory = None
            for m in self.filtered_memories:
                if m['id'] == memory_id:
                    memory = m
                    break
            
            if memory:
                self.current_memory = memory
                self.update_btn.config(state='normal')
                self.delete_btn.config(state='normal')
                self.display_memory_details(memory)
    
    def display_memory_details(self, memory):
        """Display memory details with v5 metadata"""
        # Clear previous content
        self.content_text.delete('1.0', tk.END)
        self.json_text.delete('1.0', tk.END)
        
        # Clear metadata frame
        for widget in self.metadata_frame.winfo_children():
            widget.destroy()
        
        # Display content
        self.content_text.insert('1.0', memory['content'])
        
        # Display v5 metadata in organized way
        metadata = memory['metadata']
        row = 0
        
        # Define larger font for metadata display
        metadata_font = ('Helvetica', 18)
        metadata_heading_font = ('Helvetica', 20, 'bold')
        
        # Identity section
        ttk.Label(self.metadata_frame, text="Identity", font=metadata_heading_font).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        row += 1
        
        ttk.Label(self.metadata_frame, text="ID:", font=metadata_font).grid(row=row, column=0, sticky=tk.W, padx=(20, 5))
        id_label = ttk.Label(self.metadata_frame, text=memory['id'][:40] + "...", font=metadata_font)
        id_label.grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        ttk.Label(self.metadata_frame, text="Collection:", font=metadata_font).grid(row=row, column=0, sticky=tk.W, padx=(20, 5))
        ttk.Label(self.metadata_frame, text=memory['collection'].upper(), font=metadata_font).grid(row=row, column=1, sticky=tk.W)
        row += 1
        
        # v5 Schema section
        ttk.Label(self.metadata_frame, text="v5 Schema", font=metadata_heading_font).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        row += 1
        
        fields = [
            ("Domain:", metadata.get('domain', 'unknown')),
            ("Category:", metadata.get('category', 'unknown')),
            ("Priority:", metadata.get('priority', 0)),
            ("Schema Version:", metadata.get('schema_version', 'unknown')),
            ("Memory Type:", metadata.get('memory_type', 'unknown')),
            ("Confidence:", metadata.get('confidence', 'N/A')),
        ]
        
        for label, value in fields:
            ttk.Label(self.metadata_frame, text=label, font=metadata_font).grid(row=row, column=0, sticky=tk.W, padx=(20, 5))
            ttk.Label(self.metadata_frame, text=str(value), font=metadata_font).grid(row=row, column=1, sticky=tk.W)
            row += 1
        
        # Boolean flags section
        ttk.Label(self.metadata_frame, text="Flags", font=metadata_heading_font).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        row += 1
        
        flags = [
            ("Essential:", metadata.get('is_essential', False)),
            ("Mobile Sync:", metadata.get('is_mobile_sync', False)),
            ("Needs Review:", metadata.get('needs_review', False)),
            ("Private:", metadata.get('is_private', False)),
            ("Federation Visible:", metadata.get('federation_visible', False)),
        ]
        
        for label, value in flags:
            ttk.Label(self.metadata_frame, text=label, font=metadata_font).grid(row=row, column=0, sticky=tk.W, padx=(20, 5))
            flag_text = "✓" if value else "✗"
            flag_color = "green" if value else "red"
            flag_label = tk.Label(self.metadata_frame, text=flag_text, font=metadata_font, fg=flag_color)
            flag_label.grid(row=row, column=1, sticky=tk.W)
            row += 1
        
        # Version info section
        ttk.Label(self.metadata_frame, text="Version Info", font=metadata_heading_font).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        row += 1
        
        version_fields = [
            ("Version:", metadata.get('version', 1)),
            ("Created At:", metadata.get('created_at', 'Unknown')),
            ("Last Updated:", metadata.get('last_updated', 'Never')),
            ("Created By:", metadata.get('created_by', 'Unknown')),
            ("Last Comment:", metadata.get('last_comment', 'None')),
        ]
        
        for label, value in version_fields:
            ttk.Label(self.metadata_frame, text=label, font=metadata_font).grid(row=row, column=0, sticky=tk.W, padx=(20, 5))
            ttk.Label(self.metadata_frame, text=str(value), font=metadata_font).grid(row=row, column=1, sticky=tk.W)
            row += 1
        
        # Display raw JSON
        json_str = json.dumps({
            'id': memory['id'],
            'collection': memory['collection'],
            'metadata': metadata,
            'content': memory['content'][:200] + '...' if len(memory['content']) > 200 else memory['content']
        }, indent=2)
        self.json_text.insert('1.0', json_str)
    
    def create_memory_dialog(self):
        """Create new memory with v5 schema"""
        self.show_memory_dialog(mode="create")
    
    def update_memory_dialog(self):
        """Update existing memory with v5 UPDATE capability"""
        if not self.current_memory:
            messagebox.showwarning("No Selection", "Please select a memory to update")
            return
        
        self.show_memory_dialog(mode="update", memory=self.current_memory)
    
    def delete_memory(self):
        """Delete the selected memory with confirmation"""
        if not self.current_memory:
            return
        
        memory = self.current_memory
        metadata = memory.get('metadata', {})
        title = metadata.get('title', memory['content'][:50] + '...')
        
        # Confirmation dialog
        result = messagebox.askyesno(
            "Delete Memory",
            f"Are you sure you want to delete this memory?\n\n"
            f"Title: {title}\n"
            f"ID: {memory['id']}\n"
            f"Collection: {memory['collection'].upper()}\n\n"
            f"This action cannot be undone!",
            icon='warning'
        )
        
        if result:
            try:
                # Get the collection
                collection = self.collections.get(memory['collection'])
                if collection:
                    # Delete from ChromaDB
                    collection.delete(ids=[memory['id']])
                    
                    # Remove from local memory lists
                    self.all_memories = [m for m in self.all_memories if m['id'] != memory['id']]
                    self.filtered_memories = [m for m in self.filtered_memories if m['id'] != memory['id']]
                    
                    # Clear selection
                    self.current_memory = None
                    self.update_btn.config(state='disabled')
                    self.delete_btn.config(state='disabled')
                    
                    # Clear details
                    self.content_text.delete('1.0', tk.END)
                    self.json_text.delete('1.0', tk.END)
                    for widget in self.metadata_frame.winfo_children():
                        widget.destroy()
                    
                    # Refresh the list
                    self.filter_memories()
                    
                    self.set_status(f"Memory deleted successfully: {title}")
                    messagebox.showinfo("Success", "Memory deleted successfully!")
                else:
                    messagebox.showerror("Error", f"Collection '{memory['collection']}' not found")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete memory: {str(e)}")
                self.set_status(f"Error deleting memory: {str(e)}")
    
    def copy_memory_id(self):
        """Copy current memory ID to clipboard"""
        if self.current_memory:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_memory['id'])
            self.set_status(f"Copied ID: {self.current_memory['id']}")
    
    def refresh_all(self):
        """Refresh all memories"""
        self.load_memories()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_memory_list()
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_memory_list()
    
    def set_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def show_memory_dialog(self, mode="create", memory=None):
        """Show memory create/update dialog with v5 schema support"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{'Update' if mode == 'update' else 'Create'} Memory")
        dialog.geometry("900x800")
        dialog.configure(bg='#2d2d30')
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Configure large fonts
        label_font = ('Helvetica', 16)
        entry_font = ('Helvetica', 14)
        button_font = ('Helvetica', 14)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Content section
        ttk.Label(main_frame, text="Content:", font=label_font).pack(anchor=tk.W, pady=(0, 5))
        content_text = scrolledtext.ScrolledText(main_frame, height=15, font=entry_font, 
                                               bg='#3c3c3c', fg='#d4d4d4', insertbackground='#d4d4d4')
        content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Metadata frame
        meta_frame = ttk.LabelFrame(main_frame, text="v5 Metadata", padding="10")
        meta_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create metadata fields
        fields = {}
        
        # Title
        ttk.Label(meta_frame, text="Title:", font=label_font).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        fields['title'] = ttk.Entry(meta_frame, font=entry_font, width=50)
        fields['title'].grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Domain
        ttk.Label(meta_frame, text="Domain:", font=label_font).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        fields['domain'] = ttk.Combobox(meta_frame, values=V5_DOMAINS, font=entry_font, width=47)
        fields['domain'].grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Category  
        ttk.Label(meta_frame, text="Category:", font=label_font).grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        fields['category'] = ttk.Combobox(meta_frame, values=V5_CATEGORIES, font=entry_font, width=47)
        fields['category'].grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Priority
        ttk.Label(meta_frame, text="Priority:", font=label_font).grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        fields['priority'] = ttk.Combobox(meta_frame, values=['0', '1', '2', '3'], font=entry_font, width=47)
        fields['priority'].grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Tags
        ttk.Label(meta_frame, text="Tags:", font=label_font).grid(row=4, column=0, sticky=tk.W, padx=(0, 10))
        fields['tags'] = ttk.Entry(meta_frame, font=entry_font, width=50)
        fields['tags'].grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Boolean flags frame
        flags_frame = ttk.Frame(meta_frame)
        flags_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        flag_vars = {}
        flag_vars['is_essential'] = tk.BooleanVar()
        flag_vars['needs_review'] = tk.BooleanVar()
        flag_vars['is_private'] = tk.BooleanVar()
        flag_vars['federation_visible'] = tk.BooleanVar()
        
        ttk.Checkbutton(flags_frame, text="Essential", variable=flag_vars['is_essential'], 
                       style='TCheckbutton').grid(row=0, column=0, padx=10, sticky=tk.W)
        ttk.Checkbutton(flags_frame, text="Needs Review", variable=flag_vars['needs_review'],
                       style='TCheckbutton').grid(row=0, column=1, padx=10, sticky=tk.W)
        ttk.Checkbutton(flags_frame, text="Private", variable=flag_vars['is_private'],
                       style='TCheckbutton').grid(row=0, column=2, padx=10, sticky=tk.W)
        ttk.Checkbutton(flags_frame, text="Federation Visible", variable=flag_vars['federation_visible'],
                       style='TCheckbutton').grid(row=0, column=3, padx=10, sticky=tk.W)
        
        # Collection selection for create mode
        collection_var = tk.StringVar(value='cc')
        if mode == "create":
            ttk.Label(meta_frame, text="Collection:", font=label_font).grid(row=6, column=0, sticky=tk.W, padx=(0, 10))
            collection_combo = ttk.Combobox(meta_frame, textvariable=collection_var, 
                                          values=['cc', 'dt'], font=entry_font, width=47, state="readonly")
            collection_combo.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # Pre-fill fields for update mode
        if mode == "update" and memory:
            content_text.insert('1.0', memory['content'])
            metadata = memory.get('metadata', {})
            
            fields['title'].insert(0, metadata.get('title', ''))
            fields['domain'].set(metadata.get('domain', 'technical'))
            fields['category'].set(metadata.get('category', 'memory'))
            fields['priority'].set(str(metadata.get('priority', 1)))
            
            # Handle tags
            tags = metadata.get('tags', '')
            if isinstance(tags, list):
                tags = ', '.join(tags)
            fields['tags'].insert(0, str(tags))
            
            # Set boolean flags
            flag_vars['is_essential'].set(metadata.get('is_essential', False))
            flag_vars['needs_review'].set(metadata.get('needs_review', False))
            flag_vars['is_private'].set(metadata.get('is_private', False))
            flag_vars['federation_visible'].set(metadata.get('federation_visible', False))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def save_memory():
            content = content_text.get('1.0', tk.END).strip()
            if not content:
                messagebox.showerror("Error", "Content cannot be empty!")
                return
            
            # Build metadata
            metadata = {
                'title': fields['title'].get(),
                'domain': fields['domain'].get() or 'technical',
                'category': fields['category'].get() or 'memory',
                'priority': int(fields['priority'].get() or 1),
                'is_essential': flag_vars['is_essential'].get(),
                'needs_review': flag_vars['needs_review'].get(),
                'is_private': flag_vars['is_private'].get(),
                'federation_visible': flag_vars['federation_visible'].get(),
                'schema_version': 'v5.0',
                'memory_type': 'living',
                'created_by': 'memory_browser'
            }
            
            # Handle tags
            tags_text = fields['tags'].get().strip()
            if tags_text:
                metadata['tags'] = [tag.strip() for tag in tags_text.split(',')]
            
            try:
                if mode == "create":
                    # Create new memory
                    collection_name = collection_var.get()
                    collection = self.collections.get(collection_name)
                    
                    if collection:
                        memory_id = f"{collection_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
                        metadata['created_at'] = datetime.now().isoformat()
                        metadata['version'] = 1
                        
                        collection.add(
                            documents=[content],
                            metadatas=[metadata],
                            ids=[memory_id]
                        )
                        
                        self.set_status(f"Created memory: {memory_id}")
                        messagebox.showinfo("Success", "Memory created successfully!")
                
                elif mode == "update":
                    # Update existing memory
                    collection_name = memory['collection']
                    collection = self.collections.get(collection_name)
                    
                    if collection:
                        # Update metadata with version info
                        existing_metadata = memory.get('metadata', {})
                        metadata['version'] = existing_metadata.get('version', 1) + 1
                        metadata['created_at'] = existing_metadata.get('created_at', datetime.now().isoformat())
                        metadata['last_updated'] = datetime.now().isoformat()
                        
                        # Update in ChromaDB
                        collection.update(
                            ids=[memory['id']],
                            documents=[content],
                            metadatas=[metadata]
                        )
                        
                        self.set_status(f"Updated memory: {memory['id']}")
                        messagebox.showinfo("Success", "Memory updated successfully!")
                
                # Refresh the browser
                self.load_memories()
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save memory: {str(e)}")
                self.set_status(f"Error saving memory: {str(e)}")
        
        def cancel():
            dialog.destroy()
        
        # Buttons
        ttk.Button(button_frame, text="Save", command=save_memory, style='TButton').pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel, style='TButton').pack(side=tk.RIGHT, padx=5)


def main():
    root = tk.Tk()
    app = MemoryBrowserV5(root)
    root.mainloop()


if __name__ == "__main__":
    main()