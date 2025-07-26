#!/usr/bin/env python3
"""
Web Import Workflow Script
Imports workflow directly via n8n web API with authentication.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
from datetime import datetime

# Configuration
N8N_BASE_URL = "http://localhost:5678"
WORKFLOW_FILE = "best_workflow_for_import.json"
EMAIL = "admin@n8n.local"
PASSWORD = "N8nAdmin123!"

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

class N8NWebClient:
    def __init__(self):
        # Create cookie jar to maintain session
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        urllib.request.install_opener(self.opener)
        self.session_token = None

    def make_request(self, url, method="GET", data=None, headers=None):
        """Make HTTP request with session cookies"""
        if headers is None:
            headers = {}
        
        # Add common headers
        headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        if data is not None:
            if isinstance(data, dict):
                data = json.dumps(data).encode('utf-8')
                headers['Content-Type'] = 'application/json'
            elif isinstance(data, str):
                data = data.encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                try:
                    return {
                        'status_code': response.getcode(),
                        'data': json.loads(response_data) if response_data else None,
                        'headers': dict(response.headers)
                    }
                except json.JSONDecodeError:
                    return {
                        'status_code': response.getcode(),
                        'data': response_data,
                        'headers': dict(response.headers)
                    }
        except urllib.error.HTTPError as e:
            error_data = e.read().decode('utf-8') if e.fp else str(e)
            return {
                'status_code': e.code,
                'data': None,
                'error': error_data
            }
        except Exception as e:
            return {
                'status_code': 0,
                'data': None,
                'error': str(e)
            }

    def login(self):
        """Login to n8n web interface"""
        log("Attempting to login to n8n...")
        
        # First, get the login page to establish session
        response = self.make_request(f"{N8N_BASE_URL}/")
        if response['status_code'] != 200:
            log(f"Failed to access n8n homepage: {response['status_code']}")
            return False
        
        # Attempt login
        login_data = {
            "emailOrLdapLoginId": EMAIL,
            "password": PASSWORD
        }
        
        response = self.make_request(f"{N8N_BASE_URL}/rest/login", method="POST", data=login_data)
        
        if response['status_code'] == 200:
            log("✅ Successfully logged in to n8n")
            return True
        else:
            log(f"❌ Login failed: HTTP {response['status_code']}")
            if 'error' in response:
                log(f"Error: {response['error']}")
            return False

    def get_workflows(self):
        """Get all workflows from n8n web interface"""
        log("Getting workflows from web interface...")
        response = self.make_request(f"{N8N_BASE_URL}/rest/workflows")
        
        if response['status_code'] == 200:
            data = response['data']
            workflows = data if isinstance(data, list) else data.get('data', [])
            log(f"Found {len(workflows)} workflows in web interface")
            return workflows
        else:
            log(f"❌ Failed to get workflows: HTTP {response['status_code']}")
            return []

    def create_workflow(self, workflow_data):
        """Create a new workflow via web API"""
        log(f"Creating workflow: {workflow_data['name']}")
        
        response = self.make_request(f"{N8N_BASE_URL}/rest/workflows", method="POST", data=workflow_data)
        
        if response['status_code'] in [200, 201]:
            created_workflow = response['data']
            log(f"✅ Successfully created workflow: {created_workflow.get('name')} (ID: {created_workflow.get('id')})")
            return created_workflow
        else:
            log(f"❌ Failed to create workflow: HTTP {response['status_code']}")
            if 'error' in response:
                log(f"Error: {response['error']}")
            return None

def main():
    log("🚀 Starting Web Import Process")
    log("=" * 50)
    
    # Initialize web client
    client = N8NWebClient()
    
    # Step 1: Login
    if not client.login():
        log("❌ Failed to login. Cannot proceed.")
        return False
    
    # Step 2: Check existing workflows
    existing_workflows = client.get_workflows()
    shopware_workflows = [w for w in existing_workflows if 'shopware' in w.get('name', '').lower()]
    
    if shopware_workflows:
        log(f"Found {len(shopware_workflows)} existing Shopware workflows:")
        for w in shopware_workflows:
            log(f"  - {w['name']} (ID: {w['id']})")
        log("✅ Workflows are already visible in web interface!")
        return True
    
    # Step 3: Load and import workflow
    log("📤 Loading workflow file for import...")
    try:
        with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        log(f"Loaded workflow: {workflow_data['name']}")
        log(f"Nodes: {len(workflow_data.get('nodes', []))}")
        
        # Create the workflow
        created_workflow = client.create_workflow(workflow_data)
        
        if created_workflow:
            log("✅ Workflow successfully imported via web interface!")
            
            # Verify by checking workflows again
            updated_workflows = client.get_workflows()
            shopware_workflows_after = [w for w in updated_workflows if 'shopware' in w.get('name', '').lower()]
            
            log(f"📊 Final Status:")
            log(f"  Total workflows: {len(updated_workflows)}")
            log(f"  Shopware workflows: {len(shopware_workflows_after)}")
            
            if len(shopware_workflows_after) >= 1:
                workflow = shopware_workflows_after[0]
                log(f"✅ SUCCESS: Workflow now visible in web interface!")
                log(f"  Name: {workflow['name']}")
                log(f"  ID: {workflow['id']}")
                log(f"  Active: {workflow.get('active', False)}")
                return True
            else:
                log("⚠️ Warning: Workflow created but not found in list")
                return False
        else:
            log("❌ Failed to create workflow")
            return False
            
    except FileNotFoundError:
        log(f"❌ Workflow file not found: {WORKFLOW_FILE}")
        return False
    except json.JSONDecodeError as e:
        log(f"❌ Invalid JSON in workflow file: {e}")
        return False
    except Exception as e:
        log(f"❌ Error in import process: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        log("🎉 Web import completed successfully!")
        print("\n" + "="*50)
        print("✅ WORKFLOW NOW VISIBLE IN N8N WEB INTERFACE")
        print("🌐 Access: http://localhost:5678")
        print("👤 Login: admin@n8n.local / N8nAdmin123!")
        print("="*50)
    else:
        log("❌ Web import failed. Check the logs above.")