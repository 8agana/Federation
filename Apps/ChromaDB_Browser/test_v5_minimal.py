#!/usr/bin/env python3
"""Test v5 browser initialization step by step"""

import tkinter as tk
from tkinter import ttk
import chromadb

print("Step 1: Creating root window...")
root = tk.Tk()
root.title("Test v5 Browser")
root.geometry("800x600")

print("Step 2: Creating main frame...")
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

print("Step 3: Creating treeview...")
tree = ttk.Treeview(main_frame)
tree['columns'] = ('Date', 'Title', 'Domain', 'Priority')
tree.pack(fill=tk.BOTH, expand=True)

print("Step 4: Loading ChromaDB...")
base_path = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs"
try:
    cc_client = chromadb.PersistentClient(path=f"{base_path}/cc-federation")
    cc_collection = cc_client.get_collection("cc_memories")
    print(f"✓ Loaded CC: {cc_collection.count()} memories")
except Exception as e:
    print(f"✗ Error: {e}")

print("Step 5: Starting mainloop...")
print("If it hangs here, it's the mainloop")
root.mainloop()
print("Done!")