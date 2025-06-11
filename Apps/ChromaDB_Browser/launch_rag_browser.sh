#!/bin/bash
# Launch ChromaDB RAG Browser

echo "🚀 Launching ChromaDB RAG Browser..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "src/venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv src/venv
fi

# Activate virtual environment
source src/venv/bin/activate

# Install/upgrade required packages
echo "📦 Checking dependencies..."
pip install --quiet --upgrade chromadb langchain langchain-community langchain-groq \
    sentence-transformers python-dotenv

# Check for GROQ_API_KEY
if [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  GROQ_API_KEY not set. LLM synthesis will be disabled."
    echo "   To enable: export GROQ_API_KEY='your-api-key'"
else
    echo "✅ GROQ API key found. LLM synthesis enabled."
fi

echo ""
echo "🤖 Starting ChromaDB RAG Browser..."
echo "=================================="

# Launch the RAG browser
cd src
python chromadb_rag_browser.py