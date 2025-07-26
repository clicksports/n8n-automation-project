#!/usr/bin/env python3
"""
Test script for HELD Inuit Heizhandschuh vectorization workflow
"""

import json
import time
import sys
from vectorization_workflow import VectorizationWorkflow

def test_qdrant_connection():
    """Test Qdrant connection"""
    print("🔍 Testing Qdrant connection...")
    try:
        workflow = VectorizationWorkflow()
        if workflow.qdrant_client:
            collections = workflow.qdrant_client.get_collections()
            print(f"✅ Connected to Qdrant. Found {len(collections.collections)} collections.")
            return True
        else:
            print("❌ Failed to connect to Qdrant")
            return False
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return False

def test_dataset_loading():
    """Test dataset loading"""
    print("\n📁 Testing dataset loading...")
    try:
        workflow = VectorizationWorkflow()
        chunks = workflow.load_optimized_dataset()
        if chunks:
            print(f"✅ Successfully loaded {len(chunks)} chunks")
            print(f"   Sample chunk: {chunks[0].chunk_id}")
            return True
        else:
            print("❌ Failed to load dataset")
            return False
    except Exception as e:
        print(f"❌ Dataset loading failed: {e}")
        return False

def test_embedding_generation():
    """Test embedding generation"""
    print("\n🧠 Testing embedding generation...")
    try:
        workflow = VectorizationWorkflow()
        test_text = "HELD Inuit Heizhandschuh - beheizter Motorradhandschuh"
        embedding = workflow.generate_embedding(test_text)
        if embedding and len(embedding) == 3072:
            print(f"✅ Generated embedding with {len(embedding)} dimensions")
            return True
        else:
            print(f"❌ Invalid embedding: {len(embedding) if embedding else 0} dimensions")
            return False
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        return False

def run_complete_test():
    """Run the complete workflow test"""
    print("\n🚀 Running complete vectorization workflow...")
    print("=" * 60)
    
    try:
        workflow = VectorizationWorkflow()
        results = workflow.run_complete_workflow()
        
        print("\n📊 Workflow Results:")
        print("-" * 30)
        
        # Print step results
        for step_name, step_result in results.get("steps", {}).items():
            status = "✅" if step_result.get("success") else "❌"
            print(f"{status} {step_name.replace('_', ' ').title()}")
            
            # Print additional details
            for key, value in step_result.items():
                if key != "success":
                    print(f"   {key}: {value}")
        
        # Print collection info
        if "collection_info" in results:
            print(f"\n📈 Collection Info:")
            for key, value in results["collection_info"].items():
                print(f"   {key}: {value}")
        
        # Print search test results
        if "steps" in results and "test_search" in results["steps"]:
            search_results = results["steps"]["test_search"].get("search_results", {})
            if search_results:
                print(f"\n🔍 Search Test Results:")
                for query, results_list in search_results.items():
                    print(f"\n   Query: '{query}'")
                    for i, result in enumerate(results_list[:2]):  # Show top 2 results
                        print(f"   {i+1}. Score: {result['score']:.3f}")
                        print(f"      Chunk: {result['chunk_id']}")
                        print(f"      Content: {result['content'][:100]}...")
        
        return results.get("success", False)
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        return False

def interactive_search_test():
    """Interactive search testing"""
    print("\n🔍 Interactive Search Test")
    print("=" * 30)
    print("Enter search queries to test the vectorized knowledge base.")
    print("Type 'quit' to exit.\n")
    
    workflow = VectorizationWorkflow()
    
    while True:
        try:
            query = input("Search query: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            print(f"\nSearching for: '{query}'")
            results = workflow.test_search(query, limit=3)
            
            if results:
                print(f"Found {len(results)} results:\n")
                for i, result in enumerate(results, 1):
                    print(f"{i}. Score: {result['score']:.3f}")
                    print(f"   Chunk: {result['chunk_id']}")
                    print(f"   Category: {result['metadata'].get('content_category', 'N/A')}")
                    print(f"   Content: {result['content']}")
                    print()
            else:
                print("No results found.\n")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Search error: {e}\n")
    
    print("Search test completed.")

def main():
    """Main test function"""
    print("HELD Inuit Heizhandschuh Vectorization Test Suite")
    print("=" * 55)
    
    # Run individual tests
    tests = [
        ("Qdrant Connection", test_qdrant_connection),
        ("Dataset Loading", test_dataset_loading),
        ("Embedding Generation", test_embedding_generation)
    ]
    
    passed_tests = 0
    for test_name, test_func in tests:
        if test_func():
            passed_tests += 1
    
    print(f"\n📋 Individual Tests: {passed_tests}/{len(tests)} passed")
    
    if passed_tests == len(tests):
        print("\n🎯 All individual tests passed! Running complete workflow...")
        
        # Run complete workflow
        if run_complete_test():
            print("\n🎉 All tests passed! Vectorization workflow is working correctly.")
            
            # Ask for interactive testing
            response = input("\nWould you like to run interactive search tests? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                interactive_search_test()
        else:
            print("\n❌ Complete workflow test failed.")
            sys.exit(1)
    else:
        print(f"\n❌ {len(tests) - passed_tests} tests failed. Please check the setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()