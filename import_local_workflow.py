#!/usr/bin/env python3
"""
Import Local Workflow Script
Imports the shopware-to-qdrant-local.json workflow into n8n.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import sys
from datetime import datetime

# Configuration
N8N_BASE_URL = "http://localhost:5678"
WORKFLOW_FILE = "docker/workflows/shopware-to-qdrant-local.json"
TARGET_WORKFLOW_NAME = "Shopware to Qdrant Product Import (Best Version)"

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
        with urllib.request.urlopen(req, timeout=30) as response:
            return {
                'status_code': response.getcode(),
                'data': json.loads(response.read().decode('utf-8')) if response.getcode() in [200, 201] else None
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

def find_existing_workflow(workflows, target_name):
    """Find existing workflow by name"""
    for workflow in workflows:
        if workflow.get('name') == target_name:
            return workflow
    return None

def delete_workflow(workflow_id):
    """Delete a workflow by ID"""
    log(f"Deleting existing workflow {workflow_id}...")
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
        "active": workflow_data.get("active", False),
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

def activate_workflow(workflow_id):
    """Activate a workflow"""
    log(f"Activating workflow {workflow_id}...")
    
    # Update workflow to set active=true
    update_data = {"active": True}
    response = make_request(f"{N8N_BASE_URL}/rest/workflows/{workflow_id}", method="PATCH", data=update_data)
    
    if response['status_code'] == 200:
        log(f"✅ Workflow {workflow_id} activated successfully")
        return True
    else:
        log(f"❌ Failed to activate workflow {workflow_id}: HTTP {response['status_code']}")
        return False

def main():
    log("🚀 Starting Local Workflow Import Process")
    log("=" * 60)
    
    # Step 1: Load the local workflow file
    log("📂 Step 1: Loading local workflow file...")
    try:
        with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        # Update the name to match the target
        workflow_data['name'] = TARGET_WORKFLOW_NAME
        
        log(f"✅ Loaded workflow: {workflow_data['name']}")
        log(f"   Nodes: {len(workflow_data.get('nodes', []))}")
        log(f"   Active: {workflow_data.get('active', False)}")
        
    except FileNotFoundError:
        log(f"❌ Workflow file not found: {WORKFLOW_FILE}")
        return False
    except json.JSONDecodeError as e:
        log(f"❌ Invalid JSON in workflow file: {e}")
        return False
    except Exception as e:
        log(f"❌ Error loading workflow file: {e}")
        return False
    
    # Step 2: Get all current workflows
    log("📋 Step 2: Getting current workflows from n8n...")
    all_workflows = get_all_workflows()
    
    if all_workflows is None:
        log("❌ Could not retrieve workflows. Check if n8n is running.")
        return False
    
    # Step 3: Check for existing workflow with same name
    log("🔍 Step 3: Checking for existing workflow...")
    existing_workflow = find_existing_workflow(all_workflows, TARGET_WORKFLOW_NAME)
    
    if existing_workflow:
        log(f"⚠️ Found existing workflow: {existing_workflow['name']} (ID: {existing_workflow['id']})")
        log("🗑️ Deleting existing workflow to avoid conflicts...")
        
        if not delete_workflow(existing_workflow['id']):
            log("❌ Failed to delete existing workflow. Continuing anyway...")
    else:
        log("✅ No existing workflow found with the same name")
    
    # Step 4: Upload the workflow
    log("📤 Step 4: Uploading workflow to n8n...")
    uploaded_workflow = upload_workflow(workflow_data)
    
    if not uploaded_workflow:
        log("❌ Failed to upload workflow")
        return False
    
    # Step 5: Activate the workflow if it was active in the source
    if workflow_data.get('active', False):
        log("🔄 Step 5: Activating workflow...")
        activate_workflow(uploaded_workflow['id'])
    else:
        log("ℹ️ Step 5: Workflow uploaded as inactive (as specified in source)")
    
    # Step 6: Verify final state
    log("🔍 Step 6: Verifying final state...")
    final_workflows = get_all_workflows()
    target_workflow = find_existing_workflow(final_workflows, TARGET_WORKFLOW_NAME)
    
    if target_workflow:
        log("✅ SUCCESS: Workflow sync completed!")
        log(f"   Name: {target_workflow['name']}")
        log(f"   ID: {target_workflow['id']}")
        log(f"   Active: {target_workflow['active']}")
        log(f"   Created: {target_workflow.get('createdAt', 'N/A')}")
        log(f"   Updated: {target_workflow.get('updatedAt', 'N/A')}")
        
        log("")
        log("🎯 Next Steps:")
        log(f"1. Go to {N8N_BASE_URL}")
        log("2. Navigate to Workflows")
        log(f"3. Find '{target_workflow['name']}'")
        if not target_workflow['active']:
            log("4. Click the toggle to activate it")
        else:
            log("4. Workflow is already active and ready to use!")
        
        log("")
        log("🎉 WORKFLOW SYNC COMPLETE!")
        return True
    else:
        log("❌ Verification failed: Workflow not found after upload")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        log("🎉 All operations completed successfully!")
        sys.exit(0)
    else:
        log("❌ Some operations failed. Check the logs above.")
        sys.exit(1)