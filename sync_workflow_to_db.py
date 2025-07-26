#!/usr/bin/env python3
"""
Direct Database Workflow Sync Script
Directly inserts the workflow into the n8n PostgreSQL database.
"""

import json
import psycopg2
import psycopg2.extras
import uuid
from datetime import datetime
import sys
import os

# Configuration
DB_CONFIG = {
    'host': os.getenv('DB_POSTGRESDB_HOST', 'localhost'),
    'port': os.getenv('DB_POSTGRESDB_PORT', '5432'),
    'database': os.getenv('DB_POSTGRESDB_DATABASE', 'n8n'),
    'user': os.getenv('DB_POSTGRESDB_USER', 'n8n_user'),
    'password': os.getenv('DB_POSTGRESDB_PASSWORD', 'n8n_password')
}
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

def connect_to_db():
    """Connect to the n8n PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        log("✅ Connected to n8n database")
        return conn
    except Exception as e:
        log(f"❌ Error connecting to database: {e}")
        return None

def get_existing_workflow(conn, name):
    """Check if workflow with same name exists"""
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT id, name, active FROM workflow_entity WHERE name = %s", (name,))
        result = cursor.fetchone()
        
        if result:
            log(f"Found existing workflow: {result['name']} (ID: {result['id']})")
            return dict(result)
        else:
            log("No existing workflow found with the same name")
            return None
    except Exception as e:
        log(f"❌ Error checking existing workflow: {e}")
        return None

def delete_workflow(conn, workflow_id):
    """Delete existing workflow"""
    try:
        cursor = conn.cursor()
        
        # Delete from workflow_entity table
        cursor.execute("DELETE FROM workflow_entity WHERE id = %s", (workflow_id,))
        
        # Delete related executions (optional, for cleanup)
        cursor.execute("DELETE FROM execution_entity WHERE \"workflowId\" = %s", (workflow_id,))
        
        conn.commit()
        log(f"✅ Deleted existing workflow {workflow_id}")
        return True
    except Exception as e:
        log(f"❌ Error deleting workflow: {e}")
        return False

def insert_workflow(conn, workflow_data):
    """Insert workflow into database"""
    try:
        cursor = conn.cursor()
        
        # Generate new ID
        workflow_id = str(uuid.uuid4())
        
        # Prepare workflow data for database
        now = datetime.now().isoformat() + 'Z'
        
        # Clean workflow data (remove n8n-specific fields)
        clean_workflow = {
            "name": workflow_data["name"],
            "nodes": workflow_data["nodes"],
            "connections": workflow_data["connections"],
            "active": workflow_data.get("active", False),
            "settings": workflow_data.get("settings", {}),
            "staticData": workflow_data.get("staticData", {}),
            "pinData": workflow_data.get("pinData", {}),
            "triggerCount": workflow_data.get("triggerCount", 1),
            "versionId": workflow_data.get("versionId", "1")
        }
        
        # Insert into workflow_entity table
        cursor.execute("""
            INSERT INTO workflow_entity (
                id, name, active, nodes, connections, "createdAt", "updatedAt",
                settings, "staticData", "pinData", "triggerCount", "versionId"
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            workflow_id,
            clean_workflow["name"],
            clean_workflow["active"],
            json.dumps(clean_workflow["nodes"]),
            json.dumps(clean_workflow["connections"]),
            now,
            now,
            json.dumps(clean_workflow["settings"]),
            json.dumps(clean_workflow["staticData"]),
            json.dumps(clean_workflow["pinData"]),
            clean_workflow["triggerCount"],
            clean_workflow["versionId"]
        ))
        
        conn.commit()
        log(f"✅ Successfully inserted workflow with ID: {workflow_id}")
        return workflow_id
        
    except Exception as e:
        log(f"❌ Error inserting workflow: {e}")
        return None

def verify_workflow(conn, workflow_id):
    """Verify the workflow was inserted correctly"""
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT id, name, active, "createdAt", "updatedAt"
            FROM workflow_entity
            WHERE id = %s
        """, (workflow_id,))
        
        result = cursor.fetchone()
        if result:
            workflow = dict(result)
            log("✅ Workflow verification successful:")
            log(f"   ID: {workflow['id']}")
            log(f"   Name: {workflow['name']}")
            log(f"   Active: {bool(workflow['active'])}")
            log(f"   Created: {workflow['createdAt']}")
            log(f"   Updated: {workflow['updatedAt']}")
            return True
        else:
            log("❌ Workflow verification failed - not found in database")
            return False
    except Exception as e:
        log(f"❌ Error verifying workflow: {e}")
        return False

def main():
    log("🚀 Starting Direct Database Workflow Sync")
    log("=" * 60)
    
    # Step 1: Load workflow
    log("📂 Step 1: Loading workflow file...")
    workflow_data = load_workflow()
    if not workflow_data:
        return False
    
    # Step 2: Connect to database
    log("🔌 Step 2: Connecting to n8n database...")
    conn = connect_to_db()
    if not conn:
        return False
    
    try:
        # Step 3: Check for existing workflow
        log("🔍 Step 3: Checking for existing workflow...")
        existing = get_existing_workflow(conn, TARGET_WORKFLOW_NAME)
        
        if existing:
            log("🗑️ Step 4: Deleting existing workflow...")
            if not delete_workflow(conn, existing['id']):
                log("⚠️ Warning: Failed to delete existing workflow, continuing anyway...")
        else:
            log("✅ Step 4: No existing workflow to delete")
        
        # Step 5: Insert new workflow
        log("📤 Step 5: Inserting workflow into database...")
        workflow_id = insert_workflow(conn, workflow_data)
        
        if not workflow_id:
            return False
        
        # Step 6: Verify insertion
        log("🔍 Step 6: Verifying workflow insertion...")
        if verify_workflow(conn, workflow_id):
            log("")
            log("🎉 SUCCESS: Workflow sync completed!")
            log("")
            log("🎯 Next Steps:")
            log("1. Restart n8n to pick up the database changes:")
            log("   docker-compose restart n8n")
            log("2. Go to http://localhost:5678")
            log("3. Sign in to n8n")
            log(f"4. Find '{TARGET_WORKFLOW_NAME}' in your workflows")
            log("5. Activate it if needed")
            log("")
            log("✨ Your local workflow changes are now synced to the live n8n instance!")
            return True
        else:
            return False
            
    finally:
        conn.close()
        log("🔌 Database connection closed")

if __name__ == "__main__":
    success = main()
    if success:
        log("🎉 All operations completed successfully!")
        sys.exit(0)
    else:
        log("❌ Some operations failed. Check the logs above.")
        sys.exit(1)