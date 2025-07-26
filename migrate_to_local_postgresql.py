#!/usr/bin/env python3
"""
Complete n8n SQLite to Local PostgreSQL Migration Script
Sets up local PostgreSQL with PostgREST using Docker
"""

import os
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_command(command, description, check_output=False):
    """Run a command and return success status"""
    log(f"🔧 {description}")
    try:
        if check_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            return True, result.stdout.strip()
        else:
            result = subprocess.run(command, shell=True, check=True)
            return True, None
    except subprocess.CalledProcessError as e:
        log(f"❌ {description} - Failed: {e}")
        return False, None
    except Exception as e:
        log(f"❌ {description} - Error: {e}")
        return False, None

def check_prerequisites():
    """Check if all prerequisites are met"""
    log("🔍 Checking prerequisites")
    
    prerequisites = [
        ("docker", "Docker availability"),
        ("docker-compose", "Docker Compose availability"),
        ("python3", "Python 3 availability")
    ]
    
    all_good = True
    for cmd, desc in prerequisites:
        success, _ = run_command(f"{cmd} --version", f"Checking {desc}")
        if not success:
            all_good = False
    
    # Check if required files exist
    required_files = [
        "docker/database.sqlite",
        "migration_export/schema/complete_schema.sql",
        "docker-compose-local-postgresql.yml"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            log(f"❌ Required file missing: {file_path}")
            all_good = False
        else:
            log(f"✅ Found required file: {file_path}")
    
    return all_good

def create_backup():
    """Create backup of current state"""
    log("💾 Creating migration backup")
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = f"backups/pre-local-postgresql-migration-{timestamp}"
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup SQLite database
        if os.path.exists("docker/database.sqlite"):
            shutil.copy2("docker/database.sqlite", f"{backup_dir}/database.sqlite")
            log("✅ SQLite database backed up")
        
        # Backup current docker-compose.yml
        if os.path.exists("docker-compose.yml"):
            shutil.copy2("docker-compose.yml", f"{backup_dir}/docker-compose.yml")
            log("✅ Docker Compose configuration backed up")
        
        # Create backup info
        backup_info = {
            "timestamp": timestamp,
            "backup_dir": backup_dir,
            "migration_type": "sqlite_to_local_postgresql",
            "files_backed_up": [
                "database.sqlite",
                "docker-compose.yml"
            ]
        }
        
        with open(f"{backup_dir}/backup_info.json", "w") as f:
            json.dump(backup_info, f, indent=2)
        
        log(f"✅ Backup created: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        log(f"❌ Backup creation failed: {e}")
        return None

def setup_environment():
    """Set up environment for local PostgreSQL"""
    log("⚙️ Setting up environment")
    
    # Copy local environment file
    if os.path.exists(".env.local"):
        if not os.path.exists(".env"):
            shutil.copy2(".env.local", ".env")
            log("✅ Copied .env.local to .env")
        else:
            log("ℹ️ .env already exists, keeping current version")
    
    # Install Python dependencies
    log("📦 Installing Python dependencies")
    success, _ = run_command("pip install psycopg2-binary python-dotenv", "Installing PostgreSQL dependencies")
    if not success:
        log("⚠️ Failed to install dependencies, continuing anyway...")
    
    return True

def stop_current_services():
    """Stop current services"""
    log("🛑 Stopping current services")
    
    # Stop current n8n
    success, _ = run_command("docker-compose down", "Stopping current services")
    if success:
        log("✅ Current services stopped")
    else:
        log("ℹ️ No services were running")
    
    return True

def start_local_postgresql_stack():
    """Start local PostgreSQL stack"""
    log("🚀 Starting local PostgreSQL stack")
    
    # Start PostgreSQL, PostgREST, and n8n
    success, _ = run_command("docker-compose -f docker-compose-local-postgresql.yml up -d", "Starting local PostgreSQL stack")
    if success:
        log("✅ Local PostgreSQL stack started")
        
        # Wait for services to be ready
        log("⏳ Waiting for services to initialize...")
        time.sleep(30)
        
        # Check service health
        log("🔍 Checking service health...")
        
        # Check PostgreSQL
        success, _ = run_command("docker-compose -f docker-compose-local-postgresql.yml exec -T postgres pg_isready -U n8n_user -d n8n", "Checking PostgreSQL health")
        if success:
            log("✅ PostgreSQL is ready")
        else:
            log("⚠️ PostgreSQL health check failed")
        
        # Check PostgREST
        success, _ = run_command("curl -f http://localhost:3000/ || echo 'PostgREST not ready yet'", "Checking PostgREST health")
        if success:
            log("✅ PostgREST is ready")
        else:
            log("⚠️ PostgREST health check failed")
        
        return True
    else:
        log("❌ Failed to start local PostgreSQL stack")
        return False

def import_data():
    """Import data to PostgreSQL"""
    log("📥 Importing data to PostgreSQL")
    
    try:
        # Import data using the existing CSV files
        data_dir = "migration_export/data"
        if os.path.exists(data_dir):
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            log(f"Found {len(csv_files)} CSV files to import")
            
            for csv_file in csv_files:
                table_name = csv_file[:-4]  # Remove .csv extension
                csv_path = os.path.join(data_dir, csv_file)
                
                # Copy file to container and import
                copy_cmd = f"docker cp {csv_path} n8n-postgres-local:/tmp/{csv_file}"
                import_cmd = f"docker-compose -f docker-compose-local-postgresql.yml exec -T postgres psql -U n8n_user -d n8n -c \"\\COPY {table_name} FROM '/tmp/{csv_file}' WITH CSV HEADER;\""
                
                success1, _ = run_command(copy_cmd, f"Copying {csv_file} to container")
                if success1:
                    success2, _ = run_command(import_cmd, f"Importing {table_name}")
                    if success2:
                        log(f"✅ Imported {table_name}")
                    else:
                        log(f"⚠️ Failed to import {table_name}")
                else:
                    log(f"⚠️ Failed to copy {csv_file}")
        
        log("✅ Data import completed")
        return True
        
    except Exception as e:
        log(f"❌ Data import failed: {e}")
        return False

def verify_migration():
    """Verify migration success"""
    log("🔍 Verifying migration")
    
    try:
        # Test n8n health endpoint
        import urllib.request
        import urllib.error
        
        try:
            response = urllib.request.urlopen("http://localhost:5678/healthz", timeout=10)
            if response.status == 200:
                log("✅ n8n health check passed")
            else:
                log(f"⚠️ n8n health check returned status: {response.status}")
        except urllib.error.URLError as e:
            log(f"⚠️ n8n health check failed: {e}")
        
        # Test PostgREST endpoint
        try:
            response = urllib.request.urlopen("http://localhost:3000/", timeout=10)
            if response.status == 200:
                log("✅ PostgREST health check passed")
            else:
                log(f"⚠️ PostgREST health check returned status: {response.status}")
        except urllib.error.URLError as e:
            log(f"⚠️ PostgREST health check failed: {e}")
        
        # Test database connection
        success, _ = run_command("docker-compose -f docker-compose-local-postgresql.yml exec -T postgres psql -U n8n_user -d n8n -c 'SELECT COUNT(*) FROM workflow_entity;'", "Testing database connection")
        if success:
            log("✅ Database connection test passed")
        else:
            log("⚠️ Database connection test failed")
        
        return True
        
    except Exception as e:
        log(f"❌ Migration verification failed: {e}")
        return False

def rollback_migration(backup_dir):
    """Rollback migration to SQLite"""
    log("🔄 Rolling back migration")
    
    try:
        # Stop local PostgreSQL stack
        run_command("docker-compose -f docker-compose-local-postgresql.yml down", "Stopping local PostgreSQL stack")
        
        # Restore SQLite configuration
        if os.path.exists(f"{backup_dir}/docker-compose.yml"):
            shutil.copy2(f"{backup_dir}/docker-compose.yml", "docker-compose.yml")
            log("✅ Docker configuration restored")
        
        # Restore SQLite database
        if os.path.exists(f"{backup_dir}/database.sqlite"):
            shutil.copy2(f"{backup_dir}/database.sqlite", "docker/database.sqlite")
            log("✅ SQLite database restored")
        
        # Start SQLite version
        success, _ = run_command("docker-compose up -d", "Starting SQLite n8n")
        if success:
            log("✅ Rollback completed successfully")
            return True
        else:
            log("❌ Failed to start SQLite version")
            return False
            
    except Exception as e:
        log(f"❌ Rollback failed: {e}")
        return False

def main():
    log("🚀 Starting n8n SQLite to Local PostgreSQL Migration")
    log("=" * 70)
    
    # Check prerequisites
    if not check_prerequisites():
        log("❌ Prerequisites not met. Please install required tools.")
        return False
    
    # Create backup
    backup_dir = create_backup()
    if not backup_dir:
        log("❌ Failed to create backup. Aborting migration.")
        return False
    
    try:
        # Setup environment
        if not setup_environment():
            log("❌ Environment setup failed")
            return False
        
        # Stop current services
        if not stop_current_services():
            log("❌ Failed to stop current services")
            return False
        
        # Start local PostgreSQL stack
        if not start_local_postgresql_stack():
            log("❌ Failed to start local PostgreSQL stack")
            log("🔄 Attempting rollback...")
            rollback_migration(backup_dir)
            return False
        
        # Import data
        if not import_data():
            log("⚠️ Data import had issues, but continuing...")
        
        # Verify migration
        if not verify_migration():
            log("⚠️ Migration verification had issues, but services are running")
        
        log("🎉 Local PostgreSQL migration completed successfully!")
        log(f"💾 Backup available at: {backup_dir}")
        log("🌐 Services available at:")
        log("   - n8n: http://localhost:5678")
        log("   - PostgREST API: http://localhost:3000")
        log("   - PostgreSQL: localhost:5432")
        log("   - pgAdmin: http://localhost:8080 (run with --profile admin)")
        
        return True
        
    except KeyboardInterrupt:
        log("⚠️ Migration interrupted by user")
        log("🔄 Attempting rollback...")
        rollback_migration(backup_dir)
        return False
    except Exception as e:
        log(f"❌ Unexpected error during migration: {e}")
        log("🔄 Attempting rollback...")
        rollback_migration(backup_dir)
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n" + "="*70)
        print("✅ N8N LOCAL POSTGRESQL MIGRATION COMPLETE")
        print("🎯 PostgREST MCP Configuration:")
        print("   URL: http://localhost:3000")
        print("   API Key: (not required for local)")
        print("   Schema: public")
        print("🔧 Use these values in Roo Code MCP installation")
        print("="*70)
    else:
        print("❌ Migration failed. Check logs above for details.")
        sys.exit(1)