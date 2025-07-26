#!/usr/bin/env python3
"""
Supabase MCP Server Setup Script
Installs and configures the Supabase MCP server for n8n integration
"""

import json
import os
import subprocess
import sys
from datetime import datetime

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_command(command, description):
    """Run a command and return success status"""
    log(f"🔧 {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log(f"✅ {description} - Success")
            return True
        else:
            log(f"❌ {description} - Failed: {result.stderr}")
            return False
    except Exception as e:
        log(f"❌ {description} - Error: {e}")
        return False

def install_supabase_mcp():
    """Install PostgREST MCP server"""
    log("📦 Installing PostgREST MCP Server")
    
    # Check if npm is available
    if not run_command("npm --version", "Checking npm availability"):
        log("❌ npm is not available. Please install Node.js and npm first.")
        return False
    
    # Install PostgREST MCP server
    if not run_command("npm install -g @supabase-community/mcp-server-postgrest", "Installing PostgREST MCP server globally"):
        log("⚠️ Global install failed, trying local install...")
        if not run_command("npm install @supabase-community/mcp-server-postgrest", "Installing PostgREST MCP server locally"):
            return False
    
    return True

def create_mcp_config():
    """Create MCP configuration for VSCode"""
    log("⚙️ Creating MCP configuration")
    
    # Read environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    # PostgREST URL is Supabase URL + /rest/v1
    postgrest_url = f"{supabase_url}/rest/v1" if supabase_url else None
    
    if not supabase_url or not supabase_key:
        log("⚠️ Supabase environment variables not found")
        log("Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your .env file")
        
        # Create template configuration
        mcp_config = {
            "mcpServers": {
                "postgrest": {
                    "command": "npx",
                    "args": ["@supabase-community/mcp-server-postgrest"],
                    "env": {
                        "POSTGREST_URL": "[your-supabase-url]/rest/v1",
                        "POSTGREST_API_KEY": "[your-service-role-key]",
                        "POSTGREST_SCHEMA": "public"
                    }
                }
            }
        }
    else:
        # Create actual configuration
        mcp_config = {
            "mcpServers": {
                "postgrest": {
                    "command": "npx",
                    "args": ["@supabase-community/mcp-server-postgrest"],
                    "env": {
                        "POSTGREST_URL": postgrest_url,
                        "POSTGREST_API_KEY": supabase_key,
                        "POSTGREST_SCHEMA": "public"
                    }
                }
            }
        }
    
    # Ensure .vscode directory exists
    vscode_dir = ".vscode"
    if not os.path.exists(vscode_dir):
        os.makedirs(vscode_dir)
        log(f"📁 Created {vscode_dir} directory")
    
    # Read existing settings or create new
    settings_file = os.path.join(vscode_dir, "settings.json")
    settings = {}
    
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            log("📄 Loaded existing VSCode settings")
        except json.JSONDecodeError:
            log("⚠️ Invalid JSON in existing settings, creating new")
            settings = {}
    
    # Update settings with MCP configuration
    if "mcp.servers" not in settings:
        settings["mcp.servers"] = {}
    
    settings["mcp.servers"].update(mcp_config["mcpServers"])
    
    # Write updated settings
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    
    log(f"✅ MCP configuration saved to {settings_file}")
    return True

def create_requirements_file():
    """Create requirements.txt for PostgreSQL dependencies"""
    log("📝 Creating requirements.txt for PostgreSQL")
    
    requirements = [
        "psycopg2-binary>=2.9.0",
        "python-dotenv>=0.19.0",
        "asyncpg>=0.27.0",  # For async PostgreSQL operations
        "sqlalchemy>=1.4.0",  # For ORM operations if needed
    ]
    
    with open("requirements-postgresql.txt", "w") as f:
        f.write("\n".join(requirements))
        f.write("\n")
    
    log("✅ Created requirements-postgresql.txt")
    return True

def test_mcp_connection():
    """Test MCP server connection"""
    log("🧪 Testing MCP server connection")
    
    # This is a basic test - in practice, you'd need to test with actual MCP client
    if run_command("npx @supabase-community/mcp-server-postgrest --help", "Testing PostgREST MCP server availability"):
        log("✅ PostgREST MCP server is available")
        return True
    else:
        log("❌ PostgREST MCP server test failed")
        return False

def main():
    log("🚀 Starting Supabase MCP Server Setup")
    log("=" * 60)
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Install Supabase MCP server
    if install_supabase_mcp():
        success_count += 1
    
    # Step 2: Create MCP configuration
    if create_mcp_config():
        success_count += 1
    
    # Step 3: Create requirements file
    if create_requirements_file():
        success_count += 1
    
    # Step 4: Test MCP connection
    if test_mcp_connection():
        success_count += 1
    
    log(f"\n📊 Setup Summary: {success_count}/{total_steps} steps completed")
    
    if success_count == total_steps:
        log("🎉 PostgREST MCP Server setup completed successfully!")
        log("\n📋 Next Steps:")
        log("1. Set up your Supabase project and get credentials")
        log("2. Update .env file with Supabase credentials")
        log("3. Install PostgreSQL dependencies: pip install -r requirements-postgresql.txt")
        log("4. Run the migration: python3 migrate_to_postgresql.py")
        log("5. See POSTGREST_MCP_SETUP.md for detailed configuration")
        return True
    else:
        log("⚠️ Some setup steps failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n" + "="*60)
        print("✅ POSTGREST MCP SERVER SETUP COMPLETE")
        print("🔧 PostgREST MCP configuration added to .vscode/settings.json")
        print("📦 Dependencies listed in requirements-postgresql.txt")
        print("📖 See POSTGREST_MCP_SETUP.md for detailed configuration")
        print("📖 Follow SUPABASE_MIGRATION_GUIDE.md for migration steps")
        print("="*60)
    else:
        print("❌ PostgREST MCP server setup failed.")