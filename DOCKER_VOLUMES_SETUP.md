# n8n Docker Volume Configuration

## Overview
Successfully configured n8n with proper Docker volumes for persistent data storage that survives container restarts and recreation.

## Volume Configuration

### Named Volumes
- **`n8n_data`**: Main n8n data directory (`/home/node/.n8n`)
- **`n8n_files`**: Binary data storage (`/home/node/.n8n/binaryData`)

### Volume Mapping
```yaml
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
```

## Improvements Made

### 1. **Proper Volume Management**
- Named volumes instead of simple bind mounts
- Better isolation and management
- Explicit volume definitions

### 2. **Enhanced Configuration**
- Added health check endpoint (`/healthz`)
- Explicit SQLite database configuration
- Read-only workflows directory mount
- Improved environment variables

### 3. **Data Persistence**
- Database: `./docker/database.sqlite`
- Binary files: `./docker/binaryData/`
- Configuration: `./docker/config`
- Workflows: `./workflows/` (read-only)

### 4. **Health Monitoring**
- Health check every 30 seconds
- 40-second startup grace period
- Automatic restart on failure

## Container Status
✅ **Running and Healthy**
- Container: `n8n-production`
- Status: `Up (healthy)`
- Port: `5678:5678`
- Health endpoint: http://localhost:5678/healthz

## Volume Status
✅ **Volumes Created**
- `n8n_n8n_data` - Main data volume
- `n8n_n8n_files` - Binary files volume

## Data Backup
- Backup created at: `./backups/volume-migration-[timestamp]/`
- All existing data preserved and accessible

## Commands
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f

# Restart container
docker-compose restart

# Stop/start
docker-compose down
docker-compose up -d

# Check volumes
docker volume ls | grep n8n
```

## Benefits
1. **Data Persistence**: Data survives container recreation
2. **Better Management**: Named volumes are easier to manage
3. **Health Monitoring**: Automatic health checks
4. **Backup Safety**: Existing data preserved
5. **Performance**: Optimized volume configuration