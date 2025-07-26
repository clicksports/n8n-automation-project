#!/bin/bash

# Restore n8n workflows from backup directory
# This script imports all workflow JSON files from the most recent backup

echo "🔄 Restoring n8n workflows from backup..."

# n8n instance details
N8N_URL="http://localhost:5678"

# Find the most recent backup directory
BACKUP_DIR=$(ls -td workflows/backups/backup-* 2>/dev/null | head -1)

if [ -z "$BACKUP_DIR" ]; then
    echo "❌ No backup directories found in workflows/backups/"
    exit 1
fi

echo "📁 Using backup directory: $BACKUP_DIR"

# Function to import a single workflow
import_workflow() {
    local workflow_file="$1"
    local filename=$(basename "$workflow_file")
    
    echo "📥 Importing workflow: $filename"
    
    # Try to import via n8n API
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d @"$workflow_file" \
        "$N8N_URL/api/v1/workflows" 2>/dev/null)
    
    if [ $? -eq 0 ] && echo "$response" | grep -q '"id"'; then
        workflow_id=$(echo "$response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        echo "✅ Successfully imported $filename (ID: $workflow_id)"
        return 0
    else
        echo "❌ Failed to import $filename"
        echo "Response: $response"
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

# Count workflow files
workflow_count=$(find "$BACKUP_DIR" -name "*.json" | wc -l)
echo "📊 Found $workflow_count workflow files to import"

# Import each workflow
successful_imports=0
failed_imports=0

for workflow_file in "$BACKUP_DIR"/*.json; do
    if [ -f "$workflow_file" ]; then
        if import_workflow "$workflow_file"; then
            ((successful_imports++))
        else
            ((failed_imports++))
        fi
    fi
done

echo ""
echo "📊 Restore Summary:"
echo "✅ Successful imports: $successful_imports"
echo "❌ Failed imports: $failed_imports"
echo "📁 Backup directory used: $BACKUP_DIR"

if [ $successful_imports -gt 0 ]; then
    echo ""
    echo "🎉 Workflows successfully restored!"
    echo "🌐 Access your n8n instance at: $N8N_URL"
else
    echo ""
    echo "⚠️  No workflows were imported successfully."
    echo "Please check the n8n logs and API connectivity."
fi

echo ""
echo "✅ Restore process completed!"