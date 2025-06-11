#!/usr/bin/env python3
"""
Test script for SharedTokenMetrics - DT Instance
"""

import sys
import os
sys.path.append('/Users/samuelatagana/Documents/Federation/System/Memory/2_BridgeScripts/utilities')

try:
    from shared_token_metrics import SharedTokenMetrics
    print("✅ Successfully imported SharedTokenMetrics")
    
    # Initialize as DT instance
    dt_metrics = SharedTokenMetrics("DT")
    print("✅ Successfully created DT instance of SharedTokenMetrics")
    
    # Track a test operation with this conversation content
    test_content = "Testing shared token metrics collection with DT instance. This 50k+ token conversation is perfect for testing high token scenarios. We're building collaborative AI token tracking to prevent token deaths."
    
    result = dt_metrics.track_memory_operation(
        operation="test_memory_operation",
        content=test_content,
        additional_metadata={
            "test_type": "shared_collection_validation",
            "conversation_context": "50k+ token session",
            "source": "DT_testing_phase"
        }
    )