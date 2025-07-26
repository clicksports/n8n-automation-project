#!/usr/bin/env python3
"""
Import Best Workflow Script
Uses only standard library to import the best workflow to n8n.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import sys
from datetime import datetime

# Configuration
N8N_BASE_URL = "http://localhost:5678"
WORKFLOW_FILE = "workflows/current_workflow.json"

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def make_request(url, method="GET", data=None, headers=None):
    """Make HTTP request using urllib"""
    if headers is None:
        headers = {}
    
    if data is not None:
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return {
                'status_code': response.getcode(),
                'data': json.loads(response.read().decode('utf-8')) if response.getcode() == 200 else None
            }
    except urllib.error.HTTPError as e:
        return {
            'status_code': e.code,
            'data': None,
            'error': e.read().decode('utf-8') if e.fp else str(e)
        }
    except Exception as e:
        return {
            'status_code': 0,
            'data': None,
            'error': str(e)
        }

def get_all_workflows():
    """Get all workflows from n8n"""
    log("Getting all workflows from n8n...")
    response = make_request(f"{N8N_BASE_URL}/rest/workflows")
    
    if response['status_code'] == 200:
        data = response['data']
        workflows = data if isinstance(data, list) else data.get('data', [])
        log(f"Found {len(workflows)} workflows")
        return workflows
    else:
        log(f"❌ Failed to get workflows: HTTP {response['status_code']}")
        if 'error' in response:
            log(f"Error: {response['error']}")
        return []

def delete_workflow(workflow_id):
    """Delete a workflow by ID"""
    log(f"Deleting workflow {workflow_id}...")
    response = make_request(f"{N8N_BASE_URL}/rest/workflows/{workflow_id}", method="DELETE")
    
    if response['status_code'] in [200, 204]:
        log(f"✅ Deleted workflow {workflow_id}")
        return True
    else:
        log(f"❌ Failed to delete workflow {workflow_id}: HTTP {response['status_code']}")
        return False

def upload_workflow(workflow_data):
    """Upload a workflow to n8n"""
    log(f"Uploading workflow: {workflow_data['name']}")
    
    # Clean the workflow data for upload
    clean_workflow = {
        "name": workflow_data["name"],
        "nodes": workflow_data["nodes"],
        "connections": workflow_data["connections"],
        "active": False,  # Start inactive for safety
        "settings": workflow_data.get("settings", {}),
        "staticData": workflow_data.get("staticData", {}),
        "tags": workflow_data.get("tags", [])
    }
    
    response = make_request(f"{N8N_BASE_URL}/rest/workflows", method="POST", data=clean_workflow)
    
    if response['status_code'] in [200, 201]:
        uploaded_workflow = response['data']
        log(f"✅ Successfully uploaded workflow: {uploaded_workflow.get('name')} (ID: {uploaded_workflow.get('id')})")
        return uploaded_workflow
    else:
        log(f"❌ Failed to upload workflow: HTTP {response['status_code']}")
        if 'error' in response:
            log(f"Error: {response['error']}")
        return None

def main():
    log("🚀 Starting Best Workflow Import Process")
    log("=" * 60)
    
    # Step 1: Get all current workflows
    all_workflows = get_all_workflows()
    
    if all_workflows is None:
        log("❌ Could not retrieve workflows. Check if n8n is running.")
        return False
    
    # Step 2: Find Shopware workflows to clean up
    shopware_workflows = [w for w in all_workflows if 'shopware' in w.get('name', '').lower()]
    
    if shopware_workflows:
        log(f"🗑️ Found {len(shopware_workflows)} existing Shopware workflows to clean up:")
        for w in shopware_workflows:
            log(f"  - {w['name']} (ID: {w['id']})")
        
        # Delete existing Shopware workflows
        deleted_count = 0
        for workflow in shopware_workflows:
            if delete_workflow(workflow['id']):
                deleted_count += 1
        
        log(f"📊 Deleted {deleted_count}/{len(shopware_workflows)} workflows")
    else:
        log("✅ No existing Shopware workflows found")
    
    # Step 3: Load and upload the best workflow
    log("📤 Loading and uploading the best workflow...")
    try:
        with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
            workflow_content = f.read()
        
        # Parse the JSON - it's an array with one workflow
        workflow_array = json.loads(workflow_content)
        if isinstance(workflow_array, list) and len(workflow_array) > 0:
            workflow_data = workflow_array[0]
        else:
            workflow_data = workflow_array
        
        log(f"Loaded workflow: {workflow_data['name']}")
        log(f"Nodes: {len(workflow_data.get('nodes', []))}")
        
        # Upload the workflow
        uploaded_workflow = upload_workflow(workflow_data)
        
        if uploaded_workflow:
            log("✅ Workflow uploaded successfully!")
            
            # Verify upload
            updated_workflows = get_all_workflows()
            shopware_workflows_after = [w for w in updated_workflows if 'shopware' in w.get('name', '').lower()]
            
            log(f"📊 Final Status:")
            log(f"  Total workflows in n8n: {len(updated_workflows)}")
            log(f"  Shopware workflows: {len(shopware_workflows_after)}")
            
            if len(shopware_workflows_after) >= 1:
                workflow = shopware_workflows_after[0]
                log(f"✅ SUCCESS: Clean workflow uploaded!")
                log(f"  Name: {workflow['name']}")
                log(f"  ID: {workflow['id']}")
                log(f"  Active: {workflow['active']}")
                
                log("🎯 Next Steps:")
                log(f"1. Go to {N8N_BASE_URL}")
                log("2. Navigate to Workflows")
                log(f"3. Find '{workflow['name']}'")
                log("4. Click the toggle to activate it")
                log("")
                log("🎉 IMPORT COMPLETE! Your best workflow is now in n8n.")
                return True
            else:
                log(f"⚠️ Warning: No Shopware workflows found after upload")
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