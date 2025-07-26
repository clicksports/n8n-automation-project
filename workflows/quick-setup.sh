#!/bin/bash

# Shopware to Qdrant Quick Setup Script
# This script helps you set up the Qdrant collections and verify connectivity

echo "🚀 Shopware to Qdrant Quick Setup"
echo "=================================="

# Qdrant connection details
QDRANT_URL="https://8ec957ec-27b4-4041-9714-f8dde751b007.europe-west3-0.gcp.cloud.qdrant.io:6333"
API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.50x-a9c0zTX_dzWnKjq-xM7rJ0ym6_yZ-D_eN_Idft4"

echo "📡 Testing Qdrant connection..."
response=$(curl -s -w "%{http_code}" -X GET "$QDRANT_URL" \
  --header "api-key: $API_KEY" \
  -o /dev/null)

if [ "$response" = "200" ]; then
    echo "✅ Qdrant connection successful!"
else
    echo "❌ Qdrant connection failed (HTTP $response)"
    echo "Please check your network connection and credentials"
    exit 1
fi

echo ""
echo "📋 Listing existing collections..."
curl -s -X GET "$QDRANT_URL/collections" \
  --header "api-key: $API_KEY" | jq '.'

echo ""
echo "🏗️ Creating production collection: shopware_products"
curl -s -X PUT "$QDRANT_URL/collections/shopware_products" \
  --header "api-key: $API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "vectors": {
      "size": 1536,
      "distance": "Cosine"
    },
    "optimizers_config": {
      "default_segment_number": 2
    },
    "replication_factor": 1
  }' | jq '.'

echo ""
echo "🧪 Creating test collection: shopware_products_test"
curl -s -X PUT "$QDRANT_URL/collections/shopware_products_test" \
  --header "api-key: $API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "vectors": {
      "size": 1536,
      "distance": "Cosine"
    },
    "optimizers_config": {
      "default_segment_number": 1
    },
    "replication_factor": 1
  }' | jq '.'

echo ""
echo "✅ Setup complete! Your collections are ready."
echo ""
echo "📝 Next steps:"
echo "1. Import the n8n workflow from shopware-to-qdrant-import-enhanced.json"
echo "2. Configure OpenAI credentials in n8n"
echo "3. Configure Qdrant credentials in n8n with:"
echo "   - Host: 8ec957ec-27b4-4041-9714-f8dde751b007.europe-west3-0.gcp.cloud.qdrant.io"
echo "   - Port: 6333"
echo "   - API Key: $API_KEY"
echo "   - Use SSL: true"
echo "4. Test with shopware_products_test collection first"
echo "5. Run full import to shopware_products collection"
echo ""
echo "📚 See README.md for detailed instructions"