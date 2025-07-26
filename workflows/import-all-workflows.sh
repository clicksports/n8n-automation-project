#!/bin/bash

# Import all Shopware to Qdrant workflows into n8n
# This script imports multiple workflow versions via n8n API

echo "🚀 Importing all Shopware to Qdrant workflows into n8n..."

# n8n instance details
N8N_URL="http://localhost:5678"

# Array of workflow files to import
WORKFLOW_FILES=(
    "shopware-to-qdrant-import.json"
    "shopware-to-qdrant-import-enhanced.json"
    "shopware-to-qdrant-import-fixed.json"
    "shopware-to-qdrant-complete.json"
)

# Function to import a single workflow
import_workflow() {
    local workflow_file="$1"
    
    if [ ! -f "$workflow_file" ]; then
        echo "❌ Workflow file $workflow_file not found!"
        return 1
    fi
    
    echo "📁 Importing workflow: $workflow_file"
    
    # Try to import via n8n API
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d @"$workflow_file" \
        "$N8N_URL/api/v1/workflows" 2>/dev/null)
    
    if [ $? -eq 0 ] && echo "$response" | grep -q '"id"'; then
        echo "✅ Successfully imported $workflow_file"
        return 0
    else
        echo "⚠️  API import failed for $workflow_file, trying manual approach..."
        return 1
    fi
}

# Check if n8n is running
echo "🔍 Checking if n8n is accessible at $N8N_URL..."
if ! curl -s "$N8N_URL" > /dev/null 2>&1; then
    echo "❌ n8n is not accessible at $N8N_URL"
    echo "Please ensure n8n is running on localhost:5678"
    exit 1
fi

echo "✅ n8n is accessible"

# Import each workflow
successful_imports=0
failed_imports=0

for workflow_file in "${WORKFLOW_FILES[@]}"; do
    if import_workflow "$workflow_file"; then
        ((successful_imports++))
    else
        ((failed_imports++))
        echo "📋 Manual import required for $workflow_file:"
        echo "1. Go to $N8N_URL"
        echo "2. Click 'Create Workflow' or '+' button"
        echo "3. Click the menu (three dots) → 'Import from JSON'"
        echo "4. Copy and paste the contents of: $workflow_file"
        echo ""
    fi
done

echo ""
echo "📊 Import Summary:"
echo "✅ Successful API imports: $successful_imports"
echo "⚠️  Manual imports needed: $failed_imports"

if [ $failed_imports -gt 0 ]; then
    echo ""
    echo "🔧 For manual imports:"
    echo "1. Open your browser to $N8N_URL"
    echo "2. For each failed workflow file:"
    echo "   - Create a new workflow"
    echo "   - Use 'Import from JSON' option"
    echo "   - Copy the entire JSON content from the file"
    echo ""
    echo "📚 See README.md for detailed setup instructions"
fi

echo ""
echo "✅ Import process completed!"