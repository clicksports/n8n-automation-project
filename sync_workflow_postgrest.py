#!/usr/bin/env python3
"""
Sync Workflow via PostgREST
Uses PostgREST API to sync local workflow changes to n8n PostgreSQL database.
"""

import json
import requests
import uuid
from datetime import datetime
import sys

# Configuration
POSTGREST_URL = "http://localhost:3000"
WORKFLOW_FILE = "docker/workflows/shopware-to-qdrant-local.json"
TARGET_WORKFLOW_NAME = "Shopware to Qdrant Product Import (Best Version)"

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def load_workflow():
    """Load workflow from JSON file"""
    try:
        with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        # Update the name to match target
        workflow_data['name'] = TARGET_WORKFLOW_NAME
        
        log(f"✅ Loaded workflow: {workflow_data['name']}")
        log(f"   Nodes: {len(workflow_data.get('nodes', []))}")
        log(f"   Active: {workflow_data.get('active', False)}")
        
        return workflow_data
    except Exception as e:
        log(f"❌ Error loading workflow: {e}")
        return None

def get_existing_workflows():
    """Get existing workflows from PostgREST"""
    try:
        response = requests.get(f"{POSTGREST_URL}/workflow_entity", timeout=10)
        if response.status_code == 200:
            workflows = response.json()
            log(f"✅ Found {len(workflows)} existing workflows")
            return workflows
        else:
            log(f"❌ Failed to get workflows: HTTP {response.status_code}")
            return []
    except Exception as e:
        log(f"❌ Error getting workflows: {e}")
        return []

def find_workflow_by_name(workflows, name):
    """Find workflow by name"""
    for workflow in workflows:
        if workflow.get('name') == name:
            return workflow
    return None

def update_workflow_via_postgrest(workflow_id, workflow_data):
    """Update existing workflow via PostgREST"""
    try:
        # Prepare update data
        update_data = {
            "name": workflow_data["name"],
            "nodes": workflow_data["nodes"],
            "connections": workflow_data["connections"],
            "active": workflow_data.get("active", False),
            "settings": workflow_data.get("settings", {}),
            "staticData": workflow_data.get("staticData", {}),
            "pinData": workflow_data.get("pinData", {}),
            "triggerCount": workflow_data.get("triggerCount", 1),
            "versionId": workflow_data.get("versionId", "1"),
            "updatedAt": datetime.utcnow().isoformat() + 'Z'
        }
        
        response = requests.patch(
            f"{POSTGREST_URL}/workflow_entity?id=eq.{workflow_id}",
            json=update_data,
            headers={
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            updated_workflow = response.json()[0] if response.json() else {}
            log(f"✅ Successfully updated workflow: {updated_workflow.get('name')} (ID: {workflow_id})")
            return updated_workflow
        else:
            log(f"❌ Failed to update workflow: HTTP {response.status_code}")
            log(f"Response: {response.text}")
            return None
            
    except Exception as e:
        log(f"❌ Error updating workflow: {e}")
        return None

def create_workflow_via_postgrest(workflow_data):
    """Create new workflow via PostgREST"""
    try:
        # Generate new ID
        workflow_id = str(uuid.uuid4())
        
        # Prepare create data
        create_data = {
            "id": workflow_id,
            "name": workflow_data["name"],
            "nodes": workflow_data["nodes"],
            "connections": workflow_data["connections"],
            "active": workflow_data.get("active", False),
            "settings": workflow_data.get("settings", {}),
            "staticData": workflow_data.get("staticData", {}),
            "pinData": workflow_data.get("pinData", {}),
            "triggerCount": workflow_data.get("triggerCount", 1),
            "versionId": workflow_data.get("versionId", "1"),
            "createdAt": datetime.utcnow().isoformat() + 'Z',
            "updatedAt": datetime.utcnow().isoformat() + 'Z'
        }
        
        response = requests.post(
            f"{POSTGREST_URL}/workflow_entity",
            json=create_data,
            headers={
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            timeout=30
        )
        
        if response.status_code == 201:
            created_workflow = response.json()[0] if response.json() else {}
            log(f"✅ Successfully created workflow: {created_workflow.get('name')} (ID: {workflow_id})")
            return created_workflow
        else:
            log(f"❌ Failed to create workflow: HTTP {response.status_code}")
            log(f"Response: {response.text}")
            return None
            
    except Exception as e:
        log(f"❌ Error creating workflow: {e}")
        return None

def verify_workflow_sync():
    """Verify the workflow sync was successful"""
    try:
        response = requests.get(
            f"{POSTGREST_URL}/workflow_entity?name=eq.{TARGET_WORKFLOW_NAME}",
            timeout=10
        )
        
        if response.status_code == 200:
            workflows = response.json()
            if workflows:
                workflow = workflows[0]
                log("✅ Workflow verification successful:")
                log(f"   ID: {workflow['id']}")
                log(f"   Name: {workflow['name']}")
                log(f"   Active: {workflow['active']}")
                log(f"   Updated: {workflow['updatedAt']}")
                return True
            else:
                log("❌ Workflow not found after sync")
                return False
        else:
            log(f"❌ Failed to verify workflow: HTTP {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Error verifying workflow: {e}")
        return False

def main():
    log("🚀 Starting PostgREST Workflow Sync")
    log("=" * 60)
    
    # Step 1: Load workflow
    log("📂 Step 1: Loading local workflow file...")
    workflow_data = load_workflow()
    if not workflow_data:
        return False
    
    # Step 2: Get existing workflows
    log("📋 Step 2: Getting existing workflows...")
    existing_workflows = get_existing_workflows()
    
    # Step 3: Check if workflow exists
    log("🔍 Step 3: Checking for existing workflow...")
    existing_workflow = find_workflow_by_name(existing_workflows, TARGET_WORKFLOW_NAME)
    
    if existing_workflow:
        log(f"⚠️ Found existing workflow: {existing_workflow['name']} (ID: {existing_workflow['id']})")
        log("🔄 Step 4: Updating existing workflow...")
        result = update_workflow_via_postgrest(existing_workflow['id'], workflow_data)
    else:
        log("✅ No existing workflow found with target name")
        log("📤 Step 4: Creating new workflow...")
        result = create_workflow_via_postgrest(workflow_data)
    
    if not result:
        return False
    
    # Step 5: Verify sync
    log("🔍 Step 5: Verifying workflow sync...")
    if verify_workflow_sync():
        log("")
        log("🎉 SUCCESS: Workflow sync completed!")
        log("")
        log("🎯 Next Steps:")
        log("1. Go to http://localhost:5678")
        log("2. Sign in to n8n")
        log(f"3. Find '{TARGET_WORKFLOW_NAME}' in your workflows")
        log("4. The workflow should be visible and ready to use!")
        log("")
        log("✨ Your local workflow changes are now synced via PostgREST!")
        return True
    else:
        return False

if __name__ == "__main__":
    success = main()
    if success:
        log("🎉 All operations completed successfully!")
        sys.exit(0)
    else:
        log("❌ Some operations failed. Check the logs above.")
        sys.exit(1)