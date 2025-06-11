#!/usr/bin/env python3
"""
Federation Tools Launcher
Choose between Memory Browser and RAG Search
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import os

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Federation Tools Launcher")
        self.root.geometry("600x400")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Header
        header = ttk.Label(
            root,
            text="Federation Tools",
            font=('Helvetica', 24, 'bold')
        )
        header.pack(pady=30)
        
        # Description
        desc = ttk.Label(
            root,
            text="Choose a tool to launch:",
            font=('Helvetica', 14)
        )
        desc.pack(pady=(0, 30))
        
        # Buttons frame
        buttons_frame = ttk.Frame(root)
        buttons_frame.pack(expand=True)
        
        # Memory Browser button
        memory_frame = ttk.LabelFrame(buttons_frame, text="Memory Browser", padding=20)
        memory_frame.grid(row=0, column=0, padx=20, pady=10)
        
        ttk.Label(
            memory_frame,
            text="🧠",
            font=('Helvetica', 48)
        ).pack()
        
        ttk.Label(
            memory_frame,
            text="Browse CC & DT memories\nwith advanced filtering",
            font=('Helvetica', 12),
            justify='center'
        ).pack(pady=10)
        
        ttk.Button(
            memory_frame,
            text="Launch Memory Browser",
            command=self.launch_memory_browser,
            style='Accent.TButton'
        ).pack()
        
        # RAG Search button
        rag_frame = ttk.LabelFrame(buttons_frame, text="RAG V2 Search", padding=20)
        rag_frame.grid(row=0, column=1, padx=20, pady=10)
        
        ttk.Label(
            rag_frame,
            text="🚀",
            font=('Helvetica', 48)
        ).pack()
        
        ttk.Label(
            rag_frame,
            text="Search across all sources\nwith 5 specialized tools",
            font=('Helvetica', 12),
            justify='center'
        ).pack(pady=10)
        
        ttk.Button(
            rag_frame,
            text="Launch RAG Search",
            command=self.launch_rag_search,
            style='Accent.TButton'
        ).pack()
        
        # Status
        self.status = ttk.Label(
            root,
            text="Ready to launch",
            font=('Helvetica', 12),
            foreground='gray'
        )
        self.status.pack(pady=20)
    
    def launch_memory_browser(self):
        """Launch memory browser"""
        self.status.config(text="Launching Memory Browser...", foreground='blue')
        self.root.update()
        
        script = os.path.join(os.path.dirname(__file__), 'memory_browser_app.py')
        subprocess.Popen([sys.executable, script])
        
        self.root.after(1000, lambda: self.status.config(text="Memory Browser launched", foreground='green'))
        self.root.after(3000, lambda: self.status.config(text="Ready to launch", foreground='gray'))
    
    def launch_rag_search(self):
        """Launch RAG search"""
        self.status.config(text="Launching RAG Search...", foreground='blue')
        self.root.update()
        
        script = os.path.join(os.path.dirname(__file__), 'rag_search_app.py')
        subprocess.Popen([sys.executable, script])
        
        self.root.after(1000, lambda: self.status.config(text="RAG Search launched", foreground='green'))
        self.root.after(3000, lambda: self.status.config(text="Ready to launch", foreground='gray'))


def main():
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()