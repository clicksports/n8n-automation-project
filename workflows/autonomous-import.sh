#!/bin/bash

# Autonomous n8n Workflow Import Script
# This script will automatically import all workflows via n8n API with authentication

echo "🤖 Starting autonomous n8n workflow import..."

# Configuration
N8N_URL="http://localhost:5678"
EMAIL="christian.gick@clicksports.de"
PASSWORD="7E31UOz295GcHt"

# Workflow files to import
WORKFLOW_FILES=(
    "shopware-to-qdrant-import-enhanced.json"
    "shopware-to-qdrant-import-fixed.json"
    "shopware-to-qdrant-complete.json"
    "shopware-to-qdrant-import.json"
)

# Function to authenticate and get session cookie
authenticate() {
    echo "🔐 Authenticating with n8n..."
    
    # Get login page to extract any CSRF tokens if needed
    login_response=$(curl -s -c cookies.txt -b cookies.txt "$N8N_URL/login" 2>/dev/null)
    
    # Attempt login
    auth_response=$(curl -s -c cookies.txt -b cookies.txt \
        -X POST \
        -H "Content-Type: application/json" \
        -d "{\"emailOrLdapLoginId\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
        "$N8N_URL/rest/login" 2>/dev/null)
    
    if echo "$auth_response" | grep -q '"id"'; then
        echo "✅ Authentication successful"
        return 0
    else
        echo "❌ Authentication failed"
        echo "Response: $auth_response"
        return 1
    fi
}

# Function to import a single workflow
import_workflow() {
    local workflow_file="$1"
    local workflow_name=$(basename "$workflow_file" .json)
    
    echo "📥 Importing workflow: $workflow_name"
    
    if [ ! -f "$workflow_file" ]; then
        echo "❌ File not found: $workflow_file"
        return 1
    fi
    
    # Import workflow via API
    import_response=$(curl -s -b cookies.txt \
        -X POST \
        -H "Content-Type: application/json" \
        -d @"$workflow_file" \
        "$N8N_URL/rest/workflows" 2>/dev/null)
    
    if echo "$import_response" | grep -q '"id"'; then
        workflow_id=$(echo "$import_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        echo "✅ Successfully imported: $workflow_name (ID: $workflow_id)"
        return 0
    else
        echo "❌ Failed to import: $workflow_name"
        echo "Response: $import_response"
        return 1
    fi
}

# Function to list all workflows
list_workflows() {
    echo "📋 Fetching current workflows..."
    
    workflows_response=$(curl -s -b cookies.txt \
        "$N8N_URL/rest/workflows" 2>/dev/null)
    
    if echo "$workflows_response" | grep -q '"data"'; then
        echo "Current workflows:"
        echo "$workflows_response" | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | while read name; do
            echo "  - $name"
        done
        
        # Count workflows
        workflow_count=$(echo "$workflows_response" | grep -o '"name":"[^"]*"' | wc -l)
        echo "Total workflows: $workflow_count"
        return 0
    else
        echo "❌ Failed to fetch workflows"
        echo "Response: $workflows_response"
        return 1
    fi
}

# Function to test a workflow
test_workflow() {
    local workflow_name="$1"
    echo "🧪 Testing workflow: $workflow_name"
    
    # Get workflow ID by name
    workflows_response=$(curl -s -b cookies.txt "$N8N_URL/rest/workflows" 2>/dev/null)
    workflow_id=$(echo "$workflows_response" | grep -B5 -A5 "\"name\":\"$workflow_name\"" | grep -o '"id":"[^"]*"' | cut -d'"' -f4 | head -1)
    
    if [ -z "$workflow_id" ]; then
        echo "❌ Workflow not found: $workflow_name"
        return 1
    fi
    
    echo "Found workflow ID: $workflow_id"
    
    # For testing, we'll just verify the workflow exists and is accessible
    workflow_detail=$(curl -s -b cookies.txt "$N8N_URL/rest/workflows/$workflow_id" 2>/dev/null)
    
    if echo "$workflow_detail" | grep -q '"nodes"'; then
        node_count=$(echo "$workflow_detail" | grep -o '"nodes":\[[^]]*\]' | grep -o '{"' | wc -l)
        echo "✅ Workflow accessible with $node_count nodes"
        return 0
    else
        echo "❌ Failed to access workflow details"
        return 1
    fi
}

# Main execution
main() {
    echo "🚀 Starting autonomous import process..."
    echo "Target: $N8N_URL"
    echo "Workflows to import: ${#WORKFLOW_FILES[@]}"
    echo ""
    
    # Check if n8n is accessible
    if ! curl -s "$N8N_URL" > /dev/null 2>&1; then
        echo "❌ n8n is not accessible at $N8N_URL"
        exit 1
    fi
    
    echo "✅ n8n is accessible"
    
    # Authenticate
    if ! authenticate; then
        echo "❌ Authentication failed, cannot proceed"
        exit 1
    fi
    
    # Show current state
    echo ""
    echo "📊 Current state:"
    list_workflows
    echo ""
    
    # Import workflows
    successful_imports=0
    failed_imports=0
    
    for workflow_file in "${WORKFLOW_FILES[@]}"; do
        if import_workflow "$workflow_file"; then
            ((successful_imports++))
        else
            ((failed_imports++))
        fi
        echo ""
    done
    
    # Show final state
    echo "📊 Final state:"
    list_workflows
    echo ""
    
    # Test imported workflows
    echo "🧪 Testing imported workflows..."
    for workflow_file in "${WORKFLOW_FILES[@]}"; do
        workflow_name=$(jq -r '.name' "$workflow_file" 2>/dev/null || echo "Unknown")
        if [ "$workflow_name" != "Unknown" ] && [ "$workflow_name" != "null" ]; then
            test_workflow "$workflow_name"
        fi
        echo ""
    done
    
    # Summary
    echo "📈 Import Summary:"
    echo "✅ Successful imports: $successful_imports"
    echo "❌ Failed imports: $failed_imports"
    echo "📊 Total workflows processed: $((successful_imports + failed_imports))"
    
    # Cleanup
    rm -f cookies.txt
    
    if [ $successful_imports -gt 0 ]; then
        echo ""
        echo "🎉 Import process completed successfully!"
        echo "You can now access your workflows at: $N8N_URL"
    else
        echo ""
        echo "❌ No workflows were imported successfully"
        exit 1
    fi
}

# Run main function
main "$@"