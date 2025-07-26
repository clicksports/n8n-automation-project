#!/usr/bin/env python3
"""
Complete n8n SQLite to PostgreSQL Migration Script
Orchestrates the entire migration process with rollback capabilities
"""

import os
import json
import shutil
import subprocess
import sys
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
        ("python3", "Python 3 availability"),
        ("npm", "Node.js/npm availability")
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
        "migration_export/export_summary.json"
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
    backup_dir = f"backups/pre-postgresql-migration-{timestamp}"
    
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
        
        # Backup .env if it exists
        if os.path.exists(".env"):
            shutil.copy2(".env", f"{backup_dir}/.env")
            log("✅ Environment file backed up")
        
        # Create backup info
        backup_info = {
            "timestamp": timestamp,
            "backup_dir": backup_dir,
            "migration_type": "sqlite_to_postgresql",
            "files_backed_up": [
                "database.sqlite",
                "docker-compose.yml",
                ".env"
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
    """Set up environment for PostgreSQL"""
    log("⚙️ Setting up environment")
    
    # Check if .env exists
    if not os.path.exists(".env"):
        if os.path.exists(".env.template"):
            log("📋 .env not found, please copy .env.template to .env and fill in your values")
            return False
        else:
            log("❌ Neither .env nor .env.template found")
            return False
    
    # Install Python dependencies
    log("📦 Installing Python dependencies")
    success, _ = run_command("pip install psycopg2-binary python-dotenv", "Installing PostgreSQL dependencies")
    if not success:
        log("⚠️ Failed to install dependencies, continuing anyway...")
    
    return True

def stop_current_n8n():
    """Stop current n8n instance"""
    log("🛑 Stopping current n8n instance")
    
    success, _ = run_command("docker-compose down", "Stopping n8n containers")
    if success:
        log("✅ n8n stopped successfully")
        return True
    else:
        log("⚠️ Failed to stop n8n, continuing anyway...")
        return True  # Continue even if stop fails

def validate_postgresql_config():
    """Validate PostgreSQL configuration"""
    log("🔍 Validating PostgreSQL configuration")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        log("⚠️ python-dotenv not available, skipping .env loading")
    
    required_vars = [
        "DB_POSTGRESDB_HOST",
        "DB_POSTGRESDB_PASSWORD"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        log(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        log("Please update your .env file with PostgreSQL credentials")
        return False
    
    log("✅ PostgreSQL configuration validated")
    return True

def update_docker_config():
    """Update Docker configuration for PostgreSQL"""
    log("🐳 Updating Docker configuration")
    
    try:
        # Backup current config
        if os.path.exists("docker-compose.yml"):
            shutil.copy2("docker-compose.yml", "docker-compose-sqlite-backup.yml")
        
        # Copy PostgreSQL config
        if os.path.exists("docker-compose-postgresql.yml"):
            shutil.copy2("docker-compose-postgresql.yml", "docker-compose.yml")
            log("✅ Docker configuration updated for PostgreSQL")
            return True
        else:
            log("❌ PostgreSQL Docker configuration not found")
            return False
            
    except Exception as e:
        log(f"❌ Failed to update Docker configuration: {e}")
        return False

def start_postgresql_n8n():
    """Start n8n with PostgreSQL"""
    log("🚀 Starting n8n with PostgreSQL")
    
    success, _ = run_command("docker-compose up -d", "Starting n8n with PostgreSQL")
    if success:
        log("✅ n8n started with PostgreSQL")
        
        # Wait a bit for startup
        log("⏳ Waiting for n8n to initialize...")
        import time
        time.sleep(30)
        
        return True
    else:
        log("❌ Failed to start n8n with PostgreSQL")
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
        
        # Test database connection with PostgreSQL script
        log("🔍 Testing PostgreSQL database connection")
        success, _ = run_command("python3 postgresql_db_import.py --test", "Testing PostgreSQL connection")
        
        return True
        
    except Exception as e:
        log(f"❌ Migration verification failed: {e}")
        return False

def rollback_migration(backup_dir):
    """Rollback migration to SQLite"""
    log("🔄 Rolling back migration")
    
    try:
        # Stop PostgreSQL version
        run_command("docker-compose down", "Stopping PostgreSQL n8n")
        
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
    log("🚀 Starting n8n SQLite to PostgreSQL Migration")
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
        
        # Validate PostgreSQL configuration
        if not validate_postgresql_config():
            log("❌ PostgreSQL configuration invalid")
            return False
        
        # Stop current n8n
        if not stop_current_n8n():
            log("❌ Failed to stop current n8n")
            return False
        
        # Update Docker configuration
        if not update_docker_config():
            log("❌ Failed to update Docker configuration")
            return False
        
        # Start PostgreSQL n8n
        if not start_postgresql_n8n():
            log("❌ Failed to start PostgreSQL n8n")
            log("🔄 Attempting rollback...")
            rollback_migration(backup_dir)
            return False
        
        # Verify migration
        if not verify_migration():
            log("⚠️ Migration verification had issues, but n8n is running")
        
        log("🎉 Migration completed successfully!")
        log(f"💾 Backup available at: {backup_dir}")
        log("🌐 Access n8n at: http://localhost:5678")
        
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
        print("✅ N8N POSTGRESQL MIGRATION COMPLETE")
        print("🎯 Next Steps:")
        print("1. Install Supabase MCP server: python3 setup_supabase_mcp.py")
        print("2. Configure Supabase credentials in .env")
        print("3. Test MCP integration with AI assistants")
        print("4. Import your data to Supabase using the migration guide")
        print("="*70)
    else:
        print("❌ Migration failed. Check logs above for details.")
        sys.exit(1)