#!/usr/bin/env python3
"""
PostgreSQL Database Import Script
Directly inserts workflow into the n8n PostgreSQL database.
"""

import json
import uuid
import os
from datetime import datetime
import sys

# Configuration
WORKFLOW_FILE = "best_workflow_for_import.json"

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Try to get connection details from environment variables
        db_config = {
            'host': os.getenv('DB_POSTGRESDB_HOST', 'localhost'),
            'port': os.getenv('DB_POSTGRESDB_PORT', '5432'),
            'database': os.getenv('DB_POSTGRESDB_DATABASE', 'postgres'),
            'user': os.getenv('DB_POSTGRESDB_USER', 'postgres'),
            'password': os.getenv('DB_POSTGRESDB_PASSWORD'),
            'sslmode': 'require' if os.getenv('DB_POSTGRESDB_SSL_ENABLED', 'true').lower() == 'true' else 'prefer'
        }
        
        if not db_config['password']:
            log("❌ Database password not found in environment variables")
            log("Please set DB_POSTGRESDB_PASSWORD environment variable")
            return None
        
        log(f"🔌 Connecting to PostgreSQL at {db_config['host']}:{db_config['port']}")
        conn = psycopg2.connect(**db_config)
        return conn
        
    except ImportError:
        log("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
        return None
    except Exception as e:
        log(f"❌ PostgreSQL connection error: {e}")
        return None

def main():
    log("🚀 Starting PostgreSQL Database Import")
    log("=" * 50)
    
    try:
        # Load workflow
        log("📁 Loading workflow file...")
        with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        log(f"Loaded workflow: {workflow_data['name']}")
        
        # Connect to database
        log("🔌 Connecting to PostgreSQL database...")
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Check existing workflows
        cursor.execute("SELECT id, name FROM workflow_entity")
        existing = cursor.fetchall()
        log(f"Found {len(existing)} existing workflows:")
        for wf_id, name in existing:
            log(f"  - {name} (ID: {wf_id})")
        
        # Generate new ID
        new_id = str(uuid.uuid4()).replace('-', '')[:16]
        log(f"Generated new workflow ID: {new_id}")
        
        # Prepare workflow data for database
        now = datetime.utcnow().isoformat() + 'Z'
        
        # Update workflow data with new ID
        workflow_data['id'] = new_id
        workflow_data['createdAt'] = now
        workflow_data['updatedAt'] = now
        workflow_data['active'] = True  # Make it active
        
        # Insert into database
        log("💾 Inserting workflow into database...")
        cursor.execute("""
            INSERT INTO workflow_entity (
                id, name, active, nodes, connections, "createdAt", "updatedAt", settings, "staticData", "versionId", "triggerCount", "isArchived"
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            new_id,
            workflow_data['name'],
            True,  # active = true
            json.dumps(workflow_data['nodes']),
            json.dumps(workflow_data['connections']),
            now,
            now,
            json.dumps(workflow_data.get('settings', {})),
            json.dumps(workflow_data.get('staticData', {})),
            1,  # versionId
            1,  # triggerCount
            False   # isArchived = false
        ))
        
        # Commit changes
        conn.commit()
        log("✅ Workflow successfully inserted into database!")
        
        # Verify insertion
        cursor.execute("SELECT id, name, active FROM workflow_entity WHERE id = %s", (new_id,))
        result = cursor.fetchone()
        if result:
            log(f"✅ Verification successful: {result[1]} (ID: {result[0]}, Active: {result[2]})")
        else:
            log("❌ Verification failed: Workflow not found after insertion")
        
        # Show all workflows
        cursor.execute("SELECT id, name, active FROM workflow_entity")
        all_workflows = cursor.fetchall()
        log(f"📊 Total workflows in database: {len(all_workflows)}")
        for wf_id, name, active in all_workflows:
            status = "✅ Active" if active else "⚪ Inactive"
            log(f"  - {name} (ID: {wf_id}) {status}")
        
        conn.close()
        
        log("🎉 PostgreSQL database import completed successfully!")
        log("🔄 Please refresh your n8n web interface to see the new workflow.")
        
        return True
        
    except FileNotFoundError:
        log(f"❌ Workflow file not found: {WORKFLOW_FILE}")
        return False
    except Exception as e:
        log(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n" + "="*60)
        print("✅ WORKFLOW SUCCESSFULLY ADDED TO POSTGRESQL DATABASE")
        print("🌐 Access: http://localhost:5678")
        print("👤 Login: admin@n8n.local / N8nAdmin123!")
        print("🔄 Refresh the page to see your workflow!")
        print("="*60)
    else:
        print("❌ PostgreSQL database import failed.")