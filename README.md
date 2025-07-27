# n8n with PostgreSQL and Qdrant Setup

This project contains a clean n8n setup with PostgreSQL database and Qdrant vector database integration.

## Architecture

- **n8n**: Workflow automation platform
- **PostgreSQL**: Primary database (migrated from SQLite)
- **Qdrant**: Vector database for product embeddings
- **PostgREST**: REST API for PostgreSQL (MCP integration)

## Services

All services run via Docker Compose:

```bash
# Start all services
docker-compose -f docker-compose-local-postgresql.yml up -d

# Check service status
docker ps
```

## Workflow Management

The project contains one main workflow:
- `workflows/current_workflow.json` - Shopware to Local Qdrant Production (With Collection Auto-Create)

### Sync Workflow Without Interface

Use the CLI sync tools to manage workflows without the n8n interface:

```bash
cd workflows

# List remote workflows
./n8n-sync.sh list-remote

# Sync local workflow to n8n
./n8n-sync.sh sync-to-n8n --backup

# Verify sync status
./verify-sync.sh
```

## Database Access

### PostgreSQL
- Host: localhost:5432
- Database: n8n
- User: n8n_user
- Password: n8n_password

### PostgREST API
- URL: http://localhost:3000
- Schema: public

### Qdrant
- URL: http://localhost:6333
- Collection: shopware_products

## Environment Configuration

Key environment variables are in `.env`:
- Database credentials
- PostgREST configuration
- API keys and tokens

## MCP Integration

The project supports Model Context Protocol (MCP) for database interaction:
- PostgREST MCP server for PostgreSQL access
- Configuration in `.roo/mcp.json`

## Workflow Features

The main workflow:
1. Authenticates with Shopware API
2. Fetches product data with pagination
3. Transforms data for vector storage
4. Auto-creates Qdrant collection if needed
5. Stores product vectors with metadata

## Maintenance

- Backups are automatically created during sync operations
- Use `./n8n-sync.sh --help` for all available commands
- Monitor services with `docker ps` and `docker logs <container>`