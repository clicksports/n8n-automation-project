#!/bin/bash

echo "🧪 N8N WORKFLOW IMPORT AND EXECUTION"
echo "===================================="

# Import the workflow
echo "🔄 Importing updated workflow into n8n..."
IMPORT_RESPONSE=$(curl -s -X POST "http://localhost:5678/api/v1/workflows" \
  -H "Content-Type: application/json" \
  -d @workflows/shopware-optimized-vectorization-workflow-fixed.json)

# Extract workflow ID
WORKFLOW_ID=$(echo "$IMPORT_RESPONSE" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    if 'data' in data and 'id' in data['data']:
        print(data['data']['id'])
    else:
        print('ERROR')
except:
    print('ERROR')
")

if [ "$WORKFLOW_ID" = "ERROR" ]; then
    echo "❌ Failed to import workflow"
    echo "Response: $IMPORT_RESPONSE"
    exit 1
fi

echo "✅ Workflow imported successfully with ID: $WORKFLOW_ID"

# Execute the workflow
echo "🚀 Executing workflow $WORKFLOW_ID..."
EXECUTE_RESPONSE=$(curl -s -X POST "http://localhost:5678/api/v1/workflows/$WORKFLOW_ID/execute" \
  -H "Content-Type: application/json" \
  -d '{}')

# Extract execution ID
EXECUTION_ID=$(echo "$EXECUTE_RESPONSE" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    if 'data' in data and 'executionId' in data['data']:
        print(data['data']['executionId'])
    else:
        print('ERROR')
except:
    print('ERROR')
")

if [ "$EXECUTION_ID" = "ERROR" ]; then
    echo "❌ Failed to execute workflow"
    echo "Response: $EXECUTE_RESPONSE"
    exit 1
fi

echo "✅ Workflow execution started with ID: $EXECUTION_ID"

# Wait for execution to complete
echo "⏳ Waiting for execution to complete..."
MAX_WAIT=60
WAIT_TIME=0

while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    STATUS_RESPONSE=$(curl -s "http://localhost:5678/api/v1/executions/$EXECUTION_ID")
    
    FINISHED=$(echo "$STATUS_RESPONSE" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    if 'data' in data and 'finished' in data['data']:
        print('true' if data['data']['finished'] else 'false')
    else:
        print('false')
except:
    print('false')
")
    
    if [ "$FINISHED" = "true" ]; then
        echo "🎉 Workflow execution completed!"
        break
    fi
    
    sleep 5
    WAIT_TIME=$((WAIT_TIME + 5))
    echo "⏳ Still running... (${WAIT_TIME}s)"
done

if [ $WAIT_TIME -ge $MAX_WAIT ]; then
    echo "⚠️ Execution timeout - check n8n interface for details"
fi

echo ""
echo "📋 Workflow ID: $WORKFLOW_ID"
echo "📋 Execution ID: $EXECUTION_ID"
echo "✅ Import and execution process completed!"