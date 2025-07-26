# n8n SQLite to Supabase PostgreSQL Migration Guide

## Overview
This guide walks you through migrating your n8n instance from SQLite to Supabase PostgreSQL with MCP server integration for enhanced AI interaction capabilities.

## Prerequisites
- Existing n8n SQLite setup (✅ Complete)
- Data export completed (✅ Complete - 185 rows from 13 tables)
- Supabase account
- Node.js and npm installed

## Step 1: Set Up Supabase PostgreSQL Instance

### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up/login to your account
3. Click "New Project"
4. Fill in project details:
   - **Name**: `n8n-production`
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to your location
5. Wait for project creation (2-3 minutes)

### 1.2 Get Connection Details
After project creation, go to **Settings > Database**:
- **Host**: `db.[project-ref].supabase.co`
- **Port**: `5432`
- **Database**: `postgres`
- **Username**: `postgres`
- **Password**: [your-generated-password]

### 1.3 Configure Database Access
1. Go to **Settings > API**
2. Note your:
   - **Project URL**: `https://[project-ref].supabase.co`
   - **API Key (anon)**: For public access
   - **API Key (service_role)**: For admin access (keep secret!)

## Step 2: Install Supabase MCP Server

### 2.1 Install the PostgREST MCP Server
```bash
# Install PostgREST MCP server globally
npm install -g @supabase-community/mcp-server-postgrest

# Or install locally in your project
npm install @supabase-community/mcp-server-postgrest
```

### 2.2 Configure MCP Server
Create MCP configuration file:

```json
{
  "mcpServers": {
    "postgrest": {
      "command": "npx",
      "args": ["@supabase-community/mcp-server-postgrest"],
      "env": {
        "POSTGREST_URL": "https://[your-project-ref].supabase.co/rest/v1",
        "POSTGREST_API_KEY": "[your-service-role-key]",
        "POSTGREST_SCHEMA": "public"
      }
    }
  }
}
```

## Step 3: Create PostgreSQL Schema in Supabase

### 3.1 Access Supabase SQL Editor
1. Go to your Supabase dashboard
2. Navigate to **SQL Editor**
3. Create a new query

### 3.2 Run Schema Creation
Execute the exported schema:
```sql
-- Copy content from migration_export/schema/complete_schema.sql
-- and paste it into the SQL editor, then run it
```

## Step 4: Import Data to PostgreSQL

### 4.1 Using Supabase Dashboard
1. Go to **Table Editor** in Supabase
2. For each table with data, use **Insert > Import data**
3. Upload the corresponding CSV files from `migration_export/data/`

### 4.2 Using SQL Commands (Alternative)
```sql
-- Example for importing workflow_entity data
-- You'll need to adapt this for each table
COPY workflow_entity FROM 'path/to/workflow_entity.csv' WITH CSV HEADER;
```

## Step 5: Update n8n Configuration

### 5.1 Update Docker Compose
Update your `docker-compose.yml`:

```yaml
services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n-production
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_RUNNERS_ENABLED=true
      - N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
      - NODE_ENV=production
      # PostgreSQL Configuration
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=db.[your-project-ref].supabase.co
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=postgres
      - DB_POSTGRESDB_USER=postgres
      - DB_POSTGRESDB_PASSWORD=[your-database-password]
      - DB_POSTGRESDB_SSL_ENABLED=true
    volumes:
      - n8n_data:/home/node/.n8n
      - n8n_files:/home/node/.n8n/binaryData
      - ./workflows:/home/node/.n8n/workflows:ro
    networks:
      - n8n-network
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  n8n_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${PWD}/docker
  n8n_files:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${PWD}/docker/binaryData

networks:
  n8n-network:
    driver: bridge
```

