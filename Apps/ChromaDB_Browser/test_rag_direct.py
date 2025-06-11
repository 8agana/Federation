#!/usr/bin/env python3
"""Test RAG V2 directly without GUI"""

import os
import sys

# Set GROQ API key
os.environ['GROQ_API_KEY'] = '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'

# Add Federation RAG to path
sys.path.append('/Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/federation_rag')

try:
    from cc_federation_rag_v2 import CCFederationRAGv2
    
    print("Testing Federation RAG V2")
    print("=" * 50)
    
    # Initialize RAG
    rag = CCFederationRAGv2()
    print("✓ RAG initialized")
    
    # Test query
    test_query = "What are we working on?"
    print(f"\nTesting query: '{test_query}'")
    print("-" * 50)
    
    # Try auto query
    try:
        print("\nTrying query_auto...")
        result = rag.query_auto(test_query)
        print(f"✓ Success! Found {result.get('contexts_found', 0)} contexts")
        print(f"Tool used: {result.get('tool_used', 'unknown')}")
        print(f"Answer preview: {result.get('answer', 'No answer')[:200]}...")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Try daily query
    try:
        print("\n\nTrying query_daily...")
        result = rag.query_daily(test_query)
        print(f"✓ Success! Found {result.get('contexts_found', 0)} contexts")
        print(f"Answer preview: {result.get('answer', 'No answer')[:200]}...")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"Failed to import RAG: {e}")
    import traceback
    traceback.print_exc()