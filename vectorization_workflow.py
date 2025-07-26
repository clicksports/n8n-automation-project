#!/usr/bin/env python3
"""
HELD Inuit Heizhandschuh Vectorization Workflow
Optimized for customer support chatbot with Qdrant integration
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
    from qdrant_client.models import Distance, VectorParams, PointStruct
    import numpy as np
except ImportError as e:
    print(f"Missing required packages. Install with: pip install openai qdrant-client numpy")
    print(f"Error: {e}")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ChunkData:
    """Data structure for optimized chunks"""
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

class VectorizationWorkflow:
    """Main workflow class for vectorizing HELD product data"""
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 qdrant_url: str = "localhost",
                 qdrant_port: int = 6333,
                 collection_name: str = "held_products"):
        """
        Initialize the vectorization workflow
        
        Args:
            openai_api_key: OpenAI API key for embeddings
            qdrant_url: Qdrant server URL
            qdrant_port: Qdrant server port
            collection_name: Name of the Qdrant collection
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
    
    def load_optimized_dataset(self, file_path: str = "optimized_dataset_format.json") -> List[ChunkData]:
        """Load the optimized dataset from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chunks = []
            for chunk_data in data.get('optimized_chunks', []):
                chunk = ChunkData(
                    chunk_id=chunk_data['chunk_id'],
                    content=chunk_data['content'],
                    metadata=chunk_data['metadata']
                )
                chunks.append(chunk)
            
            logger.info(f"Loaded {len(chunks)} chunks from {file_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            return []
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI API"""
        if not self.openai_api_key:
            # Generate mock embedding for testing
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
    
    def create_qdrant_collection(self, vector_size: int = 3072) -> bool:
        """Create Qdrant collection with optimal settings"""
        if not self.qdrant_client:
            logger.error("Qdrant client not available")
            return False
        
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True
            
            # Create collection with optimized settings
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            
            logger.info(f"Created collection '{self.collection_name}' with vector size {vector_size}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False
    
    def vectorize_chunks(self, chunks: List[ChunkData]) -> List[ChunkData]:
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
    
    def upload_to_qdrant(self, chunks: List[ChunkData]) -> bool:
        """Upload vectorized chunks to Qdrant"""
        if not self.qdrant_client:
            logger.error("Qdrant client not available")
            return False
        
        if not chunks:
            logger.error("No chunks to upload")
            return False
        
        try:
            # Prepare points for upload
            points = []
            for chunk in chunks:
                if not chunk.embedding:
                    continue
                
                # Add timestamp and processing info to metadata
                enhanced_metadata = chunk.metadata.copy()
                enhanced_metadata.update({
                    'processed_at': datetime.now().isoformat(),
                    'content_length': len(chunk.content),
                    'embedding_model': 'text-embedding-3-large',
                    'workflow_version': '1.0'
                })
                
                point = PointStruct(
                    id=hash(chunk.chunk_id) % (2**63),  # Convert string ID to int
                    vector=chunk.embedding,
                    payload={
                        'chunk_id': chunk.chunk_id,
                        'content': chunk.content,
                        'metadata': enhanced_metadata
                    }
                )
                points.append(point)
            
            # Upload to Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Successfully uploaded {len(points)} points to Qdrant collection '{self.collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload to Qdrant: {e}")
            return False
    
    def test_search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Test search functionality"""
        if not self.qdrant_client:
            logger.error("Qdrant client not available")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True
            )
            
            results = []
            for result in search_results:
                results.append({
                    'score': result.score,
                    'chunk_id': result.payload['chunk_id'],
                    'content': result.payload['content'][:200] + "..." if len(result.payload['content']) > 200 else result.payload['content'],
                    'metadata': result.payload['metadata']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the Qdrant collection"""
        if not self.qdrant_client:
            return {"error": "Qdrant client not available"}
        
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "points_count": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
                "status": collection_info.status
            }
        except Exception as e:
            return {"error": str(e)}
    
    def run_complete_workflow(self) -> Dict[str, Any]:
        """Run the complete vectorization workflow"""
        logger.info("Starting complete vectorization workflow...")
        
        results = {
            "workflow_started": datetime.now().isoformat(),
            "steps": {},
            "success": False
        }
        
        # Step 1: Load dataset
        logger.info("Step 1: Loading optimized dataset...")
        chunks = self.load_optimized_dataset()
        results["steps"]["load_dataset"] = {
            "success": len(chunks) > 0,
            "chunks_loaded": len(chunks)
        }
        
        if not chunks:
            results["error"] = "Failed to load dataset"
            return results
        
        # Step 2: Create Qdrant collection
        logger.info("Step 2: Creating Qdrant collection...")
        collection_created = self.create_qdrant_collection()
        results["steps"]["create_collection"] = {
            "success": collection_created
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
        
        # Step 4: Upload to Qdrant
        logger.info("Step 4: Uploading to Qdrant...")
        upload_success = self.upload_to_qdrant(vectorized_chunks)
        results["steps"]["upload_to_qdrant"] = {
            "success": upload_success
        }
        
        if not upload_success:
            results["error"] = "Failed to upload to Qdrant"
            return results
        
        # Step 5: Test search
        logger.info("Step 5: Testing search functionality...")
        test_queries = [
            "Wie lange hält der Akku?",
            "Welche Größen gibt es?",
            "Ist der Handschuh wasserdicht?",
            "Preis des Handschuhs"
        ]
        
        search_results = {}
        for query in test_queries:
            results_for_query = self.test_search(query, limit=2)
            search_results[query] = results_for_query
        
        results["steps"]["test_search"] = {
            "success": len(search_results) > 0,
            "test_queries": len(test_queries),
            "search_results": search_results
        }
        
        # Get final collection info
        collection_info = self.get_collection_info()
        results["collection_info"] = collection_info
        
        results["workflow_completed"] = datetime.now().isoformat()
        results["success"] = True
        
        logger.info("Vectorization workflow completed successfully!")
        return results

def main():
    """Main function to run the workflow"""
    print("HELD Inuit Heizhandschuh Vectorization Workflow")
    print("=" * 50)
    
    # Initialize workflow
    workflow = VectorizationWorkflow()
    
    # Run complete workflow
    results = workflow.run_complete_workflow()
    
    # Print results
    print("\nWorkflow Results:")
    print("=" * 30)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    if results["success"]:
        print("\n✅ Workflow completed successfully!")
        print(f"Collection: {workflow.collection_name}")
        print(f"Points uploaded: {results['collection_info'].get('points_count', 'Unknown')}")
    else:
        print(f"\n❌ Workflow failed: {results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()