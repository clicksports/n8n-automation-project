# HELD Product Vectorization - n8n Deployment Guide

## Overview
This guide provides step-by-step instructions to deploy and run the optimized HELD Inuit Heizhandschuh vectorization workflow in n8n.

## Prerequisites
- n8n instance running (local or cloud)
- Qdrant vector database accessible
- Optimized dataset file (`optimized_dataset_format.json`) in the n8n workspace
- Optional: OpenAI API key for real embeddings

## Quick Deployment

### 1. Import the Workflow
```bash
# Copy the workflow file to your n8n workflows directory
cp workflows/held-product-vectorization-optimized.json /path/to/n8n/workflows/

# Or import via n8n UI:
# 1. Open n8n interface
# 2. Click "Import from File"
# 3. Select held-product-vectorization-optimized.json
```

### 2. Setup Required Files
```bash
# Ensure the optimized dataset is accessible to n8n
cp optimized_dataset_format.json /path/to/n8n/workspace/

# Start Qdrant if not already running
docker-compose -f docker-compose-qdrant.yml up -d
```

### 3. Configure Workflow Settings
1. **Qdrant Connection**: Update the Qdrant URL in the "Upload to Qdrant" node if needed
2. **Dataset Path**: Verify the dataset file path in the "Load Optimized Dataset" node
3. **Collection Name**: Ensure the collection name matches your Qdrant setup

### 4. Execute the Workflow
1. Open the workflow in n8n
2. Click "Execute Workflow" or use the manual trigger
3. Monitor the execution progress through each node

## Detailed Setup Instructions

### Step 1: n8n Environment Preparation

#### Local n8n Setup
```bash
# Install n8n globally
npm install n8n -g

# Start n8n
n8n start

# Access n8n at http://localhost:5678
```

#### Docker n8n Setup
```bash
# Create n8n docker-compose.yml
cat > docker-compose-n8n.yml << EOF
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=password
    volumes:
      - n8n_data:/home/node/.n8n
      - ./:/data
volumes:
  n8n_data:
EOF

# Start n8n
docker-compose -f docker-compose-n8n.yml up -d
```

### Step 2: Workflow Import and Configuration

#### Import via n8n UI
1. **Access n8n**: Open http://localhost:5678
2. **Login**: Use your credentials (admin/password for Docker setup)
3. **Import Workflow**:
   - Click "+" to create new workflow
   - Click "Import from File"
   - Select `workflows/held-product-vectorization-optimized.json`
   - Click "Import"

#### Import via CLI (if available)
```bash
# Using n8n CLI
n8n import:workflow --file=workflows/held-product-vectorization-optimized.json
```

### Step 3: Node Configuration

#### 1. Load Optimized Dataset Node
```javascript
// Update the dataset path if needed
const datasetPath = path.join(process.cwd(), 'optimized_dataset_format.json');
// Or use absolute path:
// const datasetPath = '/absolute/path/to/optimized_dataset_format.json';
```

#### 2. Upload to Qdrant Node
```json
{
  "method": "PUT",
  "url": "http://localhost:6333/collections/held_products/points",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

**For Cloud Qdrant:**
```json
{
  "method": "PUT",
  "url": "https://your-cluster.qdrant.io:6333/collections/held_products/points",
  "headers": {
    "Content-Type": "application/json",
    "api-key": "your-api-key"
  }
}
```

#### 3. Optional: OpenAI Integration
To use real OpenAI embeddings instead of mock embeddings:

1. **Add OpenAI Node** between "Process & Optimize Content" and "Prepare Optimized Qdrant Point"
2. **Configure OpenAI Node**:
   ```json
   {
     "method": "POST",
     "url": "https://api.openai.com/v1/embeddings",
     "headers": {
       "Authorization": "Bearer {{ $env.OPENAI_API_KEY }}",
       "Content-Type": "application/json"
     },
     "body": {
       "model": "text-embedding-3-large",
       "input": "={{ $json.processed_content }}",
       "dimensions": 3072
     }
   }
   ```
3. **Set Environment Variable**:
   ```bash
   export OPENAI_API_KEY="sk-your-api-key-here"
   ```

### Step 4: Qdrant Collection Setup

#### Create Collection (if not exists)
```bash
# Create the held_products collection
curl -X PUT "http://localhost:6333/collections/held_products" \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 3072,
      "distance": "Cosine"
    }
  }'
```

#### Verify Collection
```bash
# Check collection info
curl "http://localhost:6333/collections/held_products"
```

### Step 5: Workflow Execution

#### Manual Execution
1. **Open Workflow**: Navigate to the imported workflow
2. **Check Connections**: Ensure all nodes are properly connected
3. **Execute**: Click "Execute Workflow" button
4. **Monitor Progress**: Watch each node execute in sequence

#### Expected Execution Flow
```
Manual Trigger
    ↓
Load Optimized Dataset (15 chunks)
    ↓
Process & Optimize Content (German preprocessing)
    ↓
Generate Mock Embeddings (3072 dimensions)
    ↓
Prepare Optimized Qdrant Point (enhanced metadata)
    ↓
Collect Points for Batch Upload (batch preparation)
    ↓
Upload to Qdrant (vector storage)
    ↓
