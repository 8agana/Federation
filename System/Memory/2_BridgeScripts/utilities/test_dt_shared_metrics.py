#!/usr/bin/env python3
"""
Test SharedTokenMetrics as DT instance
Tests collection creation, token tracking, and dashboard visualization
"""

import sys
from pathlib import Path
from datetime import datetime

# Add utilities to path
sys.path.append(str(Path(__file__).parent))
from shared_token_metrics import SharedTokenMetrics

def test_dt_metrics():
    """Run comprehensive test of SharedTokenMetrics as DT instance"""
    
    print("🧪 Testing SharedTokenMetrics as DT Instance")
    print("=" * 60)
    
    try:
        # Initialize as DT
        print("\n1️⃣ Initializing DT metrics instance...")
        dt_metrics = SharedTokenMetrics("DT")
        print("✅ Successfully initialized DT instance")
        
        # Test content from user
        test_content = """Testing shared token metrics collection with DT instance. 
This 50k+ token conversation is perfect for testing high token scenarios. 
We're building collaborative AI token tracking to prevent token deaths."""
        
        # Track initial operation
        print("\n2️⃣ Tracking test memory operation...")
        result1 = dt_metrics.track_memory_operation(
            operation="remember",
            content=test_content,
            memory_id="dt_test_001",
            additional_metadata={
                "test_type": "initial_test",
                "conversation_context": "50k+ token conversation"
            }
        )
        
        print(f"✅ Tracked operation:")
        print(f"   - Instance: {result1['instance']}")
        print(f"   - Tokens: {result1['tokens']}")
        print(f"   - Cumulative: {result1['cumulative_tokens']}")
        print(f"   - Usage: {result1['usage_percent']:.1f}%")
        print(f"   - Urgency: {result1['urgency']}")
        print(f"   - Metric ID: {result1['metric_id']}")
        
        # Track a larger operation to simulate high token usage
        print("\n3️⃣ Simulating high-token operation...")
        large_content = test_content * 100  # Simulate larger content
        
        result2 = dt_metrics.track_memory_operation(
            operation="update",
            content=large_content,
            memory_id="dt_test_002",
            additional_metadata={
                "test_type": "high_token_test",
                "simulated_scenario": "preventing token death"
            }
        )
        
        print(f"✅ High-token operation tracked:")
        print(f"   - Tokens: {result2['tokens']}")
        print(f"   - Cumulative: {result2['cumulative_tokens']}")
        print(f"   - Usage: {result2['usage_percent']:.1f}%")
        print(f"   - Urgency: {result2['urgency']}")
        
        # Check combined usage
        print("\n4️⃣ Checking combined CC/DT usage...")
        combined = dt_metrics.get_combined_usage()
        
        print(f"✅ Combined metrics (last hour):")
        print(f"   - CC tokens: {combined['cc_tokens']:,}")
        print(f"   - DT tokens: {combined['dt_tokens']:,}")
        print(f"   - Total tokens: {combined['total_tokens']:,}")
        print(f"   - CC operations: {combined['cc_operations']}")
        print(f"   - DT operations: {combined['dt_operations']}")
        print(f"   - Highest urgency: {combined['highest_urgency']}")
        
        # Check save recommendation
        print("\n5️⃣ Checking auto-save recommendation...")
        save_check = dt_metrics.should_trigger_save()
        
        print(f"✅ Save recommendation:")
        print(f"   - Should save: {save_check['should_save']}")
        print(f"   - Reason: {save_check['reason']}")
        
        # Display dashboard
        print("\n6️⃣ Token Usage Dashboard:")
        print(dt_metrics.get_usage_dashboard())
        
        # Query collection directly to verify storage
        print("\n7️⃣ Verifying ChromaDB storage...")
        collection_count = dt_metrics.metrics_collection.count()
        print(f"✅ Token metrics collection contains {collection_count} entries")
        
        # Get recent entries
        recent_results = dt_metrics.metrics_collection.get(
            limit=5,
            include=["metadatas", "documents"]
        )
        
        if recent_results["metadatas"]:
            print("\n📋 Recent metric entries:")
            for i, (doc, meta) in enumerate(zip(recent_results["documents"], recent_results["metadatas"])):
                print(f"\n   Entry {i+1}:")
                print(f"   - Document: {doc}")
                print(f"   - Instance: {meta.get('instance', 'N/A')}")
                print(f"   - Operation: {meta.get('operation', 'N/A')}")
                print(f"   - Tokens: {meta.get('tokens', 0)}")
                print(f"   - Timestamp: {meta.get('timestamp', 'N/A')}")
        
        # Test session reset
        print("\n8️⃣ Testing session reset...")
        final_metrics = dt_metrics.reset_session()
        
        print(f"✅ Session reset completed:")
        print(f"   - Final token count: {final_metrics['total_tokens']}")
        print(f"   - Total operations: {final_metrics['total_operations']}")
        print(f"   - Operations by type: {final_metrics['operations_by_type']}")
        
        print("\n✨ All tests completed successfully!")
        print("The shared token metrics system is working correctly for DT instance.")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = test_dt_metrics()
    sys.exit(0 if success else 1)