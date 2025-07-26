#!/bin/bash
# n8n SQLite to PostgreSQL Migration - Quick Start Script
# This script provides a guided setup for the migration process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Header
echo -e "${BLUE}"
echo "=================================================================="
echo "🚀 n8n SQLite to PostgreSQL Migration - Quick Start"
echo "=================================================================="
echo -e "${NC}"

# Check prerequisites
log "Checking prerequisites..."

# Check if required commands exist
commands=("docker" "docker-compose" "python3" "pip" "npm")
missing_commands=()

for cmd in "${commands[@]}"; do
    if ! command -v "$cmd" &> /dev/null; then
        missing_commands+=("$cmd")
    fi
done

if [ ${#missing_commands[@]} -ne 0 ]; then
    error "Missing required commands: ${missing_commands[*]}"
    echo "Please install the missing commands and try again."
    exit 1
fi

success "All required commands are available"

# Check if we're in the right directory
if [ ! -f "docker/database.sqlite" ]; then
    error "SQLite database not found at docker/database.sqlite"
    echo "Please run this script from your n8n project directory."
    exit 1
fi

success "Found SQLite database"

# Check if migration files exist
migration_files=("analyze_sqlite_db.py" "export_sqlite_data.py" "migrate_to_postgresql.py" "setup_supabase_mcp.py")
missing_files=()

for file in "${migration_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    error "Missing migration files: ${missing_files[*]}"
    echo "Please ensure all migration files are present."
    exit 1
fi

success "All migration files are present"

# Check if data has been exported
if [ ! -d "migration_export" ]; then
    log "Data not yet exported. Running export now..."
    python3 export_sqlite_data.py
    if [ $? -eq 0 ]; then
        success "Data export completed"
    else
        error "Data export failed"
        exit 1
    fi
else
    success "Data export directory found"
fi

# Check environment configuration
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        warning "No .env file found"
        echo ""
        echo "📋 Please follow these steps:"
        echo "1. Copy .env.template to .env:"
        echo "   cp .env.template .env"
        echo ""
        echo "2. Edit .env and fill in your Supabase credentials:"
        echo "   - SUPABASE_URL=https://[your-project-ref].supabase.co"
        echo "   - SUPABASE_SERVICE_ROLE_KEY=[your-service-role-key]"
        echo "   - DB_POSTGRESDB_HOST=db.[your-project-ref].supabase.co"
        echo "   - DB_POSTGRESDB_PASSWORD=[your-database-password]"
        echo ""
        echo "3. Get these values from your Supabase project dashboard:"
        echo "   - Go to https://supabase.com"
        echo "   - Create a new project or use existing one"
        echo "   - Go to Settings > Database for connection details"
        echo "   - Go to Settings > API for API keys"
        echo ""
        echo "4. Run this script again after configuring .env"
        exit 1
    else
        error "Neither .env nor .env.template found"
        exit 1
    fi
else
    success "Environment file (.env) found"
fi

# Install Python dependencies
log "Installing Python dependencies..."
pip install psycopg2-binary python-dotenv > /dev/null 2>&1
if [ $? -eq 0 ]; then
    success "Python dependencies installed"
else
    warning "Failed to install some Python dependencies, continuing anyway..."
fi

# Show migration options
echo ""
echo -e "${YELLOW}🎯 Migration Options:${NC}"
echo ""
echo "1. 🔍 Analyze current database (already done)"
echo "2. 📤 Export data (already done)"
echo "3. 🚀 Run complete migration to PostgreSQL"
echo "4. 🔧 Setup Supabase MCP server"
echo "5. 📖 View migration guide"
echo ""

# Ask user what they want to do
read -p "What would you like to do? (3/4/5): " choice

case $choice in
    3)
        log "Starting complete migration..."
        echo ""
        warning "This will:"
        echo "- Stop your current n8n instance"
        echo "- Create a backup of your current setup"
        echo "- Switch to PostgreSQL configuration"
        echo "- Start n8n with PostgreSQL"
        echo ""
        read -p "Continue? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            python3 migrate_to_postgresql.py
        else
            log "Migration cancelled"
        fi
        ;;
    4)
        log "Setting up Supabase MCP server..."
        python3 setup_supabase_mcp.py
        ;;
    5)
        log "Opening migration guide..."
        if command -v code &> /dev/null; then
            code SUPABASE_MIGRATION_GUIDE.md
        elif command -v cat &> /dev/null; then
            cat SUPABASE_MIGRATION_GUIDE.md
        else
            echo "Please open SUPABASE_MIGRATION_GUIDE.md in your preferred editor"
        fi
        ;;
    *)
        log "Invalid choice. Please run the script again and choose 3, 4, or 5."
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}=================================================================="
echo "🎉 Quick Start Complete!"
echo "=================================================================="
echo -e "${NC}"
echo "📚 For detailed instructions, see: SUPABASE_MIGRATION_GUIDE.md"
echo "📋 For complete overview, see: MIGRATION_COMPLETE_SUMMARY.md"
echo ""