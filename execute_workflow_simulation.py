#!/usr/bin/env python3
"""
Direct execution of the workflow logic to add frontend URLs to Qdrant
"""

import json
import re
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

def generate_frontend_url(product_name, article_number, base_url='https://shop.held.de'):
    """Generate frontend URL from product data"""
    # Convert product name to URL-friendly format
    # Handle German umlauts and special characters
    url_name = product_name
    url_name = url_name.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    url_name = url_name.replace('Ä', 'Ae').replace('Ö', 'Oe').replace('Ü', 'Ue')
    
    # Remove special characters except spaces and hyphens
    url_name = re.sub(r'[^a-zA-Z0-9\s-]', '', url_name)
    # Replace spaces with hyphens
    url_name = re.sub(r'\s+', '-', url_name)
    # Replace multiple hyphens with single hyphen
    url_name = re.sub(r'-+', '-', url_name)
    # Remove leading/trailing hyphens
    url_name = url_name.strip('-')
    
    return f"{base_url}/{url_name}/{article_number}"

def generate_deterministic_point_id(article_number, chunk_index):
    """Generate deterministic Point ID based on article number and chunk index"""
    import hashlib
    id_string = f"{article_number}_{str(chunk_index).zfill(3)}"
    # Use hash to generate a smaller, valid point ID
    hash_obj = hashlib.md5(id_string.encode())
    # Take first 4 bytes and convert to unsigned int, then limit to valid range
    hash_bytes = hash_obj.digest()[:4]
    point_id = int.from_bytes(hash_bytes, byteorder='big') % (2**31 - 1)  # Keep within 32-bit signed int range
    return point_id

def generate_mock_embedding(text, dimensions=3072):
    """Generate deterministic mock embedding based on content"""
    import hashlib
    import struct
    
    # Create a more stable hash
    text_hash = hashlib.md5(text.encode()).hexdigest()
    
    embedding = []
    for i in range(dimensions):
        # Use hash and index to create deterministic seed
        seed_str = f"{text_hash}_{i}"
        seed_hash = hashlib.md5(seed_str.encode()).digest()
        # Convert first 4 bytes to float
        seed_int = struct.unpack('I', seed_hash[:4])[0]
        # Normalize to range [-1, 1]
        value = (seed_int / (2**32 - 1)) * 2 - 1
        embedding.append(float(value))
    
    return embedding

def execute_workflow_simulation():
    """Execute the workflow simulation with frontend URL generation"""
    print("🚀 EXECUTING WORKFLOW SIMULATION WITH FRONTEND URLS")
    print("=" * 60)
    
    # Dataset from the workflow (same as in the n8n workflow)
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
    
    # Connect to Qdrant
    try:
        client = QdrantClient(host='localhost', port=6333)
        print("✅ Connected to Qdrant")
        
        # Delete existing collection and recreate
        print("🔄 Recreating collection with updated data...")
        try:
            client.delete_collection('held_products_optimized')
            print("✅ Deleted existing collection")
        except:
            print("ℹ️ Collection didn't exist, creating new one")
        
        # Create collection
        from qdrant_client.models import VectorParams, Distance
        client.create_collection(
            collection_name='held_products_optimized',
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
        )
        print("✅ Created new collection")
        
        # Process chunks and create points
        points = []
        for index, chunk in enumerate(dataset["optimized_chunks"]):
            # Generate enhanced metadata with frontend URL
            enhanced_metadata = {
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
            }
            
            # Generate embedding and point
            embedding = generate_mock_embedding(chunk["content"])
            point_id = generate_deterministic_point_id(article_number, index)
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "chunk_id": chunk["chunk_id"],
                    "content": chunk["content"],
                    "metadata": enhanced_metadata
                }
            )
            
            points.append(point)
            print(f"✅ Prepared point {index + 1}: {chunk['chunk_id']}")
            print(f"   Frontend URL: {frontend_url}")
            print(f"   Point ID: {point_id}")
        
        # Upsert points to Qdrant
        print(f"\n🔄 Uploading {len(points)} points to Qdrant...")
        client.upsert(
            collection_name='held_products_optimized',
            points=points
        )
        print("✅ Successfully uploaded all points!")
        
        return True, frontend_url, len(points)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None, 0

def verify_frontend_urls():
    """Verify that frontend URLs are correctly stored in Qdrant"""
    print("\n🔍 VERIFYING FRONTEND URLS IN QDRANT")
    print("=" * 40)
    
    try:
        client = QdrantClient(host='localhost', port=6333)
        
        # Get collection info
        collection_info = client.get_collection('held_products_optimized')
        print(f"Collection: held_products_optimized")
        print(f"Points count: {collection_info.points_count}")
        print(f"Vector size: {collection_info.config.params.vectors.size}")
        print()
        
        # Get sample points to verify frontend URLs
        points = client.scroll(
            collection_name='held_products_optimized',
            limit=3,
            with_payload=True,
            with_vectors=False
        )
        
        frontend_urls_found = 0
        for i, point in enumerate(points[0]):
            metadata = point.payload.get('metadata', {})
            frontend_url = metadata.get('frontend_url')
            
            print(f"--- Point {i + 1} ---")
            print(f"ID: {point.id}")
            print(f"Chunk ID: {point.payload.get('chunk_id', 'N/A')}")
            print(f"Article Number: {metadata.get('article_number', 'MISSING')}")
            
            if frontend_url:
                print(f"✅ Frontend URL: {frontend_url}")
                print(f"✅ Shop Base URL: {metadata.get('shop_base_url', 'MISSING')}")
                print(f"✅ URL Generated At: {metadata.get('url_generated_at', 'MISSING')}")
                print(f"✅ Workflow Version: {metadata.get('workflow_version', 'MISSING')}")
                frontend_urls_found += 1
            else:
                print("❌ Frontend URL: MISSING")
            print()
        
        print(f"📊 VERIFICATION RESULTS:")
        print(f"   Total points: {collection_info.points_count}")
        print(f"   Points with frontend URLs: {frontend_urls_found}")
        print(f"   Success rate: {frontend_urls_found}/{len(points[0])} = {(frontend_urls_found/len(points[0])*100):.1f}%")
        
        return frontend_urls_found == len(points[0])
        
    except Exception as e:
        print(f"❌ Error verifying: {e}")
        return False

def main():
    print("🧪 WORKFLOW SIMULATION: ADDING FRONTEND URLS TO QDRANT")
    print("=" * 70)
    
    # Execute workflow simulation
    success, frontend_url, point_count = execute_workflow_simulation()
    
    if success:
        print(f"\n🎉 WORKFLOW EXECUTION COMPLETED!")
        print(f"   ✅ Generated frontend URL: {frontend_url}")
        print(f"   ✅ Processed {point_count} chunks")
        print(f"   ✅ Updated Qdrant collection: held_products_optimized")
        
        # Verify the results
        verification_success = verify_frontend_urls()
        
        if verification_success:
            print("\n🎉 VERIFICATION SUCCESSFUL!")
            print("✅ All points now contain frontend URLs!")
        else:
            print("\n⚠️ VERIFICATION ISSUES DETECTED")
            print("Some points may be missing frontend URLs")
    else:
        print("\n❌ WORKFLOW EXECUTION FAILED")
        print("Check the error messages above")

if __name__ == "__main__":
    main()