### 5.2 Environment Variables
Create a `.env` file:
```env
# Supabase Configuration
SUPABASE_URL=https://[your-project-ref].supabase.co
SUPABASE_SERVICE_ROLE_KEY=[your-service-role-key]
SUPABASE_ANON_KEY=[your-anon-key]

# Database Configuration
DB_POSTGRESDB_HOST=db.[your-project-ref].supabase.co
DB_POSTGRESDB_PASSWORD=[your-database-password]
```

## Step 6: Configure MCP Integration

### 6.1 Update VSCode Settings
Add PostgREST MCP server to your `.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "postgrest": {
      "command": "npx",
      "args": ["@supabase-community/mcp-server-postgrest"],
      "env": {
        "POSTGREST_URL": "https://[your-project-ref].supabase.co/rest/v1",
        "POSTGREST_API_KEY": "[your-service-role-key]",
        "POSTGREST_SCHEMA": "public"
      }
    }
  }
}
```

### 6.2 Test MCP Connection
The PostgREST MCP server provides tools for:
- Direct database queries and operations
- CRUD operations (Create, Read, Update, Delete)
- Complex filtering and sorting
- Real-time subscriptions
- Schema introspection
- Automatic API endpoint generation

## Step 7: Migration Execution

### 7.1 Create Backup
```bash
# Backup current SQLite database
cp docker/database.sqlite backups/pre-migration-backup-$(date +%Y%m%d-%H%M%S).sqlite
```

### 7.2 Stop n8n
```bash
docker-compose down
```

### 7.3 Update Configuration
1. Update `docker-compose.yml` with PostgreSQL settings
2. Ensure all environment variables are set

### 7.4 Start with PostgreSQL
```bash
docker-compose up -d
```

### 7.5 Verify Migration
1. Check container logs: `docker-compose logs -f`
2. Access n8n at http://localhost:5678
3. Verify all workflows are present
4. Test workflow execution

## Step 8: Post-Migration Tasks

### 8.1 Update Python Scripts
Update existing scripts to use PostgreSQL:
- Replace `sqlite3` with `psycopg2` or `asyncpg`
- Update connection strings
- Modify SQL syntax for PostgreSQL compatibility

### 8.2 Test MCP Integration
Test the PostgREST MCP server functionality:
- Database queries through MCP
- CRUD operations via natural language
- Real-time data monitoring
- Schema operations

See [`POSTGREST_MCP_SETUP.md`](POSTGREST_MCP_SETUP.md) for detailed configuration.

### 8.3 Performance Optimization
1. Create indexes for frequently queried columns
2. Configure connection pooling
3. Set up monitoring and alerts

## Rollback Plan

If migration fails:

### 8.1 Quick Rollback
```bash
# Stop PostgreSQL version
docker-compose down

# Restore original docker-compose.yml
git checkout docker-compose.yml

# Start SQLite version
docker-compose up -d
```

### 8.2 Data Recovery
```bash
# Restore SQLite database if needed
cp backups/pre-migration-backup-[timestamp].sqlite docker/database.sqlite
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check Supabase project status
   - Verify connection credentials
   - Ensure SSL is enabled

2. **Schema Errors**
   - Review PostgreSQL logs
   - Check data type compatibility
   - Verify foreign key constraints

3. **MCP Server Issues**
   - Check environment variables
   - Verify API keys
   - Review MCP server logs

### Support Resources
- [Supabase Documentation](https://supabase.com/docs)
- [n8n PostgreSQL Setup](https://docs.n8n.io/hosting/configuration/database/)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)

## Benefits After Migration

### Enhanced AI Capabilities
- Structured database operations through MCP
- Real-time workflow monitoring
- Advanced analytics and reporting
- Better error handling and debugging

### Improved Performance
- Better concurrency handling
- Advanced query optimization
- Scalable architecture
- Built-in backup and recovery

### Future-Proof Architecture
- Cloud-native database
- API-first approach
- Real-time capabilities
- Advanced security features

---

**Next Steps**: Follow this guide step by step, and you'll have a fully migrated n8n instance with enhanced AI interaction capabilities through the Supabase MCP server.