Generate Completion Report (final summary)
```

#### Execution Results
```json
{
  "workflow_status": "completed",
  "upload_summary": {
    "points_uploaded": 15,
    "chunk_types": ["product_overview", "technical_specifications", "usage_scenarios", "customer_service"],
    "upload_success": true
  },
  "optimization_features": [
    "German language preprocessing",
    "Technical term standardization",
    "Enhanced metadata schema",
    "Customer intent mapping",
    "Semantic chunking strategy"
  ]
}
```

## Workflow Features

### 1. German Language Optimization
- **Character Normalization**: ä→ae, ö→oe, ü→ue, ß→ss
- **Technical Term Standardization**: Consistent terminology
- **Currency/Measurement Normalization**: €→EUR, °C→Grad Celsius

### 2. Enhanced Metadata Schema
```json
{
  "chunk_id": "inuit_001_overview",
  "content_category": "basic_info",
  "customer_intents": ["product_inquiry", "price_check"],
  "technical_level": "basic",
  "confidence_score": 0.95,
  "keywords": ["Preis", "Verfügbarkeit", "Größen"],
  "search_tags": ["HELD", "Inuit", "Heizhandschuh"],
  "language_optimized": true,
  "preprocessing_applied": ["german_normalization", "technical_term_standardization"]
}
```

### 3. Customer Support Context
- **45 Unique Customer Intents**: battery_life, sizing_questions, weather_protection, etc.
- **4 Technical Levels**: basic, intermediate, detailed, expert
- **15 Content Categories**: heating_performance, materials, safety_protection, etc.

## Testing and Validation

### 1. Workflow Execution Test
```bash
# Check if workflow completed successfully
curl "http://localhost:6333/collections/held_products/points/count"
# Expected: {"result": {"count": 15}}
```

### 2. Search Functionality Test
```bash
# Test search with German query
curl -X POST "http://localhost:6333/collections/held_products/points/search" \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, ...], 
    "limit": 3,
    "with_payload": true,
    "filter": {
      "must": [
        {"key": "language", "match": {"value": "de"}}
      ]
    }
  }'
```

### 3. Quality Validation
- **Chunk Coverage**: All 4 chunk types represented
- **Content Categories**: 15 unique categories
- **Customer Intents**: 45 mapped intents
- **Language Processing**: German optimization applied

## Troubleshooting

### Common Issues

#### 1. Dataset Loading Failed
```
Error: Dataset loading failed: ENOENT: no such file or directory
```
**Solution**: Ensure `optimized_dataset_format.json` is in the correct path
```bash
# Check file exists
ls -la optimized_dataset_format.json

# Copy to n8n workspace if needed
cp optimized_dataset_format.json /path/to/n8n/workspace/
```

#### 2. Qdrant Connection Failed
```
Error: connect ECONNREFUSED 127.0.0.1:6333
```
**Solution**: Start Qdrant server
```bash
# Start Qdrant
docker-compose -f docker-compose-qdrant.yml up -d

# Verify Qdrant is running
curl http://localhost:6333/health
```

#### 3. Collection Not Found
```
Error: Collection 'held_products' not found
```
**Solution**: Create the collection
```bash
curl -X PUT "http://localhost:6333/collections/held_products" \
  -H "Content-Type: application/json" \
  -d '{"vectors": {"size": 3072, "distance": "Cosine"}}'
```

#### 4. Memory Issues with Large Datasets
**Solution**: Increase n8n memory limits
```bash
# For Docker
docker run -e NODE_OPTIONS="--max-old-space-size=4096" n8nio/n8n

# For local installation
export NODE_OPTIONS="--max-old-space-size=4096"
n8n start
```

### Performance Optimization

#### 1. Batch Processing
- Current workflow processes all 15 chunks in batch
- For larger datasets, consider splitting into smaller batches

#### 2. Parallel Processing
- Enable parallel execution in n8n settings
- Use multiple worker processes for large datasets

#### 3. Caching
- Cache embeddings to avoid regeneration
- Store processed content for reuse

## Integration with Customer Support

### 1. Search API Integration
```javascript
// Example search function for chatbot
async function searchHELDProduct(query, limit = 3) {
  const response = await fetch('http://localhost:6333/collections/held_products/points/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      vector: await generateEmbedding(query),
      limit: limit,
      with_payload: true,
      filter: {
        must: [
          { key: "language", match: { value: "de" } }
        ]
      }
    })
  });
  
  return response.json();
}
```

### 2. Intent-Based Filtering
```javascript
// Filter by customer intent
const intentFilter = {
  must: [
    { key: "customer_intents", match: { any: ["battery_life"] } }
  ]
};
```

### 3. Technical Level Adaptation
```javascript
// Adapt response complexity based on user level
const technicalFilter = {
  must: [
    { key: "technical_level", match: { value: "basic" } }
  ]
};
```

## Monitoring and Maintenance

### 1. Workflow Monitoring
- Monitor execution times and success rates
- Set up alerts for failed executions
- Track data quality metrics

### 2. Data Updates
- Re-run workflow when product data changes
- Update embeddings when content is modified
- Maintain version control for datasets

### 3. Performance Metrics
- Search response times
- Relevance scores
- Customer satisfaction ratings

## Next Steps

1. **Production Deployment**: Move to production n8n and Qdrant instances
2. **Real Embeddings**: Integrate OpenAI API for production-quality embeddings
3. **Monitoring Setup**: Implement comprehensive monitoring and alerting
4. **Scaling**: Prepare for additional HELD products and larger datasets
5. **Integration**: Connect with existing customer support systems

The optimized HELD product vectorization workflow is now ready for deployment and integration with your customer support chatbot system.