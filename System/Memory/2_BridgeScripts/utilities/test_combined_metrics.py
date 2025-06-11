#!/usr/bin/env python3
"""
Test combined CC and DT metrics to show federation collaboration
"""

import sys
from pathlib import Path
from datetime import datetime
import time

# Add utilities to path
sys.path.append(str(Path(__file__).parent))
from shared_token_metrics import SharedTokenMetrics

def test_combined_federation():
    """Test both CC and DT instances interacting"""
    
    print("🤝 Testing Combined CC/DT Token Metrics")
    print("=" * 60)
    
    # Create both instances
    cc_metrics = SharedTokenMetrics("CC")
    dt_metrics = SharedTokenMetrics("DT")
    
    # Simulate CC doing some work
    print("\n1️⃣ CC Instance Working...")
    cc_metrics.track_memory_operation(
        "remember",
        "CC is processing user request about photography workflow automation",
        memory_id="cc_photo_001"
    )
    
    cc_metrics.track_memory_operation(
        "recall",
        "Searching for previous photography scripts and configurations",
        memory_id="cc_photo_002"
    )
    
    # Simulate DT doing heavy lifting
    print("\n2️⃣ DT Instance Working (50k+ token scenario)...")
    
    # Create large content to simulate high token usage
    large_content = """Testing shared token metrics collection with DT instance. 
This 50k+ token conversation is perfect for testing high token scenarios. 
We're building collaborative AI token tracking to prevent token deaths.
""" * 500  # Simulate very large content
    
    dt_result = dt_metrics.track_memory_operation(
        "update",
        large_content,
        memory_id="dt_heavy_001",
        additional_metadata={
            "context": "Processing large codebase refactoring",
            "risk": "approaching token limit"
        }
    )
    
    print(f"   DT processed {dt_result['tokens']:,} tokens")
    print(f"   Usage now at {dt_result['usage_percent']:.1f}%")
    print(f"   Urgency: {dt_result['urgency']}")
    
    # Show combined view from CC's perspective
    print("\n3️⃣ CC Checking Combined Status...")
    cc_combined = cc_metrics.get_combined_usage()
    print(f"   From CC's view:")
    print(f"   - My tokens: {cc_combined['cc_tokens']:,}")
    print(f"   - DT tokens: {cc_combined['dt_tokens']:,}")
    print(f"   - Combined total: {cc_combined['total_tokens']:,}")
    print(f"   - Risk level: {cc_combined['highest_urgency']}")
    
    # Check if CC should trigger save based on DT's high usage
    cc_save_check = cc_metrics.should_trigger_save()
    print(f"\n4️⃣ CC Auto-save Check:")
    print(f"   Should save: {cc_save_check['should_save']}")
    print(f"   Reason: {cc_save_check['reason']}")
    
    # Show dashboards from both perspectives
    print("\n5️⃣ CC's Dashboard View:")
    print(cc_metrics.get_usage_dashboard())
    
    print("\n6️⃣ DT's Dashboard View:")
    print(dt_metrics.get_usage_dashboard())
    
    # Simulate more work to trigger HIGH urgency
    print("\n7️⃣ Pushing towards token limit...")
    dt_metrics.track_memory_operation(
        "remember",
        large_content * 2,  # Even larger
        memory_id="dt_heavy_002"
    )
    
    # Check urgency again
    final_check = dt_metrics.should_trigger_save()
    print(f"\n8️⃣ Final Federation Status:")
    print(f"   Auto-save triggered: {final_check['should_save']}")
    print(f"   Urgency level: {final_check['combined_metrics']['highest_urgency']}")
    print(f"   Total federation tokens: {final_check['combined_metrics']['total_tokens']:,}")
    
    # Show collection stats
    print(f"\n📊 Shared Collection Stats:")
    collection_count = dt_metrics.metrics_collection.count()
    print(f"   Total metric entries: {collection_count}")
    
    return True

if __name__ == "__main__":
    test_combined_federation()