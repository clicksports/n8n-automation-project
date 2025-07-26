#!/usr/bin/env python3
"""
Simple test script for HELD vectorization workflow without external dependencies
"""

import json
import hashlib
import sys

def test_dataset_loading():
    """Test loading the optimized dataset"""
    print("📁 Testing dataset loading...")
    try:
        with open('optimized_dataset_format.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = data.get('optimized_chunks', [])
        metadata = data.get('dataset_metadata', {})
        
        print(f"✅ Dataset loaded successfully")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Product: {metadata.get('product_name', 'Unknown')}")
        print(f"   Version: {metadata.get('version', 'Unknown')}")
        
        # Validate chunk structure
        required_fields = ['chunk_id', 'content', 'metadata']
        valid_chunks = 0
        
        for chunk in chunks:
            if all(field in chunk for field in required_fields):
                valid_chunks += 1
        
        print(f"   Valid chunks: {valid_chunks}/{len(chunks)}")
        
        # Show sample chunk
        if chunks:
            sample = chunks[0]
            print(f"\n📋 Sample chunk:")
            print(f"   ID: {sample['chunk_id']}")
            print(f"   Content length: {len(sample['content'])} chars")
            print(f"   Content preview: {sample['content'][:100]}...")
            print(f"   Metadata keys: {list(sample['metadata'].keys())}")
        
        return len(chunks) > 0 and valid_chunks == len(chunks)
        
    except Exception as e:
        print(f"❌ Dataset loading failed: {e}")
        return False

def test_mock_embedding():
    """Test mock embedding generation"""
    print("\n🧠 Testing mock embedding generation...")
    try:
        # Simple deterministic embedding generation
        def generate_mock_embedding(text, dimensions=3072):
            # Use MD5 hash as seed for reproducible results
            hash_obj = hashlib.md5(text.encode())
            seed_hex = hash_obj.hexdigest()
            
            # Convert hex to numbers and normalize
            embedding = []
            for i in range(dimensions):
                # Use different parts of the hash for variety
                hex_part = seed_hex[(i * 2) % len(seed_hex):((i * 2) + 2) % len(seed_hex)]
                if len(hex_part) < 2:
                    hex_part = seed_hex[:2]
                
                # Convert to float between -1 and 1
                value = (int(hex_part, 16) / 255.0) * 2 - 1
                embedding.append(value)
            
            return embedding
        
        # Test with sample text
        test_text = "HELD Inuit Heizhandschuh - beheizter Motorradhandschuh"
        embedding = generate_mock_embedding(test_text)
        
        print(f"✅ Mock embedding generated")
        print(f"   Dimensions: {len(embedding)}")
        print(f"   Sample values: {embedding[:5]}")
        print(f"   Value range: {min(embedding):.3f} to {max(embedding):.3f}")
        
        return len(embedding) == 3072
        
    except Exception as e:
        print(f"❌ Mock embedding generation failed: {e}")
        return False

def test_chunk_analysis():
    """Analyze the chunks for completeness"""
    print("\n📊 Analyzing chunk coverage...")
    try:
        with open('optimized_dataset_format.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = data.get('optimized_chunks', [])
        
        # Analyze chunk types
        chunk_types = {}
        content_categories = {}
        customer_intents = set()
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            
            # Count chunk types
            chunk_type = metadata.get('chunk_type', 'unknown')
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
            
            # Count content categories
            category = metadata.get('content_category', 'unknown')
            content_categories[category] = content_categories.get(category, 0) + 1
            
            # Collect customer intents
            intents = metadata.get('customer_intents', [])
            customer_intents.update(intents)
        
        print(f"✅ Chunk analysis completed")
        print(f"\n📈 Chunk Types:")
        for chunk_type, count in chunk_types.items():
            print(f"   {chunk_type}: {count}")
        
        print(f"\n📂 Content Categories:")
        for category, count in content_categories.items():
            print(f"   {category}: {count}")
        
        print(f"\n🎯 Customer Intents ({len(customer_intents)} unique):")
        for intent in sorted(customer_intents):
            print(f"   - {intent}")
        
        # Check coverage
        expected_types = ['product_overview', 'technical_specifications', 'usage_scenarios', 'customer_service']
        coverage = sum(1 for t in expected_types if t in chunk_types) / len(expected_types)
        
        print(f"\n📋 Coverage Analysis:")
        print(f"   Chunk type coverage: {coverage:.1%}")
        print(f"   Total content categories: {len(content_categories)}")
        print(f"   Total customer intents: {len(customer_intents)}")
        
        return coverage >= 0.75  # At least 75% coverage
        
    except Exception as e:
        print(f"❌ Chunk analysis failed: {e}")
        return False

def test_search_simulation():
    """Simulate search functionality"""
    print("\n🔍 Simulating search functionality...")
    try:
        with open('optimized_dataset_format.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = data.get('optimized_chunks', [])
        
        # Test queries
        test_queries = [
            "Akku Laufzeit",
            "Größe Handschuh",
            "wasserdicht",
            "Preis",
            "Smartphone Touch"
        ]
        
        print(f"✅ Testing {len(test_queries)} search queries")
        
        for query in test_queries:
            print(f"\n🔎 Query: '{query}'")
            
            # Simple keyword matching simulation
            matches = []
            for chunk in chunks:
                content = chunk['content'].lower()
                query_lower = query.lower()
                
                # Count keyword matches
                score = 0
                for word in query_lower.split():
                    if word in content:
                        score += content.count(word)
                
                if score > 0:
                    matches.append({
                        'chunk_id': chunk['chunk_id'],
                        'score': score,
                        'content_preview': chunk['content'][:100] + "..."
                    })
            
            # Sort by score
            matches.sort(key=lambda x: x['score'], reverse=True)
            
            print(f"   Found {len(matches)} matches")
            for i, match in enumerate(matches[:2]):  # Show top 2
                print(f"   {i+1}. {match['chunk_id']} (score: {match['score']})")
                print(f"      {match['content_preview']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search simulation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("HELD Inuit Heizhandschuh - Simple Vectorization Test")
    print("=" * 55)
    
    tests = [
        ("Dataset Loading", test_dataset_loading),
        ("Mock Embedding", test_mock_embedding),
        ("Chunk Analysis", test_chunk_analysis),
        ("Search Simulation", test_search_simulation)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n{'='*55}")
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The vectorization dataset is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start Qdrant: docker-compose -f docker-compose-qdrant.yml up -d")
        print("3. Run full workflow: python3 vectorization_workflow.py")
    else:
        print("❌ Some tests failed. Please check the dataset and configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()