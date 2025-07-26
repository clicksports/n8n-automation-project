# 🏠 Local PostgreSQL + PostgREST Setup Complete

## 🎯 Complete Local Stack

Everything you need to run n8n with PostgreSQL and PostgREST locally using Docker - no cloud dependencies!

### 🐳 Docker Services Included

1. **PostgreSQL 15** - Local database server
2. **PostgREST** - REST API for PostgreSQL 
3. **n8n** - Workflow automation (connected to PostgreSQL)
4. **pgAdmin** - Database management UI (optional)

## 🚀 Quick Start

### 1. Run Local Migration
```bash
# Execute the complete local migration
python3 migrate_to_local_postgresql.py
```

### 2. Configure Roo Code MCP
In the Roo Code installation dialog, use these values:

**PostgREST API URL:**
```
http://localhost:3000
```

**PostgREST API Key:**
```
(leave empty - not required for local)
```

**PostgREST Schema:**
```
public
```

## 📊 Service URLs

After migration, these services will be available:

| Service | URL | Purpose |
|---------|-----|---------|
| **n8n** | http://localhost:5678 | Workflow automation |
| **PostgREST API** | http://localhost:3000 | Database REST API |
| **PostgreSQL** | localhost:5432 | Direct database access |
| **pgAdmin** | http://localhost:8080 | Database management UI |

## 🔧 Configuration Files

### Docker Compose
- **[`docker-compose-local-postgresql.yml`](docker-compose-local-postgresql.yml)** - Complete local stack
- **[`.env.local`](.env.local)** - Local environment variables

### MCP Configuration
- **[`.vscode/mcp.json`](.vscode/mcp.json)** - Updated for local PostgREST

### Migration Scripts
- **[`migrate_to_local_postgresql.py`](migrate_to_local_postgresql.py)** - Complete local migration

## 🌐 Database Credentials

### PostgreSQL Connection
```
Host: localhost
Port: 5432
Database: n8n
Username: n8n_user
Password: n8n_password
```

### pgAdmin Access (Optional)
```
URL: http://localhost:8080
Email: admin@n8n.local
Password: admin123
```

To start pgAdmin:
```bash
docker-compose -f docker-compose-local-postgresql.yml --profile admin up -d
```

## 🔍 Testing the Setup

### 1. Verify Services
```bash
# Check all services are running
docker-compose -f docker-compose-local-postgresql.yml ps

# Test PostgREST API
curl http://localhost:3000/

# Test n8n health
curl http://localhost:5678/healthz
```

### 2. Test Database Connection
```bash
# Connect to PostgreSQL
docker-compose -f docker-compose-local-postgresql.yml exec postgres psql -U n8n_user -d n8n

# List tables
\dt

# Check workflow data
SELECT COUNT(*) FROM workflow_entity;
```

### 3. Test PostgREST API
```bash
# Get all workflows via REST API
curl http://localhost:3000/workflow_entity

# Get specific workflow
curl "http://localhost:3000/workflow_entity?id=eq.your-workflow-id"
```

## 🤖 Roo Code Integration

### MCP Server Configuration
The local PostgREST MCP server is configured to connect to:
- **URL**: `http://localhost:3000`
- **Schema**: `public`
- **Authentication**: None required (local setup)

### Example AI Interactions
Once configured, you can ask Roo Code:

```
"Show me all workflows in the database"
"Count the number of active workflows"
"List recent workflow executions"
"Create a new workflow entry"
"Update workflow status to inactive"
```

## 📋 Migration Process

### What the Migration Does
1. **Backup**: Creates backup of current SQLite setup
2. **Environment**: Sets up local PostgreSQL environment
3. **Services**: Starts PostgreSQL, PostgREST, and n8n containers
4. **Schema**: Creates database schema from exported SQL
5. **Data**: Imports all data from SQLite export
6. **Verification**: Tests all services and connections

