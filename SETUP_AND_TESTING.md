# HELD Inuit Heizhandschuh Vectorization Setup & Testing Guide

## Overview
This guide provides step-by-step instructions to set up and test the optimized vectorization workflow for the HELD Inuit Heizhandschuh product data with Qdrant vector database.

## Prerequisites
- Python 3.8 or higher
- Docker and Docker Compose (for Qdrant)
- OpenAI API key (optional - will use mock embeddings if not provided)

## Quick Start

### 1. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Start Qdrant Vector Database
```bash
# Start Qdrant using Docker Compose
docker-compose -f docker-compose-qdrant.yml up -d

# Verify Qdrant is running
curl http://localhost:6333/health
```

### 3. Set OpenAI API Key (Optional)
```bash
# Set environment variable
export OPENAI_API_KEY="your-api-key-here"

# Or create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 4. Run the Complete Workflow
```bash
# Run the main vectorization workflow
python vectorization_workflow.py
```

### 5. Run Tests
```bash
# Run comprehensive test suite
python test_vectorization.py
```

## Detailed Setup Instructions

### Step 1: Environment Setup
1. **Clone or download the project files**
2. **Install Python dependencies:**
   ```bash
   pip install openai qdrant-client numpy python-dotenv requests
   ```

### Step 2: Qdrant Database Setup
1. **Start Qdrant container:**
   ```bash
   docker-compose -f docker-compose-qdrant.yml up -d
   ```

2. **Verify Qdrant is accessible:**
   ```bash
   # Check health endpoint
   curl http://localhost:6333/health
   
   # Check collections (should be empty initially)
   curl http://localhost:6333/collections
   ```

3. **Qdrant Web UI (optional):**
   - Access at: http://localhost:6333/dashboard
   - View collections, points, and perform searches

### Step 3: OpenAI Configuration (Optional)
If you have an OpenAI API key for real embeddings:

1. **Set environment variable:**
   ```bash
   export OPENAI_API_KEY="sk-your-api-key-here"
   ```

2. **Or create .env file:**
   ```bash
   echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
   ```

**Note:** If no API key is provided, the workflow will use deterministic mock embeddings for testing purposes.

## Running the Workflow

### Option 1: Complete Workflow
```bash
python vectorization_workflow.py
```

This will:
1. Load the optimized dataset (15 chunks)
2. Create Qdrant collection "held_products"
3. Generate embeddings for all chunks
4. Upload vectors to Qdrant
5. Test search functionality
6. Display results and collection info

### Option 2: Test Suite
```bash
python test_vectorization.py
```

This will:
1. Test Qdrant connection
2. Test dataset loading
3. Test embedding generation
4. Run complete workflow
5. Provide interactive search testing

## Expected Results

### Successful Workflow Output
```
HELD Inuit Heizhandschuh Vectorization Workflow
==================================================

Step 1: Loading optimized dataset...
✅ Loaded 15 chunks from optimized_dataset_format.json

Step 2: Creating Qdrant collection...
✅ Created collection 'held_products' with vector size 3072

Step 3: Vectorizing chunks...
✅ Successfully vectorized 15/15 chunks

Step 4: Uploading to Qdrant...
✅ Successfully uploaded 15 points to Qdrant collection 'held_products'

Step 5: Testing search functionality...
✅ Search tests completed

Workflow Results:
{
  "success": true,
  "collection_info": {
    "collection_name": "held_products",
    "points_count": 15,
    "vector_size": 3072,
    "distance": "Cosine"
  }
}
```

### Test Search Examples
The workflow will test these German queries:
- "Wie lange hält der Akku?" (How long does the battery last?)
- "Welche Größen gibt es?" (What sizes are available?)
- "Ist der Handschuh wasserdicht?" (Is the glove waterproof?)
- "Preis des Handschuhs" (Price of the glove)

## Verifying Results in Qdrant

### 1. Check Collection via API
```bash
# Get collection info
curl http://localhost:6333/collections/held_products

# Count points
curl http://localhost:6333/collections/held_products/points/count
```

### 2. Manual Search Test
```bash
# Search for "Akku" (battery) - requires embedding vector
curl -X POST http://localhost:6333/collections/held_products/points/search \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, ...], 
    "limit": 3,
    "with_payload": true
  }'
```

### 3. Browse via Web UI
- Open: http://localhost:6333/dashboard
- Navigate to "held_products" collection
- View points and metadata
- Perform searches

## Troubleshooting

### Common Issues

1. **Qdrant Connection Failed**
   ```bash
   # Check if Qdrant is running
   docker ps | grep qdrant
   
   # Check logs
   docker logs qdrant-held-vectorization
   
   # Restart if needed
   docker-compose -f docker-compose-qdrant.yml restart
   ```

2. **OpenAI API Errors**
   ```bash
   # Verify API key
   echo $OPENAI_API_KEY
   
   # Test API access
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

3. **Python Dependencies**
   ```bash
   # Reinstall dependencies
   pip install --upgrade -r requirements.txt
   
   # Check versions
   pip list | grep -E "(openai|qdrant|numpy)"
   ```

4. **Dataset Loading Issues**
   ```bash
   # Verify file exists
   ls -la optimized_dataset_format.json
   
   # Check JSON syntax
   python -m json.tool optimized_dataset_format.json
   ```

### Performance Optimization

1. **Batch Processing:** For larger datasets, modify the workflow to process chunks in batches
2. **Parallel Processing:** Use threading for embedding generation
3. **Memory Management:** Clear embeddings after upload for large datasets

## Advanced Usage

### Custom Configuration
```python
# Initialize with custom settings
workflow = VectorizationWorkflow(
    qdrant_url="your-qdrant-host",
    qdrant_port=6333,
    collection_name="custom_collection"
)
```

### Search with Filters
```python
# Search with metadata filters
results = workflow.qdrant_client.search(
    collection_name="held_products",
    query_vector=embedding,
    query_filter={
        "must": [
            {"key": "metadata.content_category", "match": {"value": "technical_specifications"}}
        ]
    },
    limit=5
)
```

## Data Structure

### Chunk Metadata Schema
```json
{
  "chunk_type": "product_overview|technical_specifications|usage_scenarios|customer_service",
  "content_category": "basic_info|heating_performance|materials|safety_protection|...",
  "keywords": ["array", "of", "relevant", "keywords"],
  "customer_intents": ["product_inquiry", "technical_support", "..."],
  "confidence_score": 0.95,
  "technical_level": "basic|intermediate|detailed",
  "seasonal_relevance": "winter|all_season",
  "related_products": ["product_ids"]
}
```

## Next Steps

1. **Integration with n8n:** Use the vectorized data in n8n workflows
2. **Chatbot Implementation:** Connect to your preferred chatbot framework
3. **Monitoring:** Set up logging and performance monitoring
4. **Scaling:** Extend to additional HELD products
5. **Feedback Loop:** Implement user feedback collection for continuous improvement

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the workflow logs for detailed error messages
3. Verify all prerequisites are met
4. Test individual components using the test suite