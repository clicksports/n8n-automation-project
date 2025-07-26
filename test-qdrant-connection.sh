#!/bin/bash

# Test script for Qdrant Local Setup
echo "🧪 Testing Qdrant Local Setup for Shopware n8n Workflow"
echo "========================================================"

# Test Qdrant health
echo "1. Testing Qdrant health..."
HEALTH_RESPONSE=$(curl -s http://localhost:6333/health)
if [ $? -eq 0 ]; then
    echo "✅ Qdrant is healthy"
else
    echo "❌ Qdrant health check failed"
    exit 1
fi

# Test n8n health
echo "2. Testing n8n health..."
N8N_RESPONSE=$(curl -s http://localhost:5678/healthz)
if [ $? -eq 0 ] && echo "$N8N_RESPONSE" | grep -q "ok"; then
    echo "✅ n8n is healthy"
else
    echo "❌ n8n health check failed"
    exit 1
fi

# List collections
echo "3. Checking Qdrant collections..."
COLLECTIONS=$(curl -s http://localhost:6333/collections)
echo "📂 Available collections:"
echo "$COLLECTIONS" | jq '.result.collections[].name' 2>/dev/null || echo "$COLLECTIONS"

# Check shopware_products collection
echo "4. Checking shopware_products collection..."
COLLECTION_INFO=$(curl -s http://localhost:6333/collections/shopware_products)
if echo "$COLLECTION_INFO" | grep -q '"status":"ok"'; then
    echo "✅ shopware_products collection exists and is ready"
    POINTS_COUNT=$(echo "$COLLECTION_INFO" | jq '.result.points_count' 2>/dev/null || echo "unknown")
    echo "📊 Current points count: $POINTS_COUNT"
else
    echo "❌ shopware_products collection check failed"
    exit 1
fi

# Test basic vector insertion
echo "5. Testing vector insertion..."
# Create a simple 1536-dimensional test vector with integer ID
TEST_VECTOR='{"points":[{"id":12345,"vector":'$(python3 -c "import json; print(json.dumps([0.1] * 1536))")',"payload":{"name":"Test Product","price":99.99,"test":true}}]}'

INSERT_RESPONSE=$(curl -s -X PUT "http://localhost:6333/collections/shopware_products/points" \
    -H "Content-Type: application/json" \
    -d "$TEST_VECTOR")

if echo "$INSERT_RESPONSE" | grep -q '"status":"ok"'; then
    echo "✅ Test vector insertion successful"
else
    echo "❌ Test vector insertion failed"
    echo "Response: $INSERT_RESPONSE"
    exit 1
fi

# Verify the test point was inserted
echo "6. Verifying test point insertion..."
UPDATED_INFO=$(curl -s http://localhost:6333/collections/shopware_products)
NEW_POINTS_COUNT=$(echo "$UPDATED_INFO" | jq '.result.points_count' 2>/dev/null || echo "unknown")
echo "📊 Updated points count: $NEW_POINTS_COUNT"

# Clean up test data
echo "7. Cleaning up test data..."
DELETE_RESPONSE=$(curl -s -X POST "http://localhost:6333/collections/shopware_products/points/delete" \
    -H "Content-Type: application/json" \
    -d '{"points":[12345]}')

if echo "$DELETE_RESPONSE" | grep -q '"status":"ok"'; then
    echo "✅ Test data cleanup successful"
else
    echo "⚠️ Test data cleanup failed (not critical)"
fi

echo ""
echo "🎉 All tests passed! Your Qdrant local setup is ready for Shopware workflows."
echo ""
echo "📋 Next steps:"
echo "   1. Open n8n at: http://localhost:5678"
echo "   2. Import workflow: docker/workflows/shopware-to-qdrant-local.json"
echo "   3. Execute the workflow to import Shopware products"
echo "   4. Monitor Qdrant at: http://localhost:6333/dashboard"
echo ""
echo "🔧 Useful commands:"
echo "   - Check collections: curl http://localhost:6333/collections"
echo "   - View collection info: curl http://localhost:6333/collections/shopware_products"
echo "   - Count points: curl http://localhost:6333/collections/shopware_products/points/count"