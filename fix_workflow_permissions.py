#!/usr/bin/env python3
"""
Fix Workflow Permissions Script
Associates workflows with the user's project so they appear in the n8n UI
"""

import psycopg2
import psycopg2.extras
import os
from datetime import datetime

# Configuration
DB_CONFIG = {
    'host': os.getenv('DB_POSTGRESDB_HOST', 'localhost'),
    'port': os.getenv('DB_POSTGRESDB_PORT', '5432'),
    'database': os.getenv('DB_POSTGRESDB_DATABASE', 'n8n'),
    'user': os.getenv('DB_POSTGRESDB_USER', 'n8n_user'),
    'password': os.getenv('DB_POSTGRESDB_PASSWORD', 'n8n_password')
}

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def fix_workflow_permissions():
    """Associate workflows with the user's project"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        log("🔧 Starting workflow permissions fix...")
        
        # Get all workflows
        cursor.execute("SELECT id, name FROM workflow_entity")
        workflows = cursor.fetchall()
        log(f"📊 Found {len(workflows)} workflows")
        
        # Get the project ID
        cursor.execute("SELECT id FROM project WHERE type = 'personal' LIMIT 1")
        project = cursor.fetchone()
        if not project:
            log("❌ No personal project found")
            return False
        
        project_id = project['id']
        log(f"📁 Using project ID: {project_id}")
        
        # Create shared_workflow entries for each workflow
        now = datetime.now().isoformat() + 'Z'
        
        for workflow in workflows:
            workflow_id = workflow['id']
            workflow_name = workflow['name']
            
            # Check if already shared
            cursor.execute(
                "SELECT COUNT(*) FROM shared_workflow WHERE \"workflowId\" = %s",
                (workflow_id,)
            )
            count = cursor.fetchone()[0]
            
            if count > 0:
                log(f"✅ Workflow '{workflow_name}' already shared")
                continue
            
            # Create shared_workflow entry
            cursor.execute("""
                INSERT INTO shared_workflow (
                    "workflowId", "projectId", role, "createdAt", "updatedAt"
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                workflow_id,
                project_id,
                'workflow:owner',
                now,
                now
            ))
            
            log(f"✅ Associated workflow '{workflow_name}' with project")
        
        conn.commit()
        log("🎉 All workflows are now properly associated!")
        return True
        
    except Exception as e:
        log(f"❌ Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = fix_workflow_permissions()
    if success:
        log("🎯 Workflow permissions fixed! Restart n8n to see the workflows.")
    else:
        log("❌ Failed to fix workflow permissions.")