#!/usr/bin/env python3
"""
SQLite Database Analysis Script
Analyzes the current n8n SQLite database structure and data for migration planning
"""

import sqlite3
import json
from datetime import datetime

# Configuration
DB_PATH = "docker/database.sqlite"

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def analyze_database():
    """Analyze the SQLite database structure and content"""
    log("🔍 Starting SQLite Database Analysis")
    log("=" * 60)
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        log(f"📊 Found {len(tables)} tables:")
        
        analysis_report = {
            "database_path": DB_PATH,
            "analysis_time": datetime.now().isoformat(),
            "tables": {}
        }
        
        for table_name, in tables:
            log(f"\n🔍 Analyzing table: {table_name}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Get sample data (first 3 rows)
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_data = cursor.fetchall()
            
            table_info = {
                "columns": [],
                "row_count": row_count,
                "sample_data": sample_data
            }
            
            log(f"   Columns ({len(columns)}):")
            for col in columns:
                col_info = {
                    "name": col[1],
                    "type": col[2],
                    "not_null": bool(col[3]),
                    "default": col[4],
                    "primary_key": bool(col[5])
                }
                table_info["columns"].append(col_info)
                pk_marker = " (PK)" if col[5] else ""
                null_marker = " NOT NULL" if col[3] else ""
                log(f"     - {col[1]}: {col[2]}{pk_marker}{null_marker}")
            
            log(f"   Row count: {row_count}")
            
            analysis_report["tables"][table_name] = table_info
        
        # Special analysis for workflow_entity table
        if "workflow_entity" in [t[0] for t in tables]:
            log(f"\n📋 Detailed Workflow Analysis:")
            cursor.execute("SELECT id, name, active, createdAt, updatedAt FROM workflow_entity")
            workflows = cursor.fetchall()
            
            log(f"   Total workflows: {len(workflows)}")
            active_count = sum(1 for w in workflows if w[2])
            log(f"   Active workflows: {active_count}")
            log(f"   Inactive workflows: {len(workflows) - active_count}")
            
            log(f"\n   Workflow list:")
            for workflow in workflows:
                status = "✅ Active" if workflow[2] else "⚪ Inactive"
                log(f"     - {workflow[1]} (ID: {workflow[0]}) {status}")
            
            analysis_report["workflow_summary"] = {
                "total": len(workflows),
                "active": active_count,
                "inactive": len(workflows) - active_count,
                "workflows": [
                    {
                        "id": w[0],
                        "name": w[1],
                        "active": bool(w[2]),
                        "created_at": w[3],
                        "updated_at": w[4]
                    } for w in workflows
                ]
            }
        
        conn.close()
        
        # Save analysis report
        with open("sqlite_analysis_report.json", "w") as f:
            json.dump(analysis_report, f, indent=2, default=str)
        
        log(f"\n✅ Analysis complete! Report saved to sqlite_analysis_report.json")
        return analysis_report
        
    except sqlite3.Error as e:
        log(f"❌ Database error: {e}")
        return None
    except Exception as e:
        log(f"❌ Unexpected error: {e}")
        return None

if __name__ == "__main__":
    report = analyze_database()
    if report:
        print("\n" + "="*60)
        print("✅ SQLITE DATABASE ANALYSIS COMPLETE")
        print(f"📊 Tables analyzed: {len(report['tables'])}")
        if 'workflow_summary' in report:
            print(f"📋 Workflows found: {report['workflow_summary']['total']}")
        print("📄 Full report: sqlite_analysis_report.json")
        print("="*60)
    else:
        print("❌ Database analysis failed.")