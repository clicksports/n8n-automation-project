#!/usr/bin/env python3
"""
Clean and Upload Workflow Script (curl-based)
Deletes all Shopware workflows from n8n and uploads the best optimized version.
Uses only built-in Python modules with curl for HTTP requests.
"""

import json
import subprocess
import sys
import time
from datetime import datetime

# Configuration
N8N_BASE_URL = "http://localhost:5678"
WORKFLOW_FILE = "workflows/shopware-optimized-vectorization-workflow-fixed.json"
WORKFLOW_NAME = "Shopware Optimized Vectorization Workflow"

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_curl(method, url, data=None, timeout=10):
    """Run curl command and return response"""
    try:
        cmd = ['curl', '-s', '-X', method]
        
        if data:
            cmd.extend(['-H', 'Content-Type: application/json', '-d', json.dumps(data)])
        
        cmd.append(url)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            try:
                return json.loads(result.stdout) if result.stdout.strip() else {}
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response", "raw": result.stdout}
        else:
            return {"error": f"Curl failed with code {result.returncode}", "stderr": result.stderr}
    except Exception as e:
        return {"error": str(e)}

def get_all_workflows():
    """Get all workflows from n8n"""
    log("Getting all workflows from n8n...")
    response = run_curl('GET', f"{N8N_BASE_URL}/rest/workflows")
    
    if 'error' in response:
        log(f"❌ Error getting workflows: {response['error']}")
        return []
    
    # Handle different response formats
    if isinstance(response, list):
        return response
    elif 'data' in response:
        return response['data']
    else:
        return []

def delete_workflow(workflow_id):
    """Delete a workflow by ID using curl"""
    try:
        # Try REST API first
        result = subprocess.run([
            'curl', '-s', '-X', 'DELETE', '-w', '%{http_code}',
            f'{N8N_BASE_URL}/rest/workflows/{workflow_id}'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and ('200' in result.stdout or '204' in result.stdout):
            return True
        
        # Try API v1 as fallback
        result = subprocess.run([
            'curl', '-s', '-X', 'DELETE', '-w', '%{http_code}',
            f'{N8N_BASE_URL}/api/v1/workflows/{workflow_id}'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and ('200' in result.stdout or '204' in result.stdout):
            return True
            
        log(f"❌ Failed to delete workflow {workflow_id}: HTTP response {result.stdout}")
        return False
    except Exception as e:
        log(f"❌ Error deleting workflow {workflow_id}: {e}")
        return False

def upload_workflow(workflow_data):
    """Upload a workflow to n8n using curl"""
    try:
        # Remove ID and other n8n-specific fields for clean upload
        clean_workflow = {
            "name": workflow_data["name"],
            "nodes": workflow_data["nodes"],
            "connections": workflow_data["connections"],
            "active": False,  # Start inactive for safety
            "settings": workflow_data.get("settings", {}),
            "staticData": workflow_data.get("staticData", {}),
            "tags": workflow_data.get("tags", [])
        }
        
        response = run_curl('POST', f"{N8N_BASE_URL}/rest/workflows", clean_workflow, timeout=15)
        
        if 'error' not in response and 'id' in response:
            log(f"✅ Successfully uploaded workflow: {response.get('name')} (ID: {response.get('id')})")
            return response
        else:
            log(f"❌ Failed to upload workflow: {response.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        log(f"❌ Error uploading workflow: {e}")
        return None

def main():
    log("🚀 Starting Clean and Upload Workflow Process")
    log("=" * 60)
    
    # Step 1: Get all current workflows
    log("📋 Step 1: Getting all current workflows...")
    all_workflows = get_all_workflows()
    
    if not all_workflows:
        log("❌ Could not retrieve workflows. Check if n8n is running.")
        return False
    
    # Step 2: Find Shopware workflows
    log("🔍 Step 2: Identifying Shopware workflows...")
    shopware_workflows = [w for w in all_workflows if 'shopware' in w.get('name', '').lower()]
    
    log(f"Found {len(shopware_workflows)} Shopware workflows:")
    for w in shopware_workflows:
        log(f"  - {w['name']} (ID: {w['id']})")
    
    # Step 3: Delete all Shopware workflows
    if shopware_workflows:
        log("🗑️ Step 3: Deleting all Shopware workflows...")
        deleted_count = 0
        for workflow in shopware_workflows:
            log(f"Deleting: {workflow['name']} (ID: {workflow['id']})")
            if delete_workflow(workflow['id']):
                deleted_count += 1
                log(f"✅ Deleted: {workflow['name']}")
                time.sleep(0.5)  # Small delay between deletions
            else:
                log(f"❌ Failed to delete: {workflow['name']}")
        
        log(f"📊 Deletion Summary: {deleted_count}/{len(shopware_workflows)} workflows deleted")
        
        # Wait a moment for n8n to process deletions
        log("⏳ Waiting for n8n to process deletions...")
        time.sleep(2)
    else:
        log("✅ No Shopware workflows found to delete")
    
    # Step 4: Load and upload the best workflow
    log("📤 Step 4: Loading and uploading the optimized workflow...")
    try:
        with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        # Update the workflow name to be clean and unique
        workflow_data['name'] = WORKFLOW_NAME
        
        log(f"Loaded workflow: {workflow_data['name']}")
        log(f"Nodes: {len(workflow_data.get('nodes', []))}")
        log(f"Version: {workflow_data.get('meta', {}).get('templateCredsSetupCompleted', 'N/A')}")
        
        # Upload the workflow
        uploaded_workflow = upload_workflow(workflow_data)
        
        if uploaded_workflow:
            log("✅ Step 4 Complete: Workflow uploaded successfully!")
            
            # Step 5: Verify upload
            log("🔍 Step 5: Verifying upload...")
            updated_workflows = get_all_workflows()
            shopware_workflows_after = [w for w in updated_workflows if 'shopware' in w.get('name', '').lower()]
            
            log(f"📊 Final Status:")
            log(f"  Total workflows in n8n: {len(updated_workflows)}")
            log(f"  Shopware workflows: {len(shopware_workflows_after)}")
            
            if len(shopware_workflows_after) == 1:
                workflow = shopware_workflows_after[0]
                log(f"✅ SUCCESS: Single clean workflow uploaded!")
                log(f"  Name: {workflow['name']}")
                log(f"  ID: {workflow['id']}")
                log(f"  Active: {workflow['active']}")
                log(f"  Created: {workflow.get('createdAt', 'N/A')}")
                
                # Step 6: Provide activation instructions
                log("🎯 Step 6: Next Steps")
                log("To activate the workflow:")
                log(f"1. Go to {N8N_BASE_URL}")
                log("2. Navigate to Workflows")
                log(f"3. Find '{workflow['name']}'")
                log("4. Click the toggle to activate it")
                log("")
                log("🎉 CLEANUP COMPLETE! You now have a single, optimized Shopware workflow.")
                return True
            else:
                log(f"⚠️ Warning: Expected 1 Shopware workflow, found {len(shopware_workflows_after)}")
                for w in shopware_workflows_after:
                    log(f"  - {w['name']} (ID: {w['id']})")
                return False
        else:
            log("❌ Failed to upload workflow")
            return False
            
    except FileNotFoundError:
        log(f"❌ Workflow file not found: {WORKFLOW_FILE}")
        return False
    except json.JSONDecodeError as e:
        log(f"❌ Invalid JSON in workflow file: {e}")
        return False
    except Exception as e:
        log(f"❌ Error in upload process: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        log("🎉 All operations completed successfully!")
        sys.exit(0)
    else:
        log("❌ Some operations failed. Check the logs above.")
        sys.exit(1)