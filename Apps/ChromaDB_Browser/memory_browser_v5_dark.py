#!/usr/bin/env python3
"""
ChromaDB Memory Browser v5 - Dark Theme Fixed Version
All the v5 features with proper dark theme
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the v5 browser
from tkinter_memory_browser_v5_bigger import MemoryBrowserV5
import tkinter as tk
from tkinter import ttk

class DarkMemoryBrowserV5(MemoryBrowserV5):
    """v5 Browser with dark theme fixes"""
    
    def __init__(self, root):
        # Set dark theme before calling parent init
        self.setup_dark_theme(root)
        super().__init__(root)
    
    def setup_dark_theme(self, root):
        """Configure dark theme colors"""
        # Dark color scheme
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#d4d4d4',
            'select_bg': '#264f78',
            'select_fg': '#ffffff',
            'button_bg': '#2d2d30',
            'entry_bg': '#3c3c3c',
            'tree_bg': '#252526',
            'tree_fg': '#cccccc',
            'tree_selected': '#094771',
            'frame_bg': '#2d2d30',
            'label_fg': '#cccccc'
        }
        
        # Configure root
        root.configure(bg=self.colors['bg'])
        
        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure all ttk widgets
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', background=self.colors['button_bg'], foreground=self.colors['fg'])
        style.map('TButton',
            background=[('active', self.colors['select_bg'])],
            foreground=[('active', self.colors['select_fg'])]
        )
        
        # Entry style
        style.configure('TEntry', 
            fieldbackground=self.colors['entry_bg'],
            background=self.colors['entry_bg'],
            foreground=self.colors['fg'],
            insertcolor=self.colors['fg']
        )
        
        # Combobox style
        style.configure('TCombobox',
            fieldbackground=self.colors['entry_bg'],
            background=self.colors['button_bg'],
            foreground=self.colors['fg']
        )
        
        # Checkbutton style
        style.configure('TCheckbutton',
            background=self.colors['bg'],
            foreground=self.colors['fg']
        )
        
        # LabelFrame style
        style.configure('TLabelframe',
            background=self.colors['bg'],
            foreground=self.colors['fg']
        )
        style.configure('TLabelframe.Label',
            background=self.colors['bg'],
            foreground=self.colors['fg']
        )
        
        # Notebook style
        style.configure('TNotebook',
            background=self.colors['bg']
        )
        style.configure('TNotebook.Tab',
            background=self.colors['button_bg'],
            foreground=self.colors['fg']
        )
        style.map('TNotebook.Tab',
            background=[('selected', self.colors['select_bg'])],
            foreground=[('selected', self.colors['select_fg'])]
        )
        
        # Treeview style
        style.configure('Treeview',
            background=self.colors['tree_bg'],
            foreground=self.colors['tree_fg'],
            fieldbackground=self.colors['tree_bg']
        )
        style.configure('Treeview.Heading',
            background=self.colors['button_bg'],
            foreground=self.colors['fg']
        )
        style.map('Treeview',
            background=[('selected', self.colors['tree_selected'])],
            foreground=[('selected', self.colors['select_fg'])]
        )
        
        # Scrollbar style
        style.configure('TScrollbar',
            background=self.colors['button_bg'],
            troughcolor=self.colors['tree_bg'],
            bordercolor=self.colors['bg'],
            arrowcolor=self.colors['fg'],
            darkcolor=self.colors['bg'],
            lightcolor=self.colors['bg']
        )
    
    def configure_styles(self):
        """Override to keep dark theme while configuring fonts"""
        style = ttk.Style()
        
        # Configure fonts - BIGGER SIZES
        default_font = ('Helvetica', 18)
        heading_font = ('Helvetica', 22, 'bold')
        tree_font = ('Helvetica', 16)
        
        # Configure styles with fonts only (colors already set)
        style.configure('Heading.TLabel', font=heading_font)
        style.configure('TLabel', font=default_font)
        style.configure('TButton', font=default_font)
        style.configure('Treeview', font=tree_font, rowheight=40)
        style.configure('Treeview.Heading', font=heading_font)
        style.configure('TCheckbutton', font=default_font)
        style.configure('TCombobox', font=default_font)
        style.configure('TEntry', font=default_font)

def main():
    print("🌙 Starting ChromaDB Memory Browser v5 - Dark Theme")
    print("=" * 50)
    print("Loading CC and DT memories with dark theme...")
    print()
    
    root = tk.Tk()
    
    # Also configure Text widgets (not ttk)
    root.option_add('*Text.background', '#3c3c3c')
    root.option_add('*Text.foreground', '#d4d4d4')
    root.option_add('*Text.insertBackground', '#d4d4d4')
    root.option_add('*Text.selectBackground', '#264f78')
    root.option_add('*Text.selectForeground', '#ffffff')
    
    app = DarkMemoryBrowserV5(root)
    root.mainloop()

if __name__ == "__main__":
    main()