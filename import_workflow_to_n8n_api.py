#!/usr/bin/env python3
"""
Import Workflow to n8n via API
Uses n8n's REST API to import the local workflow file.
"""

import json
import subprocess
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

def run_curl_command(command):
    """Run a curl command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timed out',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def login_to_n8n():
    """Login to n8n and get session cookie"""
    log("🔐 Logging into n8n...")
    
    login_data = {
        "email": "admin@n8n.local",
        "password": "Admin123!"
    }
    
    # Create login command
    login_cmd = f'''curl -s -c cookies.txt -X POST "{N8N_BASE_URL}/rest/login" \
        -H "Content-Type: application/json" \
        -d '{json.dumps(login_data)}' '''
    
    result = run_curl_command(login_cmd)
    
    if result['success']:
        log("✅ Successfully logged into n8n")
        return True
    else:
        log(f"❌ Failed to login: {result['stderr']}")
        return False

def load_workflow():
    """Load workflow from JSON file"""
    try:
        with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        # Update the name to match target
        workflow_data['name'] = TARGET_WORKFLOW_NAME
        
        # Remove n8n-specific fields that shouldn't be in import
        fields_to_remove = ['id', 'createdAt', 'updatedAt', 'versionId']
        for field in fields_to_remove:
            workflow_data.pop(field, None)
        
        log(f"✅ Loaded workflow: {workflow_data['name']}")
        log(f"   Nodes: {len(workflow_data.get('nodes', []))}")
        log(f"   Active: {workflow_data.get('active', False)}")
        
        return workflow_data
    except Exception as e:
        log(f"❌ Error loading workflow: {e}")
        return None

def import_workflow(workflow_data):
    """Import workflow via n8n API"""
    log("📤 Importing workflow via n8n API...")
    
    # Create temporary file with workflow data
    temp_file = "temp_workflow.json"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=2)
        
        # Import workflow using n8n API
        import_cmd = f'''curl -s -b cookies.txt -X POST "{N8N_BASE_URL}/rest/workflows" \
            -H "Content-Type: application/json" \
            -d @{temp_file}'''
        
        result = run_curl_command(import_cmd)
        
        if result['success']:
            try:
                response_data = json.loads(result['stdout'])
                if 'id' in response_data:
                    log(f"✅ Successfully imported workflow with ID: {response_data['id']}")
                    return response_data
                else:
                    log(f"⚠️ Unexpected response: {result['stdout']}")
                    return None
            except json.JSONDecodeError:
                log(f"❌ Invalid JSON response: {result['stdout']}")
                return None
        else:
            log(f"❌ Failed to import workflow: {result['stderr']}")
            log(f"Response: {result['stdout']}")
            return None
            
    except Exception as e:
        log(f"❌ Error during import: {e}")
        return None
    finally:
        # Clean up temp file
        try:
            import os
            os.remove(temp_file)
        except:
            pass

def verify_import():
    """Verify the workflow was imported successfully"""
    log("🔍 Verifying workflow import...")
    
    # Get all workflows
    list_cmd = f'''curl -s -b cookies.txt "{N8N_BASE_URL}/rest/workflows"'''
    
    result = run_curl_command(list_cmd)
    
    if result['success']:
        try:
            workflows = json.loads(result['stdout'])
            if isinstance(workflows, dict) and 'data' in workflows:
                workflows = workflows['data']
            
            # Find our workflow
            target_workflow = None
            for workflow in workflows:
                if workflow.get('name') == TARGET_WORKFLOW_NAME:
                    target_workflow = workflow
                    break
            
            if target_workflow:
                log("✅ Workflow verification successful:")
                log(f"   ID: {target_workflow['id']}")
                log(f"   Name: {target_workflow['name']}")
                log(f"   Active: {target_workflow['active']}")
                return True
            else:
                log("❌ Workflow not found after import")
                return False
                
        except json.JSONDecodeError:
            log(f"❌ Invalid JSON response: {result['stdout']}")
            return False
    else:
        log(f"❌ Failed to verify import: {result['stderr']}")
        return False

def cleanup():
    """Clean up temporary files"""
    try:
        import os
        if os.path.exists("cookies.txt"):
            os.remove("cookies.txt")
    except:
        pass

def main():
    log("🚀 Starting n8n API Workflow Import")
    log("=" * 60)
    
    try:
        # Step 1: Load workflow
        log("📂 Step 1: Loading local workflow file...")
        workflow_data = load_workflow()
        if not workflow_data:
            return False
        
        # Step 2: Login to n8n
        log("🔐 Step 2: Logging into n8n...")
        if not login_to_n8n():
            return False
        
        # Step 3: Import workflow
        log("📤 Step 3: Importing workflow...")
        imported_workflow = import_workflow(workflow_data)
        if not imported_workflow:
            return False
        
        # Step 4: Verify import
        log("🔍 Step 4: Verifying import...")
        if verify_import():
            log("")
            log("🎉 SUCCESS: Workflow imported successfully!")
            log("")
            log("🎯 Next Steps:")
            log("1. Go to http://localhost:5678")
            log("2. Sign in with admin@n8n.local / Admin123!")
            log(f"3. Find '{TARGET_WORKFLOW_NAME}' in your workflows")
            log("4. The workflow should now be visible and ready to use!")
            log("")
            log("✨ Your local workflow is now synced to the live n8n instance!")
            return True
        else:
            return False
            
    finally:
        cleanup()

if __name__ == "__main__":
    success = main()
    if success:
        log("🎉 All operations completed successfully!")
        sys.exit(0)
    else:
        log("❌ Some operations failed. Check the logs above.")
        sys.exit(1)