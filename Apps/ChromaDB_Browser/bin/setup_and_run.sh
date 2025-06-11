#!/bin/bash
# Quick setup for Federation Browser

echo "🧠 Setting up Federation Memory Browser (Tkinter Bigger)..."

# Navigate to src directory
cd /Users/samuelatagana/Documents/Federation/Apps/ChromaDB_Browser/src

# Check if we're in the right directory
if [ ! -f "tkinter_memory_browser_v5_bigger.py" ]; then
    echo "❌ Cannot find tkinter_memory_browser_v5_bigger.py"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install chromadb

# Run the browser
echo "🚀 Launching Federation Browser..."
python tkinter_memory_browser_v5_bigger.py

echo "✅ Browser should be running! Check for the Tkinter window."
