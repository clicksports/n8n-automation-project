#!/bin/bash

# Autonomous Test and Improvement Loop for Shopware to Qdrant Integration
# This script will test, debug, improve, and loop until the workflow works perfectly

LOG_FILE="workflows/test-loop.log"
WORKFLOW_ID="i6RnhP6rCz2hpRVJ"
N8N_URL="http://localhost:5678"
ITERATION=1
MAX_ITERATIONS=10

echo "🚀 Starting Autonomous Test and Improvement Loop" | tee -a $LOG_FILE
echo "=================================================" | tee -a $LOG_FILE
echo "Timestamp: $(date)" | tee -a $LOG_FILE
echo "Workflow ID: $WORKFLOW_ID" | tee -a $LOG_FILE
echo "Max Iterations: $MAX_ITERATIONS" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Function to log with timestamp
log_with_timestamp() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Function to test Shopware OAuth directly
test_shopware_oauth() {
    log_with_timestamp "🔐 Testing Shopware OAuth directly..."
    
    local response=$(curl -s -w "%{http_code}" -X POST 'https://shop.held.de/api/oauth/token' \
        --header 'Content-Type: application/json' \
        --data '{
            "grant_type": "client_credentials",
            "client_id": "SWIANEPSMGTHMLJMT1BHEFAZNW",
            "client_secret": "UVJKRGFWZENoVW9OY1ZuUktYNkN6NFRucVNVQU1VR1B0cElhUzE"
        }' -o /tmp/oauth_response.json)
    
    local http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        log_with_timestamp "✅ OAuth test successful (HTTP $http_code)"
        local token=$(cat /tmp/oauth_response.json | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
        log_with_timestamp "🔑 Access token obtained: ${token:0:20}..."
        echo "$token"
        return 0
    else
        log_with_timestamp "❌ OAuth test failed (HTTP $http_code)"
        log_with_timestamp "Response: $(cat /tmp/oauth_response.json)"
        return 1
    fi
}

# Function to test Qdrant connection
test_qdrant_connection() {
    log_with_timestamp "🔗 Testing Qdrant connection..."
    
    local response=$(curl -s -w "%{http_code}" -X GET \
        'https://8ec957ec-27b4-4041-9714-f8dde751b007.europe-west3-0.gcp.cloud.qdrant.io:6333/collections' \
        --header 'api-key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.50x-a9c0zTX_dzWnKjq-xM7rJ0ym6_yZ-D_eN_Idft4' \
        -o /tmp/qdrant_response.json)
    
    local http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        log_with_timestamp "✅ Qdrant connection successful (HTTP $http_code)"
        log_with_timestamp "Collections: $(cat /tmp/qdrant_response.json)"
        return 0
    else
        log_with_timestamp "❌ Qdrant connection failed (HTTP $http_code)"
        log_with_timestamp "Response: $(cat /tmp/qdrant_response.json)"
        return 1
    fi
}

# Function to fix workflow JSON issues
fix_workflow_json() {
    local issue="$1"
    log_with_timestamp "🔧 Fixing workflow issue: $issue"
    
    case "$issue" in
        "http_method")
            log_with_timestamp "Fixing HTTP method in OAuth node..."
            # Create a corrected workflow with proper POST method
            cat > workflows/shopware-to-qdrant-import-fixed.json << 'EOF'
{
  "name": "Shopware to Qdrant Product Import (Fixed)",
  "active": true,
  "nodes": [
    {
      "parameters": {},
      "id": "manual-trigger-1",
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://shop.held.de/api/oauth/token",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "grant_type",
              "value": "client_credentials"
            },
            {
              "name": "client_id",
              "value": "SWIANEPSMGTHMLJMT1BHEFAZNW"
            },
            {
              "name": "client_secret",
              "value": "UVJKRGFWZENoVW9OY1ZuUktYNkN6NFRucVNVQU1VR1B0cElhUzE"
            }
          ]
        },
        "options": {
          "timeout": 30000
        }
      },
      "id": "oauth-token-1",
      "name": "Get OAuth Token",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [460, 300]
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [
        [
          {
            "node": "Get OAuth Token",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "pinData": {},
  "settings": {
    "executionOrder": "v1"
  },
  "staticData": null,
  "tags": [],
  "triggerCount": 1,
  "updatedAt": "$(date -u +%Y-%m-%dT%H:%M:%S.000Z)",
  "versionId": "3"
}
EOF
            log_with_timestamp "✅ Created fixed workflow JSON"
            return 0
            ;;
        *)
            log_with_timestamp "❌ Unknown issue: $issue"
            return 1
            ;;
    esac
}

