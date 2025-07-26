#!/bin/bash

# Activate all imported workflows in n8n
echo "🔄 Activating all workflows in n8n..."

# Get all workflow IDs and activate them
n8n list:workflow --onlyId 2>/dev/null | while read -r workflow_id; do
    if [[ -n "$workflow_id" ]]; then
        echo "⚡ Activating workflow: $workflow_id"
        # Use n8n CLI to update workflow status (if available) or API call
        curl -s -X PATCH "http://localhost:5678/rest/workflows/$workflow_id" \
            -H "Content-Type: application/json" \
            -d '{"active": true}' > /dev/null 2>&1
        
        if [[ $? -eq 0 ]]; then
            echo "✅ Activated: $workflow_id"
        else
            echo "⚠️  Failed to activate: $workflow_id"
        fi
    fi
done

echo ""
echo "🎉 Workflow activation completed!"
echo "💡 Refresh your n8n browser page to see the activated workflows"