#!/usr/bin/env python3
"""
Script to delete duplicate n8n workflows
"""

import subprocess
import json

def run_curl_command(url, method="GET", data=None):
    """Run a curl command and return the result"""
    cmd = ["curl", "-s"]
    
    if method == "DELETE":
        cmd.extend(["-X", "DELETE"])
    
    if data:
        cmd.extend(["-H", "Content-Type: application/json", "-d", json.dumps(data)])
    
    cmd.append(url)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"

def get_workflows():
    """Get all workflows from n8n"""
    success, stdout, stderr = run_curl_command("http://localhost:5678/rest/workflows")
    
    if not success:
        print(f"❌ Failed to get workflows: {stderr}")
        return []
    
    try:
        data = json.loads(stdout)
        workflows = data if isinstance(data, list) else data.get('data', [])
        return workflows
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return []

def delete_workflow(workflow_id):
    """Delete a workflow by ID"""
    success, stdout, stderr = run_curl_command(f"http://localhost:5678/rest/workflows/{workflow_id}", method="DELETE")
    
    if success:
        print(f"✅ Successfully deleted workflow {workflow_id}")
        return True
    else:
        print(f"❌ Failed to delete workflow {workflow_id}: {stderr}")
        return False

def main():
    print("🗑️ N8N WORKFLOW CLEANUP SCRIPT")
    print("=" * 50)
    
    # Get all workflows
    workflows = get_workflows()
    if not workflows:
        print("❌ No workflows found or unable to connect to n8n")
        return
    
    # Find Shopware workflows
    shopware_workflows = [w for w in workflows if 'shopware' in w.get('name', '').lower()]
    
    print(f"📊 Found {len(shopware_workflows)} Shopware workflows:")
    for w in shopware_workflows:
        print(f"   - {w['name']} (ID: {w['id']})")
    print()
    
    # Identify workflows to delete
    to_delete = []
    to_keep = []
    
    # Group workflows by base name
    name_groups = {}
    for w in shopware_workflows:
        base_name = w['name'].replace(' (Fixed)', '').strip()
        if base_name not in name_groups:
            name_groups[base_name] = []
        name_groups[base_name].append(w)
    
    # Determine which to delete
    for base_name, group in name_groups.items():
        if len(group) > 1:
            # Sort by update time, newest first
            group.sort(key=lambda x: x.get('updatedAt', ''), reverse=True)
            
            # Keep the Fixed version if it exists, otherwise keep the newest
            fixed_versions = [w for w in group if '(Fixed)' in w['name']]
            if fixed_versions:
                # Keep the newest Fixed version
                fixed_versions.sort(key=lambda x: x.get('updatedAt', ''), reverse=True)
                to_keep.append(fixed_versions[0])
                # Delete all others
                for w in group:
                    if w['id'] != fixed_versions[0]['id']:
                        to_delete.append(w)
            else:
                # No Fixed version, keep the newest
                to_keep.append(group[0])
                to_delete.extend(group[1:])
        else:
            # Single workflow, keep it
            to_keep.append(group[0])
    
    print("🎯 DELETION PLAN:")
    print(f"   Workflows to keep: {len(to_keep)}")
    for w in to_keep:
        print(f"   🟢 KEEP: {w['name']} (ID: {w['id']})")
    
    print(f"   Workflows to delete: {len(to_delete)}")
    for w in to_delete:
        print(f"   🔴 DELETE: {w['name']} (ID: {w['id']})")
    
    if not to_delete:
        print("✅ No workflows need to be deleted!")
        return
    
    print()
    print("🗑️ STARTING DELETION...")
    
    deleted_count = 0
    for workflow in to_delete:
        if delete_workflow(workflow['id']):
            deleted_count += 1
    
    print()
    print(f"📊 DELETION SUMMARY:")
    print(f"   Successfully deleted: {deleted_count}/{len(to_delete)} workflows")
    
    if deleted_count == len(to_delete):
        print("🎉 All duplicate workflows have been successfully deleted!")
    else:
        print("⚠️ Some workflows could not be deleted. Check the errors above.")

if __name__ == "__main__":
    main()