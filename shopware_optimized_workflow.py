#!/usr/bin/env python3
"""
Shopware-Optimized HELD Product Vectorization Workflow
Enhanced with proper upsert functionality and article number tracking
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib

# Third-party imports
try:
    import openai
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, FilterSelector, PayloadSchemaType
    import numpy as np
except ImportError as e:
    print(f"Missing required packages. Install with: pip install openai qdrant-client numpy")
    print(f"Error: {e}")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ShopwareChunkData:
    """Enhanced data structure for Shopware-optimized chunks"""
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    article_number: str
    chunk_index: int
    embedding: Optional[List[float]] = None

class ShopwareOptimizedWorkflow:
    """Shopware-optimized workflow class for vectorizing HELD product data"""
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 qdrant_url: str = "localhost",
                 qdrant_port: int = 6333,
                 collection_name: str = "held_products_optimized"):
        """
        Initialize the Shopware-optimized vectorization workflow
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.qdrant_url = qdrant_url
        self.qdrant_port = qdrant_port
        self.collection_name = collection_name
        
        # Initialize OpenAI client
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            logger.warning("No OpenAI API key provided. Using mock embeddings for testing.")
        
        # Initialize Qdrant client
        try:
            self.qdrant_client = QdrantClient(host=qdrant_url, port=qdrant_port)
            logger.info(f"Connected to Qdrant at {qdrant_url}:{qdrant_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            self.qdrant_client = None
    
    def load_and_enhance_dataset(self, file_path: str = "optimized_dataset_format.json") -> List[ShopwareChunkData]:
        """Load dataset and enhance with Shopware-specific metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract article number from dataset metadata
            article_number = data.get('dataset_metadata', {}).get('product_id', 'unknown')
            logger.info(f"Processing product: {article_number}")
            
            chunks = []
            for i, chunk_data in enumerate(data.get('optimized_chunks', [])):
                # Enhanced metadata with Shopware fields
                enhanced_metadata = chunk_data['metadata'].copy()
                enhanced_metadata.update({
                    # Shopware Integration Fields
                    'article_number': article_number,
                    'shopware_product_id': f"sw_{article_number}",
                    'shopware_variant_id': f"sw_var_{article_number}_{i:03d}",
                    'last_updated': datetime.now().isoformat(),
                    'content_version': '2.0',
                    'chunk_index': i,
                    
                    # Product Hierarchy
                    'brand': 'HELD',
                    'category_path': 'Handschuhe > Touring-Handschuhe > mit Membrane',
                    'product_line': 'Inuit',
                    
                    # Update Tracking
                    'source_system': 'shopware',
                    'sync_status': 'active',
                    'price_currency': 'EUR',
                    'stock_status': 'available',
                    
                    # Processing metadata
                    'processed_at': datetime.now().isoformat(),
                    'content_length': len(chunk_data['content']),
                    'embedding_model': 'text-embedding-3-large',
                    'workflow_version': '2.0_shopware_optimized'
                })
                
                chunk = ShopwareChunkData(
                    chunk_id=chunk_data['chunk_id'],
                    content=chunk_data['content'],
                    metadata=enhanced_metadata,
                    article_number=article_number,
                    chunk_index=i
                )
                chunks.append(chunk)
            
            logger.info(f"Enhanced {len(chunks)} chunks with Shopware metadata")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to load and enhance dataset: {e}")
            return []
    
    def generate_deterministic_point_id(self, article_number: str, chunk_index: int) -> int:
        """Generate deterministic Point ID based on article number and chunk index"""
        # Create deterministic ID that will be consistent across updates
        id_string = f"{article_number}_{chunk_index:03d}"
        return hash(id_string) % (2**63)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI API"""
        if not self.openai_api_key:
            # Generate deterministic mock embedding for testing
            hash_obj = hashlib.md5(text.encode())
            seed = int(hash_obj.hexdigest()[:8], 16)
            np.random.seed(seed)
            return np.random.normal(0, 1, 3072).tolist()
        
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-large",
                input=text,
                dimensions=3072
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return []
    
    def create_optimized_collection(self, vector_size: int = 3072) -> bool:
        """Create Qdrant collection with Shopware-optimized settings"""
        if not self.qdrant_client:
            logger.error("Qdrant client not available")
            return False
        
        try:
            # Check if collection exists and delete it for fresh start
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name in collection_names:
                logger.info(f"Deleting existing collection '{self.collection_name}'")
                self.qdrant_client.delete_collection(self.collection_name)
            
            # Create collection with optimized settings
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            
            # Create payload indexes for efficient Shopware queries
            indexes_to_create = [
                'metadata.article_number',      # Critical for upsert operations
                'metadata.shopware_product_id',
                'metadata.brand',
                'metadata.category_path',
                'metadata.last_updated',
                'metadata.chunk_type',
                'metadata.source_system',
                'metadata.sync_status'
            ]
            
            for field_name in indexes_to_create:
                try:
                    self.qdrant_client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=field_name,
                        field_schema=PayloadSchemaType.KEYWORD
                    )
                    logger.info(f"Created index for {field_name}")
                except Exception as e:
                    logger.warning(f"Failed to create index for {field_name}: {e}")
            
            logger.info(f"Created optimized collection '{self.collection_name}' with indexes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False
    
    def vectorize_chunks(self, chunks: List[ShopwareChunkData]) -> List[ShopwareChunkData]:
        """Generate embeddings for all chunks"""
        logger.info("Starting vectorization process...")
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Vectorizing chunk {i+1}/{len(chunks)}: {chunk.chunk_id}")
            
            # Generate embedding
            embedding = self.generate_embedding(chunk.content)
            if embedding:
                chunk.embedding = embedding
            else:
                logger.warning(f"Failed to generate embedding for chunk {chunk.chunk_id}")
        
        successful_chunks = [chunk for chunk in chunks if chunk.embedding]
        logger.info(f"Successfully vectorized {len(successful_chunks)}/{len(chunks)} chunks")
        
        return successful_chunks
    
    def upsert_product_data(self, article_number: str, chunks: List[ShopwareChunkData]) -> bool:
        """
        Upsert product data with proper Shopware integration
        This method ensures that existing product data is replaced, not duplicated
        """
        if not self.qdrant_client:
            logger.error("Qdrant client not available")
            return False
        
        if not chunks:
            logger.error("No chunks to upsert")
            return False
        
        try:
            logger.info(f"Starting upsert for article {article_number}")
            
            # Step 1: Delete existing product data
            logger.info(f"Deleting existing data for article {article_number}")
            delete_result = self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=FilterSelector(
                    filter=Filter(
                        must=[
                            FieldCondition(
                                key="metadata.article_number",
                                match=MatchValue(value=article_number)
                            )
                        ]
                    )
                )
            )
            logger.info(f"Deleted existing points: {delete_result}")
            
            # Step 2: Prepare new points with deterministic IDs
            points = []
            for chunk in chunks:
                if not chunk.embedding:
                    continue
                
                # Generate deterministic Point ID
                point_id = self.generate_deterministic_point_id(chunk.article_number, chunk.chunk_index)
                
                point = PointStruct(
                    id=point_id,
                    vector=chunk.embedding,
                    payload={
                        'chunk_id': chunk.chunk_id,
                        'content': chunk.content,
                        'metadata': chunk.metadata
                    }
                )
                points.append(point)
                logger.debug(f"Prepared point {point_id} for chunk {chunk.chunk_id}")
            
            # Step 3: Upsert new data
            logger.info(f"Upserting {len(points)} points for article {article_number}")
            upsert_result = self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Successfully upserted {len(points)} points for article {article_number}")
            logger.info(f"Upsert result: {upsert_result}")
            return True
            
        except Exception as e:
            logger.error(f"Upsert failed for {article_number}: {e}")
            return False
    
    def test_upsert_functionality(self, article_number: str) -> Dict[str, Any]:
        """Test upsert functionality by performing multiple updates"""
        logger.info(f"Testing upsert functionality for article {article_number}")
        
        results = {
            "test_started": datetime.now().isoformat(),
            "article_number": article_number,
            "tests": {}
        }
        
        try:
            # Test 1: Check initial state
            initial_count = self.get_product_point_count(article_number)
            results["tests"]["initial_count"] = {
                "success": True,
                "count": initial_count
            }
            
            # Test 2: Simulate first update
            logger.info("Simulating first product update...")
            chunks = self.load_and_enhance_dataset()
            if chunks:
                # Modify content to simulate update
                for chunk in chunks:
                    chunk.content += " [UPDATED_V1]"
                    chunk.metadata['content_version'] = '2.1'
                    chunk.metadata['last_updated'] = datetime.now().isoformat()
                
                vectorized_chunks = self.vectorize_chunks(chunks)
                upsert_success = self.upsert_product_data(article_number, vectorized_chunks)
                
                count_after_first = self.get_product_point_count(article_number)
                results["tests"]["first_update"] = {
                    "success": upsert_success,
                    "count_after": count_after_first,
                    "points_changed": count_after_first != initial_count
                }
            
            # Test 3: Simulate second update (should replace, not add)
            logger.info("Simulating second product update...")
            if chunks:
                # Modify content again
                for chunk in chunks:
                    chunk.content = chunk.content.replace("[UPDATED_V1]", "[UPDATED_V2]")
                    chunk.metadata['content_version'] = '2.2'
                    chunk.metadata['last_updated'] = datetime.now().isoformat()
                
                vectorized_chunks = self.vectorize_chunks(chunks)
                upsert_success = self.upsert_product_data(article_number, vectorized_chunks)
                
                count_after_second = self.get_product_point_count(article_number)
                results["tests"]["second_update"] = {
                    "success": upsert_success,
                    "count_after": count_after_second,
                    "count_stable": count_after_second == count_after_first,
                    "no_duplicates": True if count_after_second == len(chunks) else False
                }
            
            # Test 4: Verify content was actually updated
            sample_point = self.get_sample_product_point(article_number)
            if sample_point:
                content_updated = "[UPDATED_V2]" in sample_point.get('content', '')
                version_updated = sample_point.get('metadata', {}).get('content_version') == '2.2'
                
                results["tests"]["content_verification"] = {
                    "success": content_updated and version_updated,
                    "content_updated": content_updated,
                    "version_updated": version_updated,
                    "sample_version": sample_point.get('metadata', {}).get('content_version')
                }
            
            results["test_completed"] = datetime.now().isoformat()
            results["overall_success"] = all(test.get("success", False) for test in results["tests"].values())
            
        except Exception as e:
            logger.error(f"Upsert test failed: {e}")
            results["error"] = str(e)
            results["overall_success"] = False
        
        return results
    
    def get_product_point_count(self, article_number: str) -> int:
        """Get count of points for a specific article number"""
        try:
            result = self.qdrant_client.count(
                collection_name=self.collection_name,
                count_filter=Filter(
                    must=[
                        FieldCondition(
                            key="metadata.article_number",
                            match=MatchValue(value=article_number)
                        )
                    ]
                )
            )
            return result.count
        except Exception as e:
            logger.error(f"Failed to count points for {article_number}: {e}")
            return 0
    
    def get_sample_product_point(self, article_number: str) -> Optional[Dict[str, Any]]:
        """Get a sample point for the specified article number"""
        try:
            result = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="metadata.article_number",
                            match=MatchValue(value=article_number)
                        )
                    ]
                ),
                limit=1,
                with_payload=True,
                with_vectors=False
            )
            
            if result[0]:
                return result[0][0].payload
            return None
            
        except Exception as e:
            logger.error(f"Failed to get sample point for {article_number}: {e}")
            return None
    
    def test_search_functionality(self, article_number: str) -> Dict[str, Any]:
        """Test search functionality with article number filtering"""
        test_queries = [
            "Wie lange hält der Akku?",
            "Welche Größen gibt es?", 
            "Ist der Handschuh wasserdicht?",
            "Preis des Handschuhs"
        ]
        
        results = {}
        for query in test_queries:
            try:
                # Generate query embedding
                query_embedding = self.generate_embedding(query)
                if not query_embedding:
                    continue
                
                # Search with article number filter
                search_results = self.qdrant_client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    query_filter=Filter(
                        must=[
                            FieldCondition(
                                key="metadata.article_number",
                                match=MatchValue(value=article_number)
                            )
                        ]
                    ),
                    limit=2,
                    with_payload=True
                )
                
                results[query] = [
                    {
                        'score': result.score,
                        'chunk_id': result.payload['chunk_id'],
                        'article_number': result.payload['metadata']['article_number'],
                        'content_preview': result.payload['content'][:100] + "..."
                    }
                    for result in search_results
                ]
                
            except Exception as e:
                logger.error(f"Search failed for query '{query}': {e}")
                results[query] = []
        
        return results
    
    def run_complete_shopware_workflow(self) -> Dict[str, Any]:
        """Run the complete Shopware-optimized vectorization workflow"""
        logger.info("Starting complete Shopware-optimized vectorization workflow...")
        
        results = {
            "workflow_started": datetime.now().isoformat(),
            "workflow_version": "2.0_shopware_optimized",
            "steps": {},
            "success": False
        }
        
        # Step 1: Load and enhance dataset
        logger.info("Step 1: Loading and enhancing dataset with Shopware metadata...")
        chunks = self.load_and_enhance_dataset()
        article_number = chunks[0].article_number if chunks else "unknown"
        
        results["article_number"] = article_number
        results["steps"]["load_dataset"] = {
            "success": len(chunks) > 0,
            "chunks_loaded": len(chunks),
            "article_number": article_number
        }
        
        if not chunks:
            results["error"] = "Failed to load dataset"
            return results
        
        # Step 2: Create optimized Qdrant collection
        logger.info("Step 2: Creating Shopware-optimized Qdrant collection...")
        collection_created = self.create_optimized_collection()
        results["steps"]["create_collection"] = {
            "success": collection_created,
            "collection_name": self.collection_name
        }
        
        if not collection_created:
            results["error"] = "Failed to create Qdrant collection"
            return results
        
        # Step 3: Vectorize chunks
        logger.info("Step 3: Vectorizing chunks...")
        vectorized_chunks = self.vectorize_chunks(chunks)
        results["steps"]["vectorize_chunks"] = {
            "success": len(vectorized_chunks) > 0,
            "chunks_vectorized": len(vectorized_chunks),
            "chunks_failed": len(chunks) - len(vectorized_chunks)
        }
        
        if not vectorized_chunks:
            results["error"] = "Failed to vectorize chunks"
            return results
        
        # Step 4: Initial upsert
        logger.info("Step 4: Performing initial upsert...")
        upsert_success = self.upsert_product_data(article_number, vectorized_chunks)
        results["steps"]["initial_upsert"] = {
            "success": upsert_success,
            "points_upserted": len(vectorized_chunks)
        }
        
        if not upsert_success:
            results["error"] = "Failed to perform initial upsert"
            return results
        
        # Step 5: Test upsert functionality
        logger.info("Step 5: Testing upsert functionality...")
        upsert_test_results = self.test_upsert_functionality(article_number)
        results["steps"]["upsert_testing"] = upsert_test_results
        
        # Step 6: Test search functionality
        logger.info("Step 6: Testing search functionality...")
        search_results = self.test_search_functionality(article_number)
        results["steps"]["search_testing"] = {
            "success": len(search_results) > 0,
            "queries_tested": len(search_results),
            "search_results": search_results
        }
        
        # Get final collection info
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            results["collection_info"] = {
                "collection_name": self.collection_name,
                "points_count": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
                "status": collection_info.status
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
        
        results["workflow_completed"] = datetime.now().isoformat()
        results["success"] = all(
            step.get("success", False) for step in results["steps"].values() 
            if isinstance(step, dict) and "success" in step
        )
        
        if results["success"]:
            logger.info("✅ Shopware-optimized vectorization workflow completed successfully!")
        else:
            logger.error("❌ Shopware-optimized vectorization workflow failed")
        
        return results

def main():
    """Main function to run the Shopware-optimized workflow"""
    print("HELD Inuit Heizhandschuh - Shopware-Optimized Vectorization Workflow")
    print("=" * 70)
    
    # Initialize workflow
    workflow = ShopwareOptimizedWorkflow()
    
    # Run complete workflow
    results = workflow.run_complete_shopware_workflow()
    
    # Print results
    print("\nWorkflow Results:")
    print("=" * 40)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    if results["success"]:
        print("\n✅ Shopware-optimized workflow completed successfully!")
        print(f"Collection: {workflow.collection_name}")
        print(f"Article Number: {results.get('article_number', 'Unknown')}")
        print(f"Points uploaded: {results.get('collection_info', {}).get('points_count', 'Unknown')}")
        
        # Print upsert test summary
        upsert_tests = results.get("steps", {}).get("upsert_testing", {})
        if upsert_tests.get("overall_success"):
            print("✅ Upsert functionality verified - ready for Shopware integration!")
        else:
            print("❌ Upsert functionality issues detected")
            
    else:
        print(f"\n❌ Workflow failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()