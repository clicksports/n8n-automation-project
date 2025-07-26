#!/usr/bin/env python3
"""
Test script to simulate the modified workflow and verify frontend URL generation
"""

import json
import requests
import time
from datetime import datetime

def generate_frontend_url(product_name, article_number, base_url='https://shop.held.de'):
    """Generate frontend URL from product data"""
    # Convert product name to URL-friendly format
    # Handle German umlauts and special characters
    url_name = product_name
    url_name = url_name.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    url_name = url_name.replace('Ä', 'Ae').replace('Ö', 'Oe').replace('Ü', 'Ue')
    
    # Remove special characters except spaces and hyphens
    import re
    url_name = re.sub(r'[^a-zA-Z0-9\s-]', '', url_name)
    # Replace spaces with hyphens
    url_name = re.sub(r'\s+', '-', url_name)
    # Replace multiple hyphens with single hyphen
    url_name = re.sub(r'-+', '-', url_name)
    # Remove leading/trailing hyphens
    url_name = url_name.strip('-')
    
    return f"{base_url}/{url_name}/{article_number}"

def simulate_workflow():
    """Simulate the modified workflow execution"""
    print("🚀 Simulating Shopware Optimized Vectorization Workflow with Frontend URLs")
    print("=" * 70)
    
    # Dataset from the workflow
    dataset = {
        "dataset_metadata": {
            "version": "1.0",
            "created": "2025-01-26",
            "product_id": "022572-00",
            "product_name": "Inuit Heizhandschuh",
            "language": "de",
            "total_chunks": 3,
            "embedding_model": "text-embedding-3-large",
            "chunk_strategy": "semantic_overlap"
        },
        "optimized_chunks": [
            {
                "chunk_id": "inuit_001_overview",
                "content": "HELD Inuit Heizhandschuh (Art. 022572-00) - Premium beheizter Motorradhandschuh für extreme Winterbedingungen. Preis: 249,95 €. Aktuell nicht verfügbar. Kategorie: Touring-Handschuhe mit Membrane. Verfügbare Größen: 7, 8, 9, 10, 11, 12 (Standardgrößen). Farbe: schwarz. Hochwertige Verarbeitung mit 7,4V 3000 mAh Batteriesystem für zuverlässige Wärmeleistung.",
                "metadata": {
                    "chunk_type": "product_overview",
                    "content_category": "basic_info",
                    "keywords": ["Preis", "Verfügbarkeit", "Größen", "Farbe", "Heizhandschuh"],
                    "customer_intents": ["product_inquiry", "price_check", "availability", "sizing"],
                    "confidence_score": 0.95,
                    "seasonal_relevance": "winter",
                    "technical_level": "basic"
                }
            },
            {
                "chunk_id": "inuit_002_heating_system",
                "content": "Heizsystem: 7,4V 3000 mAh Lithium-Akku mit drei Heizstufen. TURBO (-70°C): Finger 2,5h, Handschuh 4,5h, Kombination 1,5h. HIGH (-50°C): Finger 4,0h, Handschuh 7,5h, Kombination 2,5h. LOW (-30°C): Finger 7,5h, Handschuh 11,0h, Kombination 4,0h. Separate Heizzonen für Finger und Handschuh steuerbar. Ladegerät inklusive.",
                "metadata": {
                    "chunk_type": "technical_specifications",
                    "content_category": "heating_performance",
                    "keywords": ["Akku", "Heizstufen", "Laufzeit", "Temperatur", "Heizzonen"],
                    "customer_intents": ["battery_life", "heating_performance", "temperature_range"],
                    "confidence_score": 0.98,
                    "technical_level": "detailed"
                }
            },
            {
                "chunk_id": "inuit_003_materials",
                "content": "Materialien: Oberhand aus hochwertigem Stretchgewebe für Flexibilität. Handfläche aus robustem Ziegenleder (farbecht und schweißbeständig). Futter: Oberhand mit Thermoplush Fleece und PRIMALOFT® Isolierung, Handfläche mit 3M™-Thinsulate™ Wärmefutter. Leder/Textil-Mix für optimale Balance zwischen Schutz und Komfort.",
                "metadata": {
                    "chunk_type": "technical_specifications",
                    "content_category": "materials",
                    "keywords": ["Stretchgewebe", "Ziegenleder", "PRIMALOFT", "Thinsulate", "Materialien"],
                    "customer_intents": ["material_questions", "quality_inquiry", "durability"],
                    "confidence_score": 0.96,
                    "technical_level": "detailed"
                }
            }
        ]
    }
    
    article_number = dataset["dataset_metadata"]["product_id"]
    product_name = dataset["dataset_metadata"]["product_name"]
    
    print(f"📦 Product: {product_name}")
    print(f"🔢 Article Number: {article_number}")
    
    # Generate frontend URL
    frontend_url = generate_frontend_url(product_name, article_number)
    print(f"🔗 Generated Frontend URL: {frontend_url}")
    print()
    
    # Process chunks with enhanced metadata including frontend URL
    enhanced_chunks = []
    for index, chunk in enumerate(dataset["optimized_chunks"]):
        enhanced_chunk = {
            "chunk_id": chunk["chunk_id"],
            "content": chunk["content"],
            "metadata": {
                **chunk["metadata"],
                # Shopware Integration Fields
                "article_number": article_number,
                "shopware_product_id": f"sw_{article_number}",
                "shopware_variant_id": f"sw_var_{article_number}_{str(index).zfill(3)}",
                "last_updated": datetime.now().isoformat(),
                "content_version": "2.0",
                "chunk_index": index,
                
                # Frontend URL Integration
                "frontend_url": frontend_url,
                "shop_base_url": "https://shop.held.de",
                "url_generated_at": datetime.now().isoformat(),
                
                # Product Hierarchy
                "brand": "HELD",
                "category_path": "Handschuhe > Touring-Handschuhe > mit Membrane",
                "product_line": "Inuit",
                
                # Update Tracking
                "source_system": "shopware",
                "sync_status": "active",
                "price_currency": "EUR",
                "stock_status": "available",
                
                # Processing metadata
                "processed_at": datetime.now().isoformat(),
                "content_length": len(chunk["content"]),
                "embedding_model": "text-embedding-3-large",
                "workflow_version": "2.1_shopware_optimized_with_frontend_url"
            },
            "article_number": article_number,
            "chunk_index": index,
            "frontend_url": frontend_url
        }
        enhanced_chunks.append(enhanced_chunk)
        
        print(f"✅ Enhanced chunk {index + 1}: {chunk['chunk_id']}")
        print(f"   Frontend URL: {frontend_url}")
        print(f"   Metadata keys: {len(enhanced_chunk['metadata'])}")
        print()
    
    return enhanced_chunks, frontend_url