### Data Migrated
- ✅ **5 workflows** (with complete configuration)
- ✅ **1 user account** (admin@n8n.local)
- ✅ **5 execution records** (with history)
- ✅ **Settings and configuration**
- ✅ **Tags and metadata**
- ✅ **Project and sharing data**

## 🛠️ Management Commands

### Service Management
```bash
# Start all services
docker-compose -f docker-compose-local-postgresql.yml up -d

# Stop all services
docker-compose -f docker-compose-local-postgresql.yml down

# View logs
docker-compose -f docker-compose-local-postgresql.yml logs -f

# Restart specific service
docker-compose -f docker-compose-local-postgresql.yml restart n8n
```

### Database Management
```bash
# Backup database
docker-compose -f docker-compose-local-postgresql.yml exec postgres pg_dump -U n8n_user n8n > backup.sql

# Restore database
docker-compose -f docker-compose-local-postgresql.yml exec -T postgres psql -U n8n_user n8n < backup.sql

# Access database shell
docker-compose -f docker-compose-local-postgresql.yml exec postgres psql -U n8n_user n8n
```

## 🔄 Rollback Plan

If you need to rollback to SQLite:

### Automatic Rollback
The migration script creates automatic backups and can rollback on failure.

### Manual Rollback
```bash
# Stop local PostgreSQL stack
docker-compose -f docker-compose-local-postgresql.yml down

# Restore original configuration
cp backups/pre-local-postgresql-migration-[timestamp]/docker-compose.yml docker-compose.yml
cp backups/pre-local-postgresql-migration-[timestamp]/database.sqlite docker/database.sqlite

# Start SQLite version
docker-compose up -d
```

## 🎯 Benefits of Local Setup

### Advantages
- ✅ **No Cloud Dependencies** - Everything runs locally
- ✅ **Full Control** - Complete control over data and services
- ✅ **No Costs** - No cloud service fees
- ✅ **Fast Performance** - Local network speeds
- ✅ **Privacy** - Data never leaves your machine
- ✅ **Development Friendly** - Easy to modify and experiment

### Enhanced Capabilities
- 🤖 **AI Database Operations** via PostgREST MCP
- 📊 **REST API Access** to all n8n data
- 🔍 **Advanced Queries** with PostgreSQL features
- 📈 **Better Performance** than SQLite for complex operations
- 🔄 **Real-time Updates** through PostgREST subscriptions

## 🆘 Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Change ports in docker-compose-local-postgresql.yml if needed
   - Default ports: 5432 (PostgreSQL), 3000 (PostgREST), 5678 (n8n)

2. **Services Not Starting**
   - Check Docker is running: `docker ps`
   - Check logs: `docker-compose -f docker-compose-local-postgresql.yml logs`
   - Restart services: `docker-compose -f docker-compose-local-postgresql.yml restart`

3. **Data Import Issues**
   - Check PostgreSQL is ready: `docker-compose -f docker-compose-local-postgresql.yml exec postgres pg_isready`
   - Manually import: Use pgAdmin or psql commands

4. **MCP Connection Issues**
   - Verify PostgREST is running: `curl http://localhost:3000/`
   - Check Roo Code MCP settings
   - Restart VSCode

### Debug Commands
```bash
# Check service status
docker-compose -f docker-compose-local-postgresql.yml ps

# View service logs
docker-compose -f docker-compose-local-postgresql.yml logs [service-name]

# Test PostgREST
curl -v http://localhost:3000/

# Test database connection
docker-compose -f docker-compose-local-postgresql.yml exec postgres pg_isready -U n8n_user
```

## ✅ Ready to Use

Your local PostgreSQL + PostgREST setup is complete and ready for:

1. **n8n workflow automation** with PostgreSQL backend
2. **AI-powered database operations** via Roo Code MCP
3. **REST API access** to all n8n data
4. **Advanced database features** and performance

**Next Step**: Run `python3 migrate_to_local_postgresql.py` to start the migration!