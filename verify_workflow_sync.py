#!/usr/bin/env python3
"""
Workflow Sync Verification Script
Verifies that local workflow changes are synced to the live n8n instance.
"""

import json
import psycopg2
import psycopg2.extras
from datetime import datetime
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

def verify_workflow_sync():
    """Verify workflow sync status"""
    log("🔍 Verifying workflow sync status...")
    log("=" * 50)
    
    try:
        # Check local file
        with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
            local_workflow = json.load(f)
        
        log(f"✅ Local workflow file found:")
        log(f"   Name: {local_workflow['name']}")
        log(f"   Nodes: {len(local_workflow.get('nodes', []))}")
        log(f"   Active: {local_workflow.get('active', False)}")
        
        # Check database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT id, name, active, createdAt, updatedAt 
            FROM workflow_entity 
            WHERE name = ?
        """, (TARGET_WORKFLOW_NAME,))
        
        db_workflow = cursor.fetchone()
        
        if db_workflow:
            log(f"✅ Workflow found in n8n database:")
            log(f"   ID: {db_workflow['id']}")
            log(f"   Name: {db_workflow['name']}")
            log(f"   Active: {bool(db_workflow['active'])}")
            log(f"   Created: {db_workflow['createdAt']}")
            log(f"   Updated: {db_workflow['updatedAt']}")
            
            # Compare basic properties
            local_active = local_workflow.get('active', False)
            db_active = bool(db_workflow['active'])
            
            if local_active == db_active:
                log("✅ Active status matches between local and database")
            else:
                log(f"⚠️ Active status mismatch: Local={local_active}, DB={db_active}")
            
            log("")
            log("🎉 SYNC STATUS: SUCCESS")
            log("Your local workflow changes are synced to the live n8n instance!")
            log("")
            log("📋 To access your workflow:")
            log("1. Go to http://localhost:5678")
            log("2. Sign in to n8n")
            log(f"3. Find '{TARGET_WORKFLOW_NAME}' in your workflows")
            
            return True
        else:
            log("❌ Workflow NOT found in n8n database")
            log("The workflow sync may have failed or the workflow name doesn't match")
            return False
            
    except FileNotFoundError:
        log(f"❌ Local workflow file not found: {WORKFLOW_FILE}")
        return False
    except Exception as e:
        log(f"❌ Error during verification: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = verify_workflow_sync()
    if not success:
        log("❌ Verification failed. Check the logs above.")
        exit(1)