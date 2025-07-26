#!/usr/bin/env python3
"""
Simple test script to simulate the modified workflow and verify frontend URL generation
"""

import json
import re
from datetime import datetime

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
        print(f"   Content length: {len(chunk['content'])} chars")
        print()
    
    return enhanced_chunks, frontend_url

def test_url_variations():
    """Test URL generation with various product names"""
    print("🧪 Testing URL Generation with Various Product Names")
    print("=" * 60)
    
    test_cases = [
        ("Inuit Heizhandschuh", "022572-00"),
        ("Manzano Top Sportliche Tourenjacke", "062424-00-069-0-S"),
        ("Kühl Handschuh für Winter", "123456-00"),
        ("Test-Produkt (Special) & More!", "789012-00"),
        ("Ärmel mit Öffnung", "111111-00"),
        ("Größe XL Überzug", "222222-00")
    ]
    
    for product_name, article_number in test_cases:
        url = generate_frontend_url(product_name, article_number)
        print(f"Product: {product_name}")
        print(f"Article: {article_number}")
        print(f"URL: {url}")
        print()

if __name__ == "__main__":
    print("🧪 TESTING WORKFLOW WITH FRONTEND URL INTEGRATION")
    print("=" * 70)
    
    # Test URL generation variations
    test_url_variations()
    
    # Simulate workflow execution
    enhanced_chunks, frontend_url = simulate_workflow()
    
    print(f"📊 WORKFLOW SIMULATION RESULTS:")
    print(f"   ✅ Processed {len(enhanced_chunks)} chunks")
    print(f"   ✅ Generated frontend URL: {frontend_url}")
    print(f"   ✅ Enhanced metadata with {len(enhanced_chunks[0]['metadata'])} fields")
    print()
    
    # Show sample metadata structure
    print("📋 SAMPLE METADATA STRUCTURE:")
    print("=" * 40)
    sample_metadata = enhanced_chunks[0]['metadata']
    for key, value in sample_metadata.items():
        if key == 'frontend_url':
            print(f"   🔗 {key}: {value}")
        elif key in ['shop_base_url', 'url_generated_at']:
            print(f"   🌐 {key}: {value}")
        else:
            print(f"   📝 {key}: {value}")
    
    print("\n🎉 Workflow simulation completed successfully!")
    print("✅ Frontend URLs are now integrated into the product metadata!")