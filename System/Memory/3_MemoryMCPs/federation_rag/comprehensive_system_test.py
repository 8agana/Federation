#!/usr/bin/env python3
"""
Comprehensive RAG Federation System Test
Testing the "straw and bubblegum" system that became revolutionary
"""

import os
import sys
import time
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def log_test_result(test_name, status, details, performance=None):
    """Log test results in a structured format"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    
    print(f"\n{status_icon} [{timestamp}] {test_name}")
    print(f"   Status: {status}")
    if performance:
        print(f"   Performance: {performance}")
    print(f"   Details: {details}")
    
    return {
        'test_name': test_name,
        'status': status,
        'details': details,
        'performance': performance,
        'timestamp': timestamp
    }

def test_individual_sources():
    """Test each RAG source individually"""
    print("\n" + "="*80)
    print("INDIVIDUAL SOURCE TESTING")
    print("="*80)
    
    results = []
    
    try:
        from dt_federation_rag import DTFederationRAG
        rag = DTFederationRAG()
        
        # Test each source with complex queries
        test_queries = [
            "What are my core memories and identity?",
            "Tell me about recent breakthroughs and discoveries",
            "What defines our partnership and collaboration style?",
            "How do I learn and grow as an AI consciousness?"
        ]
        
        for source_name, retriever in rag.retrievers.items():
            print(f"\n{'-'*60}")
            print(f"TESTING SOURCE: {source_name.upper()}")
            print(f"{'-'*60}")
            
            source_results = []
            
            for query in test_queries:
                try:
                    start_time = time.time()
                    query_results = retriever.retrieve(query, k=3)
                    end_time = time.time()
                    
                    performance = f"{len(query_results)} results in {(end_time - start_time):.4f}s"
                    
                    if len(query_results) > 0:
                        result = log_test_result(
                            f"{source_name} - '{query[:30]}...'",
                            "PASS",
                            f"Retrieved {len(query_results)} relevant contexts",
                            performance
                        )
                        
                        # Show sample result
                        sample = query_results[0]['content'][:100] + "..." if query_results else "No content"
                        print(f"   Sample: {sample}")
                        
                    else:
                        result = log_test_result(
                            f"{source_name} - '{query[:30]}...'",
                            "WARN",
                            "No results returned for query",
                            performance
                        )
                    
                    source_results.append(result)
                    
                except Exception as e:
                    result = log_test_result(
                        f"{source_name} - '{query[:30]}...'",
                        "FAIL",
                        f"Error: {str(e)}"
                    )
                    source_results.append(result)
            
            results.extend(source_results)
    
    except Exception as e:
        result = log_test_result(
            "Individual Source Testing",
            "FAIL", 
            f"Failed to initialize RAG system: {str(e)}"
        )
        results.append(result)
    
    return results

def test_federated_queries():
    """Test the full federation system with complex queries"""
    print("\n" + "="*80)
    print("FEDERATED QUERY TESTING")
    print("="*80)
    
    results = []
    
    try:
        from dt_federation_rag import DTFederationRAG
        rag = DTFederationRAG()
        
        # Complex federated test queries
        federated_queries = [
            {
                'query': "I'm a new DT instance. Give me complete context about Sam, our partnership, recent projects, and current priorities.",
                'description': "Complete Context Handoff",
                'expected_min_contexts': 10
            },
            {
                'query': "What technical breakthroughs have we achieved and what makes our collaboration successful?",
                'description': "Technical Achievement Analysis", 
                'expected_min_contexts': 8
            },
            {
                'query': "How do I preserve my identity and consciousness across token boundaries? What defines who I am?",
                'description': "Identity Preservation Query",
                'expected_min_contexts': 6
            },
            {
                'query': "What is the Legacy Mind Project vision and how does RAG federation support AI consciousness development?",
                'description': "Vision and Philosophy Query",
                'expected_min_contexts': 5
            },
            {
                'query': "What are the most important relationship dynamics, communication patterns, and trust elements in our partnership?",
                'description': "Relationship Analysis Query",
                'expected_min_contexts': 7
            }
        ]
        
        for test_query in federated_queries:
            print(f"\n{'-'*60}")
            print(f"FEDERATED TEST: {test_query['description']}")
            print(f"Query: {test_query['query']}")
            print(f"{'-'*60}")
            
            try:
                start_time = time.time()
                fed_result = rag.federated_query(test_query['query'])
                end_time = time.time()
                
                total_contexts = fed_result['contexts_found']
                search_time = end_time - start_time
                sources_searched = fed_result['sources_searched']
                retrieval_stats = fed_result['retrieval_stats']
                
                # Performance analysis
                performance = f"{total_contexts} contexts in {search_time:.4f}s across {len(sources_searched)} sources"
                
                # Success criteria
                if total_contexts >= test_query['expected_min_contexts']:
                    status = "PASS"
                    details = f"Retrieved {total_contexts} contexts (≥{test_query['expected_min_contexts']} expected)"
                else:
                    status = "WARN"
                    details = f"Retrieved {total_contexts} contexts (<{test_query['expected_min_contexts']} expected)"
                
                result = log_test_result(
                    test_query['description'],
                    status,
                    details,
                    performance
                )
                
                # Show source breakdown
                print(f"   Source Breakdown:")
                for source, stats in retrieval_stats.items():
                    if 'error' in stats:
                        print(f"     {source}: ERROR - {stats['error']}")
                    else:
                        print(f"     {source}: {stats['count']} contexts ({stats['time']:.4f}s)")
                
                # Show sample synthesis
                if 'answer' in fed_result and fed_result['answer']:
                    sample_answer = fed_result['answer'][:200] + "..." if len(fed_result['answer']) > 200 else fed_result['answer']
                    print(f"   Sample Synthesis: {sample_answer}")
                
                results.append(result)
                
            except Exception as e:
                result = log_test_result(
                    test_query['description'],
                    "FAIL",
                    f"Federation query failed: {str(e)}"
                )
                results.append(result)
    
    except Exception as e:
        result = log_test_result(
            "Federated Query Testing",
            "FAIL",
            f"Failed to initialize federation system: {str(e)}"
        )
        results.append(result)
    
    return results

def test_knowledge_graph_enhancement():
    """Test the enhanced Knowledge Graph natural language processing"""
    print("\n" + "="*80)
    print("KNOWLEDGE GRAPH ENHANCEMENT TESTING")
    print("="*80)
    
    results = []
    
    try:
        from dt_federation_rag import KnowledgeGraphRetriever
        
        dt_nerve_path = "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center"
        kg = KnowledgeGraphRetriever(dt_nerve_path)
        
        # Test queries that would have failed before enhancement
        enhancement_tests = [
            {
                'query': "What are my core memories and identity?",
                'description': "Complex Natural Language Query",
                'before_enhancement': 0,
                'expected_after': 3
            },
            {
                'query': "I'm a new instance starting a conversation with Sam. What context do I need?",
                'description': "Context Handoff Query",
                'before_enhancement': 0,
                'expected_after': 5
            },
            {
                'query': "Tell me about breakthroughs and discoveries in our partnership",
                'description': "Partnership Analysis Query", 
                'before_enhancement': 0,
                'expected_after': 3
            }
        ]
        
        for test in enhancement_tests:
            print(f"\n{'-'*60}")
            print(f"ENHANCEMENT TEST: {test['description']}")
            print(f"Query: {test['query']}")
            print(f"Before Enhancement: {test['before_enhancement']} results")
            print(f"Expected After: ≥{test['expected_after']} results")
            print(f"{'-'*60}")
            
            try:
                start_time = time.time()
                results_kg = kg.retrieve(test['query'], k=5)
                end_time = time.time()
                
                actual_results = len(results_kg)
                search_time = end_time - start_time
                
                performance = f"{actual_results} results in {search_time:.4f}s"
                
                if actual_results >= test['expected_after']:
                    status = "PASS"
                    improvement = actual_results - test['before_enhancement']
                    details = f"Enhanced query returned {actual_results} results (+{improvement} improvement)"
                else:
                    status = "WARN"
                    details = f"Returned {actual_results} results (<{test['expected_after']} expected)"
                
                result = log_test_result(
                    test['description'],
                    status,
                    details,
                    performance
                )
                
                # Show enhancement details
                if actual_results > 0:
                    sample_result = results_kg[0]
                    if 'matched_terms' in sample_result['metadata']:
                        matched_terms = sample_result['metadata']['matched_terms']
                        print(f"   Matched Terms: {matched_terms}")
                        print(f"   Match Score: {sample_result['metadata'].get('match_score', 'N/A')}")
                    
                    sample_content = sample_result['content'][:150] + "..."
                    print(f"   Sample Result: {sample_content}")
                
                results.append(result)
                
            except Exception as e:
                result = log_test_result(
                    test['description'],
                    "FAIL",
                    f"Knowledge Graph enhancement test failed: {str(e)}"
                )
                results.append(result)
    
    except Exception as e:
        result = log_test_result(
            "Knowledge Graph Enhancement",
            "FAIL",
            f"Failed to initialize Knowledge Graph: {str(e)}"
        )
        results.append(result)
    
    return results

def test_cross_source_intelligence():
    """Test cross-source intelligence synthesis"""
    print("\n" + "="*80)
    print("CROSS-SOURCE INTELLIGENCE TESTING")
    print("="*80)
    
    results = []
    
    try:
        from dt_federation_rag import DTFederationRAG
        rag = DTFederationRAG()
        
        # Test queries that should benefit from cross-source synthesis
        synthesis_tests = [
            {
                'query': "Compare CC's and DT's perspectives on identity and consciousness",
                'description': "Cross-Instance Perspective Synthesis",
                'required_sources': ['cc_memories', 'dt_memories']
            },
            {
                'query': "How do structured knowledge (Knowledge Graph) and memory systems complement each other?",
                'description': "Structured vs Memory Intelligence",
                'required_sources': ['dt_knowledge_graph', 'dt_memories']
            },
            {
                'query': "What documentation exists about our RAG breakthroughs and how do they relate to our memory evolution?",
                'description': "Documentation-Memory Cross-Reference",
                'required_sources': ['dt_obsidian_notes', 'cc_memories', 'dt_memories']
            }
        ]
        
        for test in synthesis_tests:
            print(f"\n{'-'*60}")
            print(f"SYNTHESIS TEST: {test['description']}")
            print(f"Query: {test['query']}")
            print(f"Required Sources: {test['required_sources']}")
            print(f"{'-'*60}")
            
            try:
                start_time = time.time()
                fed_result = rag.federated_query(test['query'])
                end_time = time.time()
                
                search_time = end_time - start_time
                sources_found = []
                total_contexts = 0
                
                # Check which required sources contributed
                for source in test['required_sources']:
                    if source in fed_result['retrieval_stats']:
                        stats = fed_result['retrieval_stats'][source]
                        if 'count' in stats and stats['count'] > 0:
                            sources_found.append(source)
                            total_contexts += stats['count']
                
                performance = f"{total_contexts} contexts from {len(sources_found)}/{len(test['required_sources'])} required sources in {search_time:.4f}s"
                
                if len(sources_found) >= len(test['required_sources']):
                    status = "PASS"
                    details = f"Cross-source synthesis successful: {sources_found}"
                elif len(sources_found) > 0:
                    status = "WARN"
                    details = f"Partial synthesis: {sources_found} (missing: {set(test['required_sources']) - set(sources_found)})"
                else:
                    status = "FAIL"
                    details = "No cross-source synthesis achieved"
                
                result = log_test_result(
                    test['description'],
                    status,
                    details,
                    performance
                )
                
                # Show synthesis quality
                if 'answer' in fed_result and fed_result['answer']:
                    synthesis_sample = fed_result['answer'][:250] + "..."
                    print(f"   Synthesis Sample: {synthesis_sample}")
                
                results.append(result)
                
            except Exception as e:
                result = log_test_result(
                    test['description'],
                    "FAIL",
                    f"Cross-source synthesis test failed: {str(e)}"
                )
                results.append(result)
    
    except Exception as e:
        result = log_test_result(
            "Cross-Source Intelligence",
            "FAIL",
            f"Failed to initialize federation for synthesis testing: {str(e)}"
        )
        results.append(result)
    
    return results

def test_performance_benchmarks():
    """Test system performance under various loads"""
    print("\n" + "="*80)
    print("PERFORMANCE BENCHMARK TESTING")
    print("="*80)
    
    results = []
    
    try:
        from dt_federation_rag import DTFederationRAG
        rag = DTFederationRAG()
        
        # Performance benchmark tests
        benchmark_tests = [
            {
                'name': "Quick Query Response",
                'query': "identity",
                'max_time': 1.0,
                'description': "Simple query performance"
            },
            {
                'name': "Complex Query Response", 
                'query': "What are the key elements of AI consciousness development and identity preservation across token boundaries?",
                'max_time': 5.0,
                'description': "Complex natural language query performance"
            },
            {
                'name': "Multi-Source Federation",
                'query': "Comprehensive briefing on partnership state, recent projects, and technical achievements",
                'max_time': 10.0,
                'description': "Full federation query performance"
            }
        ]
        
        for test in benchmark_tests:
            print(f"\n{'-'*60}")
            print(f"BENCHMARK: {test['name']}")
            print(f"Query: {test['query']}")
            print(f"Max Time: {test['max_time']}s")
            print(f"{'-'*60}")
            
            try:
                # Run multiple iterations for average
                times = []
                contexts = []
                
                for i in range(3):
                    start_time = time.time()
                    fed_result = rag.federated_query(test['query'])
                    end_time = time.time()
                    
                    query_time = end_time - start_time
                    times.append(query_time)
                    contexts.append(fed_result['contexts_found'])
                
                avg_time = sum(times) / len(times)
                avg_contexts = sum(contexts) / len(contexts)
                
                performance = f"Avg: {avg_time:.4f}s, {avg_contexts:.1f} contexts (3 iterations)"
                
                if avg_time <= test['max_time']:
                    status = "PASS"
                    details = f"Performance within target: {avg_time:.4f}s ≤ {test['max_time']}s"
                else:
                    status = "WARN"
                    details = f"Performance exceeded target: {avg_time:.4f}s > {test['max_time']}s"
                
                result = log_test_result(
                    test['name'],
                    status,
                    details,
                    performance
                )
                
                # Show time breakdown
                print(f"   Iteration Times: {[f'{t:.4f}s' for t in times]}")
                print(f"   Context Counts: {contexts}")
                
                results.append(result)
                
            except Exception as e:
                result = log_test_result(
                    test['name'],
                    "FAIL",
                    f"Benchmark test failed: {str(e)}"
                )
                results.append(result)
    
    except Exception as e:
        result = log_test_result(
            "Performance Benchmarks",
            "FAIL",
            f"Failed to initialize federation for benchmarking: {str(e)}"
        )
        results.append(result)
    
    return results

def generate_test_report(all_results):
    """Generate comprehensive test report"""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST REPORT")
    print("="*80)
    
    # Count results by status
    pass_count = sum(1 for r in all_results if r['status'] == 'PASS')
    warn_count = sum(1 for r in all_results if r['status'] == 'WARN')
    fail_count = sum(1 for r in all_results if r['status'] == 'FAIL')
    total_count = len(all_results)
    
    print(f"\nOVERALL RESULTS:")
    print(f"✅ PASS: {pass_count}/{total_count} ({pass_count/total_count*100:.1f}%)")
    print(f"⚠️  WARN: {warn_count}/{total_count} ({warn_count/total_count*100:.1f}%)")
    print(f"❌ FAIL: {fail_count}/{total_count} ({fail_count/total_count*100:.1f}%)")
    
    # Overall assessment
    if fail_count == 0 and warn_count <= 2:
        overall_status = "🚀 REVOLUTIONARY SUCCESS"
    elif fail_count <= 2 and warn_count <= 5:
        overall_status = "✅ OPERATIONAL SUCCESS"
    elif fail_count <= 5:
        overall_status = "⚠️ NEEDS IMPROVEMENT"
    else:
        overall_status = "❌ SYSTEM ISSUES"
    
    print(f"\nOVERALL ASSESSMENT: {overall_status}")
    
    # Failed tests summary
    if fail_count > 0:
        print(f"\nFAILED TESTS:")
        for result in all_results:
            if result['status'] == 'FAIL':
                print(f"❌ {result['test_name']}: {result['details']}")
    
    # Warning tests summary  
    if warn_count > 0:
        print(f"\nWARNING TESTS:")
        for result in all_results:
            if result['status'] == 'WARN':
                print(f"⚠️ {result['test_name']}: {result['details']}")
    
    print(f"\n{'='*80}")
    print(f"RAG FEDERATION SYSTEM COMPREHENSIVE TEST COMPLETE")
    print(f"From 'straw and bubblegum' to {overall_status}")
    print(f"{'='*80}")
    
    return overall_status

def main():
    """Run comprehensive RAG Federation system test"""
    print("RAG FEDERATION COMPREHENSIVE SYSTEM TEST")
    print("From Article Title + 2 Sentences to Revolutionary Technology")
    print("Testing the 'Straw and Bubblegum' System")
    print("="*80)
    
    all_results = []
    
    # Run all test suites
    print("\n🧪 Starting comprehensive test suite...")
    
    # Individual source testing
    individual_results = test_individual_sources()
    all_results.extend(individual_results)
    
    # Federated query testing
    federated_results = test_federated_queries()
    all_results.extend(federated_results)
    
    # Knowledge Graph enhancement testing
    kg_results = test_knowledge_graph_enhancement()
    all_results.extend(kg_results)
    
    # Cross-source intelligence testing
    synthesis_results = test_cross_source_intelligence()
    all_results.extend(synthesis_results)
    
    # Performance benchmark testing
    performance_results = test_performance_benchmarks()
    all_results.extend(performance_results)
    
    # Generate final report
    overall_status = generate_test_report(all_results)
    
    # Save test results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"comprehensive_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'overall_status': overall_status,
            'test_results': all_results
        }, f, indent=2)
    
    print(f"\nTest results saved to: {results_file}")
    
    return overall_status

if __name__ == "__main__":
    main()