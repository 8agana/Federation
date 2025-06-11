#!/bin/bash
# Launch Federation Browser

echo "🚀 Launching Federation Memory Browser (Tkinter Bigger)..."

# Navigate to the correct directory
cd /Users/samuelatagana/Documents/Federation/Apps/ChromaDB_Browser/src

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if tkinter is available
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Tkinter not available. Please install python3-tk"
    exit 1
fi

# Check if chromadb is installed
python3 -c "import chromadb" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing ChromaDB..."
    pip3 install chromadb
fi

# Launch the browser
echo "✨ Starting browser..."
python3 tkinter_memory_browser_v5_bigger.py