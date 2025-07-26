#!/bin/bash

# Import Shopware to Qdrant workflow into n8n
# This script imports the enhanced workflow directly via n8n API

echo "🚀 Importing Shopware to Qdrant workflow into n8n..."

# n8n instance details
N8N_URL="http://localhost:5678"
WORKFLOW_FILE="shopware-to-qdrant-import-enhanced.json"

# Check if workflow file exists
if [ ! -f "$WORKFLOW_FILE" ]; then
    echo "❌ Workflow file $WORKFLOW_FILE not found!"
    exit 1
fi

echo "📁 Found workflow file: $WORKFLOW_FILE"

# Import workflow via n8n API
echo "📤 Importing workflow..."

# First, let's try to import via the web interface approach
echo "🌐 Please manually import the workflow:"
echo "1. Go to http://localhost:5678"
echo "2. Click 'Create Workflow' or use the existing workflow"
echo "3. Click the menu (three dots) → 'Import from JSON'"
echo "4. Copy and paste the contents of: $WORKFLOW_FILE"
echo ""
echo "📋 Workflow JSON content:"
echo "================================"
cat "$WORKFLOW_FILE"
echo ""
echo "================================"
echo ""
echo "✅ After importing, you'll need to:"
echo "1. Configure OpenAI credentials (for embeddings)"
echo "2. Configure Qdrant credentials (already documented)"
echo "3. Test with shopware_products_test collection"
echo "4. Run full import to shopware_products collection"
echo ""
echo "📚 See README.md for detailed setup instructions"