#!/usr/bin/env python3
"""
Script to import the updated workflow into n8n and execute it
"""

import json
import requests
import time

def import_workflow():
    """Import the updated workflow into n8n"""
    print("🔄 Importing updated workflow into n8n...")
    
    # Read the updated workflow file
    with open('workflows/shopware-optimized-vectorization-workflow-fixed.json', 'r') as f:
        workflow_data = json.load(f)
    
    # Import workflow via n8n API
    response = requests.post(
        'http://localhost:5678/api/v1/workflows',
        json=workflow_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 201:
        workflow_id = response.json()['data']['id']
        print(f"✅ Workflow imported successfully with ID: {workflow_id}")
        return workflow_id
    else:
        print(f"❌ Failed to import workflow: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def execute_workflow(workflow_id):
    """Execute the workflow"""
    print(f"🚀 Executing workflow {workflow_id}...")
    
    # Execute workflow via manual trigger
    response = requests.post(
        f'http://localhost:5678/api/v1/workflows/{workflow_id}/execute',
        json={},
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        execution_id = response.json()['data']['executionId']
        print(f"✅ Workflow execution started with ID: {execution_id}")
        return execution_id
    else:
        print(f"❌ Failed to execute workflow: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def check_execution_status(execution_id):
    """Check the status of workflow execution"""
    print(f"🔍 Checking execution status for {execution_id}...")
    
    response = requests.get(f'http://localhost:5678/api/v1/executions/{execution_id}')
    
    if response.status_code == 200:
        execution_data = response.json()['data']
        status = execution_data.get('finished', False)
        mode = execution_data.get('mode', 'unknown')
        
        print(f"Status: {'✅ Finished' if status else '⏳ Running'}")
        print(f"Mode: {mode}")
        
        if status:
            # Check if there were any errors
            if execution_data.get('stoppedAt'):
                print(f"Stopped at: {execution_data['stoppedAt']}")
            
            return True
        else:
            return False
    else:
        print(f"❌ Failed to check execution status: {response.status_code}")
        return False

def main():
    print("🧪 N8N WORKFLOW IMPORT AND EXECUTION")
    print("=" * 50)
    
    try:
        # Import the workflow
        workflow_id = import_workflow()
        if not workflow_id:
            return
        
        # Execute the workflow
        execution_id = execute_workflow(workflow_id)
        if not execution_id:
            return
        
        # Wait for execution to complete
        print("⏳ Waiting for execution to complete...")
        max_wait = 60  # Maximum wait time in seconds
        wait_time = 0
        
        while wait_time < max_wait:
            if check_execution_status(execution_id):
                print("🎉 Workflow execution completed!")
                break
            
            time.sleep(5)
            wait_time += 5
            print(f"⏳ Still running... ({wait_time}s)")
        
        if wait_time >= max_wait:
            print("⚠️ Execution timeout - check n8n interface for details")
        
        print(f"\n📋 Workflow ID: {workflow_id}")
        print(f"📋 Execution ID: {execution_id}")
        print("✅ Import and execution process completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to n8n. Make sure it's running on localhost:5678")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()