def verify_qdrant_integration():
    """Verify that Qdrant can store and retrieve the frontend URL metadata"""
    print("🔍 Verifying Qdrant Integration...")
    print("=" * 50)
    
    try:
        # Check if Qdrant is running
        response = requests.get("http://localhost:6333/collections")
        if response.status_code == 200:
            print("✅ Qdrant is running and accessible")
            
            # Check if our collection exists
            collections = response.json()["result"]["collections"]
            collection_names = [col["name"] for col in collections]
            
            if "held_products_optimized" in collection_names:
                print("✅ Collection 'held_products_optimized' exists")
                
                # Get sample points to check for frontend_url
                scroll_response = requests.post(
                    "http://localhost:6333/collections/held_products_optimized/points/scroll",
                    json={"limit": 2, "with_payload": True, "with_vector": False}
                )
                
                if scroll_response.status_code == 200:
                    points = scroll_response.json()["result"]["points"]
                    
                    if points:
                        print(f"✅ Found {len(points)} sample points")
                        
                        for i, point in enumerate(points):
                            metadata = point["payload"].get("metadata", {})
                            frontend_url = metadata.get("frontend_url")
                            
                            print(f"\n--- Point {i + 1} ---")
                            print(f"ID: {point['id']}")
                            print(f"Chunk ID: {point['payload'].get('chunk_id', 'N/A')}")
                            print(f"Article Number: {metadata.get('article_number', 'MISSING')}")
                            
                            if frontend_url:
                                print(f"✅ Frontend URL: {frontend_url}")
                            else:
                                print("❌ Frontend URL: MISSING")
                                
                            print(f"Shop Base URL: {metadata.get('shop_base_url', 'MISSING')}")
                            print(f"URL Generated At: {metadata.get('url_generated_at', 'MISSING')}")
                    else:
                        print("⚠️ No points found in collection")
                else:
                    print(f"❌ Failed to scroll points: {scroll_response.status_code}")
            else:
                print("⚠️ Collection 'held_products_optimized' does not exist")
                print(f"Available collections: {collection_names}")
        else:
            print(f"❌ Qdrant not accessible: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Qdrant. Make sure it's running on localhost:6333")
    except Exception as e:
        print(f"❌ Error checking Qdrant: {e}")

if __name__ == "__main__":
    print("🧪 TESTING WORKFLOW WITH FRONTEND URL INTEGRATION")
    print("=" * 70)
    
    # Simulate workflow execution
    enhanced_chunks, frontend_url = simulate_workflow()
    
    print(f"📊 WORKFLOW SIMULATION RESULTS:")
    print(f"   ✅ Processed {len(enhanced_chunks)} chunks")
    print(f"   ✅ Generated frontend URL: {frontend_url}")
    print(f"   ✅ Enhanced metadata with {len(enhanced_chunks[0]['metadata'])} fields")
    print()
    
    # Verify Qdrant integration
    verify_qdrant_integration()
    
    print("\n🎉 Test completed!")