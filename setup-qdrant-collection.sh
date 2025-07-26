#!/bin/bash

# Setup Qdrant Collection for Shopware Products
# This script creates the necessary collection in Qdrant for storing product vectors

set -e

QDRANT_URL="http://localhost:6333"
COLLECTION_NAME="shopware_products"

echo "🔧 Setting up Qdrant collection for Shopware products..."

# Wait for Qdrant to be ready
echo "⏳ Waiting for Qdrant to be ready..."
timeout=60
counter=0
while ! curl -s "$QDRANT_URL/health" > /dev/null; do
    if [ $counter -ge $timeout ]; then
        echo "❌ Timeout waiting for Qdrant to be ready"
        exit 1
    fi
    echo "   Waiting... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

echo "✅ Qdrant is ready!"

# Check if collection already exists
if curl -s "$QDRANT_URL/collections/$COLLECTION_NAME" | grep -q "\"status\":\"ok\""; then
    echo "⚠️  Collection '$COLLECTION_NAME' already exists. Deleting and recreating..."
    curl -X DELETE "$QDRANT_URL/collections/$COLLECTION_NAME"
    sleep 2
fi

# Create collection with appropriate vector configuration
echo "🏗️  Creating collection '$COLLECTION_NAME'..."
curl -X PUT "$QDRANT_URL/collections/$COLLECTION_NAME" \
    -H "Content-Type: application/json" \
    -d '{
        "vectors": {
            "size": 1536,
            "distance": "Cosine"
        },
        "optimizers_config": {
            "default_segment_number": 2
        },
        "replication_factor": 1
    }'

echo ""

# Verify collection creation
echo "🔍 Verifying collection creation..."
if curl -s "$QDRANT_URL/collections/$COLLECTION_NAME" | grep -q "\"status\":\"ok\""; then
    echo "✅ Collection '$COLLECTION_NAME' created successfully!"
    
    # Get collection info
    echo "📊 Collection information:"
    curl -s "$QDRANT_URL/collections/$COLLECTION_NAME" | jq '.'
else
    echo "❌ Failed to create collection '$COLLECTION_NAME'"
    exit 1
fi

echo ""
echo "🎉 Qdrant setup complete!"
echo "📍 Collection: $COLLECTION_NAME"
echo "🌐 Qdrant URL: $QDRANT_URL"
echo "📊 Vector size: 1536 (OpenAI embedding compatible)"
echo "📏 Distance metric: Cosine"
echo ""
echo "You can now run your n8n Shopware workflow to import products!"