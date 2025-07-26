#!/bin/bash

# Restore n8n workflows using n8n CLI from within Docker container
# This script imports all workflow JSON files that were copied to the docker volume

echo "🔄 Restoring n8n workflows via CLI..."

# Check if Docker container is running
CONTAINER_ID=$(docker ps -q -f "ancestor=n8nio/n8n:latest")
if [ -z "$CONTAINER_ID" ]; then
    echo "❌ n8n Docker container is not running"
    exit 1
fi

echo "✅ Found n8n container: $CONTAINER_ID"

# Import each workflow file in the docker directory
successful_imports=0
failed_imports=0

echo "📊 Importing workflows from docker directory..."

for workflow_file in docker/*.json; do
    if [ -f "$workflow_file" ]; then
        filename=$(basename "$workflow_file")
        echo "📥 Importing workflow: $filename"
        
        # Import via n8n CLI inside container
        if docker exec "$CONTAINER_ID" n8n import:workflow --input="/home/node/.n8n/$filename" 2>/dev/null | grep -q "Successfully imported"; then
            echo "✅ Successfully imported $filename"
            ((successful_imports++))
        else
            echo "❌ Failed to import $filename"
            ((failed_imports++))
        fi
    fi
done

echo ""
echo "📊 Restore Summary:"
echo "✅ Successful imports: $successful_imports"
echo "❌ Failed imports: $failed_imports"

if [ $successful_imports -gt 0 ]; then
    echo ""
    echo "🎉 Workflows successfully restored!"
    echo "🌐 Access your n8n instance at: http://localhost:5678"
    
    # Clean up the JSON files from docker directory
    echo "🧹 Cleaning up temporary files..."
    rm -f docker/*.json
    echo "✅ Cleanup completed"
else
    echo ""
    echo "⚠️  No workflows were imported successfully."
fi

echo ""
echo "✅ Restore process completed!"