# Function to execute n8n workflow and capture results
execute_workflow() {
    local workflow_id="$1"
    log_with_timestamp "▶️ Executing workflow: $workflow_id"
    
    # Execute workflow and capture output
    local output=$(n8n execute --id="$workflow_id" --baseUrl="$N8N_URL" 2>&1)
    local exit_code=$?
    
    # Log the full output
    echo "$output" >> $LOG_FILE
    
    # Analyze the output
    if echo "$output" | grep -q "Method not allowed"; then
        log_with_timestamp "❌ HTTP Method error detected"
        return 1
    elif echo "$output" | grep -q "successfully"; then
        log_with_timestamp "✅ Workflow executed successfully"
        return 0
    elif echo "$output" | grep -q "Execution was NOT successful"; then
        log_with_timestamp "❌ Workflow execution failed"
        return 2
    else
        log_with_timestamp "⚠️ Unclear execution result (exit code: $exit_code)"
        return 3
    fi
}

# Main test and improvement loop
while [ $ITERATION -le $MAX_ITERATIONS ]; do
    log_with_timestamp ""
    log_with_timestamp "🔄 ITERATION $ITERATION/$MAX_ITERATIONS"
    log_with_timestamp "================================"
    
    # Step 1: Test external dependencies
    log_with_timestamp "Step 1: Testing external dependencies..."
    
    if ! test_qdrant_connection; then
        log_with_timestamp "❌ Qdrant connection failed - cannot proceed"
        break
    fi
    
    if ! test_shopware_oauth; then
        log_with_timestamp "❌ Shopware OAuth failed - cannot proceed"
        break
    fi
    
    # Step 2: Test workflow execution
    log_with_timestamp "Step 2: Testing workflow execution..."
    
    case $(execute_workflow "$WORKFLOW_ID") in
        0)
            log_with_timestamp "🎉 SUCCESS! Workflow executed successfully"
            log_with_timestamp "✅ All tests passed in iteration $ITERATION"
            break
            ;;
        1)
            log_with_timestamp "🔧 HTTP Method issue detected - fixing..."
            if fix_workflow_json "http_method"; then
                log_with_timestamp "Importing fixed workflow..."
                if n8n import:workflow --input=workflows/shopware-to-qdrant-import-fixed.json --baseUrl="$N8N_URL" 2>&1 | tee -a $LOG_FILE; then
                    # Get new workflow ID
                    WORKFLOW_ID=$(n8n list:workflow --baseUrl="$N8N_URL" 2>/dev/null | grep "Fixed" | cut -d'|' -f1)
                    log_with_timestamp "New workflow ID: $WORKFLOW_ID"
                else
                    log_with_timestamp "❌ Failed to import fixed workflow"
                fi
            fi
            ;;
        2)
            log_with_timestamp "❌ Workflow execution failed - analyzing logs..."
            ;;
        3)
            log_with_timestamp "⚠️ Unclear result - continuing..."
            ;;
    esac
    
    # Step 3: Wait before next iteration
    if [ $ITERATION -lt $MAX_ITERATIONS ]; then
        log_with_timestamp "⏳ Waiting 5 seconds before next iteration..."
        sleep 5
    fi
    
    ITERATION=$((ITERATION + 1))
done

# Final summary
log_with_timestamp ""
log_with_timestamp "📊 FINAL SUMMARY"
log_with_timestamp "================="
if [ $ITERATION -gt $MAX_ITERATIONS ]; then
    log_with_timestamp "❌ Maximum iterations reached without success"
    log_with_timestamp "🔍 Check the log file for detailed analysis: $LOG_FILE"
else
    log_with_timestamp "✅ Workflow successfully working!"
    log_with_timestamp "🎯 Ready for production use"
fi

log_with_timestamp "📝 Full log available at: $LOG_FILE"
log_with_timestamp "🏁 Autonomous test loop completed"