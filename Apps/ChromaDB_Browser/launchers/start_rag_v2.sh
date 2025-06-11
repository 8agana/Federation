#!/bin/bash

echo "🚀 Starting ChromaDB Browser with Federation RAG V2"
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if RAG server is running
echo -e "${BLUE}Checking if RAG V2 server is running...${NC}"
if lsof -i :5100 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ RAG V2 server is already running on port 5100${NC}"
else
    echo -e "${RED}✗ RAG V2 server is not running${NC}"
    echo -e "${BLUE}Starting RAG V2 server in background...${NC}"
    
    # Start the server in background
    cd /Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/federation_rag
    nohup python3 run_cc_server_v2.py > rag_server.log 2>&1 &
    
    # Wait a bit for server to start
    sleep 5
    
    if lsof -i :5100 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ RAG V2 server started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start RAG V2 server. Check rag_server.log for errors${NC}"
        exit 1
    fi
fi

# Start the ChromaDB Browser
echo -e "${BLUE}Starting ChromaDB Browser with RAG V2...${NC}"
cd /Users/samuelatagana/Documents/Federation/Apps/ChromaDB_Browser/src

# Check if GROQ_API_KEY is set
if [ -z "$GROQ_API_KEY" ]; then
    echo -e "${RED}Warning: GROQ_API_KEY not set. LLM synthesis will be unavailable.${NC}"
    echo "To enable LLM synthesis, set your GROQ API key:"
    echo "  export GROQ_API_KEY='your-api-key-here'"
fi

# Run the browser
python3 chromadb_rag_browser_v2.py