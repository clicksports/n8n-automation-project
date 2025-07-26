#!/usr/bin/env python3
"""
N8N Workflow Cleanup Script
Helps identify and remove duplicate Shopware workflows
"""

import requests
import json
from datetime import datetime

def get_n8n_workflows():
    """Fetch all workflows from N8N API"""
    try:
        response = requests.get("http://localhost:5678/rest/workflows")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to fetch workflows: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error connecting to N8N: {e}")
        return []

def analyze_shopware_workflows(workflows):
    """Analyze Shopware-related workflows for duplicates"""
    shopware_workflows = []
    
    for workflow in workflows:
        if 'shopware' in workflow.get('name', '').lower():
            shopware_workflows.append(workflow)
    
    print(f"🔍 Found {len(shopware_workflows)} Shopware workflows:")
    print("=" * 60)
    
    for i, workflow in enumerate(shopware_workflows, 1):
        print(f"{i}. ID: {workflow.get('id')}")
        print(f"   Name: {workflow.get('name')}")
        print(f"   Active: {workflow.get('active')}")
        print(f"   Updated: {workflow.get('updatedAt', 'N/A')}")
        print(f"   Tags: {workflow.get('tags', [])}")
        print()
    
    return shopware_workflows

def identify_duplicates(workflows):
    """Identify duplicate workflows based on base names"""
    name_groups = {}
    
    for workflow in workflows:
        # Remove "(Fixed)" suffix to group similar workflows
        base_name = workflow['name'].replace(' (Fixed)', '').strip()
        if base_name not in name_groups:
            name_groups[base_name] = []
        name_groups[base_name].append(workflow)
    
    duplicates = {}
    for base_name, group in name_groups.items():
        if len(group) > 1:
            duplicates[base_name] = sorted(group, key=lambda x: x.get('updatedAt', ''), reverse=True)
    
    return duplicates

def recommend_cleanup(duplicates):
    """Provide cleanup recommendations"""
    print("🎯 CLEANUP RECOMMENDATIONS:")
    print("=" * 60)
    
    for base_name, workflows in duplicates.items():
        print(f"\n📋 Base workflow: '{base_name}'")
        print(f"   Found {len(workflows)} versions:")
        
        for i, workflow in enumerate(workflows):
            status = "🟢 KEEP" if i == 0 else "🔴 REMOVE"
            if "(Fixed)" in workflow['name']:
                status = "🟢 KEEP (IMPROVED VERSION)"
            elif i > 0 and "(Fixed)" not in workflow['name']:
                status = "🔴 REMOVE (OUTDATED)"
            
            print(f"   {status} - {workflow['name']}")
            print(f"     ID: {workflow['id']}")
            print(f"     Updated: {workflow.get('updatedAt', 'N/A')}")
            print(f"     Active: {workflow.get('active')}")

def delete_workflow(workflow_id):
    """Delete a workflow by ID"""
    try:
        response = requests.delete(f"http://localhost:5678/rest/workflows/{workflow_id}")
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Failed to delete workflow {workflow_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error deleting workflow {workflow_id}: {e}")
        return False

def main():
    print("🧹 N8N Workflow Cleanup Tool")
    print("=" * 40)
    print()
    
    # Fetch workflows
    workflows = get_n8n_workflows()
    if not workflows:
        print("❌ No workflows found or unable to connect to N8N")
        return
    
    # Analyze Shopware workflows
    shopware_workflows = analyze_shopware_workflows(workflows)
    if not shopware_workflows:
        print("ℹ️ No Shopware workflows found")
        return
    
    # Identify duplicates
    duplicates = identify_duplicates(shopware_workflows)
    if not duplicates:
        print("✅ No duplicate workflows found!")
        return
    
    # Show recommendations
    recommend_cleanup(duplicates)
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("   - Keep the 'Shopware Optimized Vectorization Workflow (Fixed)' version")
    print("   - Remove the original 'Shopware Optimized Vectorization Workflow'")
    print("   - The Fixed version has frontend URL generation and better reliability")
    print()
    print("⚠️  To actually delete workflows, you'll need to do this manually in the N8N UI")
    print("   or modify this script to include the deletion functionality.")

if __name__ == "__main__":
    main()