#!/usr/bin/env python3
"""
SQLite to PostgreSQL Data Export Script
Exports all data from n8n SQLite database in PostgreSQL-compatible format
"""

import sqlite3
import json
import os
from datetime import datetime
import csv

# Configuration
DB_PATH = "docker/database.sqlite"
EXPORT_DIR = "migration_export"

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def create_export_directory():
    """Create export directory if it doesn't exist"""
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        log(f"📁 Created export directory: {EXPORT_DIR}")
    
    # Create subdirectories
    subdirs = ["schema", "data", "sql"]
    for subdir in subdirs:
        path = os.path.join(EXPORT_DIR, subdir)
        if not os.path.exists(path):
            os.makedirs(path)

def export_table_schema(cursor, table_name):
    """Export table schema as PostgreSQL CREATE TABLE statement"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    # SQLite to PostgreSQL type mapping
    type_mapping = {
        'INTEGER': 'INTEGER',
        'TEXT': 'TEXT',
        'REAL': 'REAL',
        'BLOB': 'BYTEA',
        'varchar': 'VARCHAR',
        'char': 'CHAR',
        'boolean': 'BOOLEAN',
        'datetime': 'TIMESTAMP',
        'datetime(3)': 'TIMESTAMP(3)',
        'datetime(0)': 'TIMESTAMP(0)',
        'timestamp': 'TIMESTAMP',
        'bigint': 'BIGINT',
        'date': 'DATE'
    }
    
    create_sql = f"CREATE TABLE {table_name} (\n"
    column_definitions = []
    primary_keys = []
    
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        not_null = col[3]
        default_val = col[4]
        is_pk = col[5]
        
        # Map SQLite type to PostgreSQL type
        pg_type = col_type
        for sqlite_type, postgres_type in type_mapping.items():
            if sqlite_type.lower() in col_type.lower():
                pg_type = postgres_type
                break
        
        # Handle specific type patterns
        if '(' in col_type and col_type.startswith(('varchar', 'char')):
            pg_type = col_type.upper()
        elif col_type == 'VARCHAR':
            pg_type = 'TEXT'  # Use TEXT for unlimited VARCHAR
        
        col_def = f"  {col_name} {pg_type}"
        
        if not_null:
            col_def += " NOT NULL"
        
        if default_val is not None:
            col_def += f" DEFAULT {default_val}"
        
        column_definitions.append(col_def)
        
        if is_pk:
            primary_keys.append(col_name)
    
    create_sql += ",\n".join(column_definitions)
    
    if primary_keys:
        create_sql += f",\n  PRIMARY KEY ({', '.join(primary_keys)})"
    
    create_sql += "\n);"
    
    return create_sql

def export_table_data(cursor, table_name):
    """Export table data as JSON and CSV"""
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        log(f"   📊 Table {table_name}: 0 rows (empty)")
        return
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Export as JSON
    json_data = []
    for row in rows:
        row_dict = {}
        for i, value in enumerate(row):
            row_dict[columns[i]] = value
        json_data.append(row_dict)
    
    json_file = os.path.join(EXPORT_DIR, "data", f"{table_name}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, default=str)
    
    # Export as CSV
    csv_file = os.path.join(EXPORT_DIR, "data", f"{table_name}.csv")
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)  # Header
        writer.writerows(rows)
    
    log(f"   📊 Table {table_name}: {len(rows)} rows exported")

def generate_postgresql_import_script():
    """Generate PostgreSQL import script"""
    import_script = """#!/bin/bash
# PostgreSQL Import Script
# Run this script to import data into PostgreSQL

set -e

echo "🚀 Starting PostgreSQL data import..."

# Database connection parameters
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-n8n}"
DB_USER="${DB_USER:-postgres}"

echo "📊 Importing to: $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"

# Create schema
echo "📋 Creating database schema..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f schema/complete_schema.sql

# Import data
echo "📥 Importing data..."
"""
    
    # Add data import commands for each table with data
    data_dir = os.path.join(EXPORT_DIR, "data")
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith('.csv'):
                table_name = file[:-4]  # Remove .csv extension
                import_script += f"""
echo "   Importing {table_name}..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\\COPY {table_name} FROM '{os.path.abspath(os.path.join(data_dir, file))}' WITH CSV HEADER;"
"""
    
    import_script += """
echo "✅ PostgreSQL import completed successfully!"
"""
    
    script_file = os.path.join(EXPORT_DIR, "import_to_postgresql.sh")
    with open(script_file, 'w') as f:
        f.write(import_script)
    
    # Make script executable
    os.chmod(script_file, 0o755)
    log(f"📜 Created import script: {script_file}")

def export_database():
    """Export complete database"""
    log("🚀 Starting SQLite Database Export")
    log("=" * 60)
    
    try:
        # Create export directory
        create_export_directory()
        
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [table[0] for table in cursor.fetchall()]
        
        log(f"📊 Found {len(tables)} tables to export")
        
        # Export schema
        log("📋 Exporting database schema...")
        complete_schema = "-- n8n PostgreSQL Schema\n-- Generated from SQLite database\n\n"
        
        for table_name in tables:
            log(f"   🔧 Exporting schema for: {table_name}")
            schema_sql = export_table_schema(cursor, table_name)
            complete_schema += f"-- Table: {table_name}\n{schema_sql}\n\n"
            
            # Save individual schema file
            schema_file = os.path.join(EXPORT_DIR, "schema", f"{table_name}.sql")
            with open(schema_file, 'w') as f:
                f.write(schema_sql)
        
        # Save complete schema
        complete_schema_file = os.path.join(EXPORT_DIR, "schema", "complete_schema.sql")
        with open(complete_schema_file, 'w') as f:
            f.write(complete_schema)
        
        log(f"✅ Schema exported to: {complete_schema_file}")
        
        # Export data
        log("📥 Exporting table data...")
        export_summary = {
            "export_time": datetime.now().isoformat(),
            "total_tables": len(tables),
            "tables_with_data": 0,
            "total_rows": 0,
            "tables": {}
        }
        
        for table_name in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            export_summary["tables"][table_name] = {
                "row_count": row_count,
                "exported": row_count > 0
            }
            
            if row_count > 0:
                export_summary["tables_with_data"] += 1
                export_summary["total_rows"] += row_count
                export_table_data(cursor, table_name)
            else:
                log(f"   📊 Table {table_name}: 0 rows (skipped)")
        
        # Save export summary
        summary_file = os.path.join(EXPORT_DIR, "export_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(export_summary, f, indent=2)
        
        # Generate import script
        generate_postgresql_import_script()
        
        conn.close()
        
        log("✅ Database export completed successfully!")
        log(f"📊 Summary:")
        log(f"   - Total tables: {export_summary['total_tables']}")
        log(f"   - Tables with data: {export_summary['tables_with_data']}")
        log(f"   - Total rows exported: {export_summary['total_rows']}")
        log(f"📁 Export directory: {EXPORT_DIR}")
        
        return True
        
    except sqlite3.Error as e:
        log(f"❌ Database error: {e}")
        return False
    except Exception as e:
        log(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = export_database()
    if success:
        print("\n" + "="*60)
        print("✅ SQLITE DATABASE EXPORT COMPLETE")
        print(f"📁 Export location: {EXPORT_DIR}")
        print("📋 Files created:")
        print("   - schema/complete_schema.sql (PostgreSQL schema)")
        print("   - data/*.json (JSON data files)")
        print("   - data/*.csv (CSV data files)")
        print("   - import_to_postgresql.sh (Import script)")
        print("   - export_summary.json (Export summary)")
        print("="*60)
    else:
        print("❌ Database export failed.")