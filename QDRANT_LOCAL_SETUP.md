# Qdrant Local Docker Setup for Shopware n8n Workflow

This guide explains how to set up and use Qdrant vector database locally with Docker for your Shopware product import workflow in n8n.

## 📋 Overview

This setup provides:
- **Local Qdrant Vector Database** running in Docker
- **n8n Workflow Automation** with Qdrant integration
- **Shopware Product Import** with vector storage
- **Complete local development environment**

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Shopware API  │───▶│   n8n Workflow  │───▶│  Local Qdrant   │
│                 │    │                 │    │  Vector DB      │
│ Product Data    │    │ Transform &     │    │ Vector Storage  │
│ OAuth Token     │    │ Vectorize       │    │ Port: 6333      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Start the Services

```bash
# Start both n8n and Qdrant
docker-compose -f docker-compose-n8n-qdrant.yml up -d

# Check services are running
docker-compose -f docker-compose-n8n-qdrant.yml ps
```

### 2. Initialize Qdrant Collection

```bash
# Run the setup script to create the collection
./setup-qdrant-collection.sh
```

### 3. Access n8n and Import the Workflow

1. Open n8n at http://localhost:5678
2. **Login with existing credentials:**
   - **Email**: `admin@n8n.local`
   - **Password**: You'll need to reset the password or check your existing setup
3. Import the workflow: `docker/workflows/shopware-to-qdrant-local.json`
4. Execute the workflow to start importing Shopware products

## 📁 File Structure

```
├── docker-compose-n8n-qdrant.yml          # Combined Docker setup
├── setup-qdrant-collection.sh             # Qdrant initialization script
├── docker/workflows/
│   ├── shopware-to-qdrant-local.json      # Local Qdrant workflow
│   └── shopware-to-qdrant-complete.json   # Original cloud workflow
└── QDRANT_LOCAL_SETUP.md                  # This documentation
```

## 🔧 Configuration Details

### Docker Compose Configuration

The [`docker-compose-n8n-qdrant.yml`](docker-compose-n8n-qdrant.yml) includes:

- **Qdrant Service**:
  - Image: `qdrant/qdrant:latest`
  - Ports: `6333` (HTTP), `6334` (gRPC)
  - Persistent storage: `qdrant_storage` volume
  - Health checks enabled

- **n8n Service**:
  - Image: `n8nio/n8n:latest`
  - Port: `5678`
  - Environment variables for Qdrant connection
  - Depends on Qdrant service

### Qdrant Collection Settings

- **Collection Name**: `shopware_products`
- **Vector Size**: `1536` (OpenAI embedding compatible)
- **Distance Metric**: `Cosine`
- **Replication Factor**: `1` (single instance)

## 🔄 Workflow Changes

The local workflow ([`shopware-to-qdrant-local.json`](docker/workflows/shopware-to-qdrant-local.json)) differs from the cloud version:

### Key Changes:
1. **Qdrant URL**: `http://localhost:6333` instead of cloud URL
2. **No API Key**: Local instance doesn't require authentication
3. **Collection Name**: Uses `shopware_products` collection
4. **Enhanced Logging**: Includes local Qdrant connection info

### Workflow Steps:
1. **OAuth Authentication** with Shopware API
2. **Product Fetching** with pagination
3. **Data Transformation** for vector storage
4. **Vector Generation** (placeholder vectors for now)
5. **Qdrant Storage** via HTTP API
6. **Completion Logging** with statistics

## 🛠️ Management Commands

### Service Management

```bash
# Start services
docker-compose -f docker-compose-n8n-qdrant.yml up -d

# Stop services
docker-compose -f docker-compose-n8n-qdrant.yml down

# View logs
docker-compose -f docker-compose-n8n-qdrant.yml logs -f

# Restart specific service
docker-compose -f docker-compose-n8n-qdrant.yml restart qdrant
```

### Qdrant Management

```bash
# Check Qdrant health
curl http://localhost:6333/health

# List collections
curl http://localhost:6333/collections

# Get collection info
curl http://localhost:6333/collections/shopware_products

# Count points in collection
curl http://localhost:6333/collections/shopware_products/points/count

# Search vectors (example)
curl -X POST http://localhost:6333/collections/shopware_products/points/search \
  -H "Content-Type: application/json" \
  -d '{
    "vector": [0.1, 0.2, 0.3, ...],
    "limit": 5
  }'
```

### Data Management

```bash
# Delete all points in collection
curl -X POST http://localhost:6333/collections/shopware_products/points/delete \
  -H "Content-Type: application/json" \
  -d '{"filter": {"must": [{"key": "active", "match": {"any": [true, false]}}]}}'

# Recreate collection
curl -X DELETE http://localhost:6333/collections/shopware_products
./setup-qdrant-collection.sh
```

## 🔍 Monitoring & Debugging

### Health Checks

```bash
# Check all services
docker-compose -f docker-compose-n8n-qdrant.yml ps

# Qdrant health
curl http://localhost:6333/health

# n8n health
curl http://localhost:5678/healthz
```

### Logs

```bash
# All services
docker-compose -f docker-compose-n8n-qdrant.yml logs -f

# Qdrant only
docker-compose -f docker-compose-n8n-qdrant.yml logs -f qdrant

# n8n only
docker-compose -f docker-compose-n8n-qdrant.yml logs -f n8n
```

### Qdrant Web UI

Qdrant provides a web interface at: http://localhost:6333/dashboard

## 🚨 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using the ports
   lsof -i :6333
   lsof -i :5678
   
   # Change ports in docker-compose-n8n-qdrant.yml if needed
   ```

2. **Collection Not Found**
   ```bash
   # Recreate the collection
   ./setup-qdrant-collection.sh
   ```

3. **Connection Refused**
   ```bash
   # Check if Qdrant is running
   docker-compose -f docker-compose-n8n-qdrant.yml ps qdrant
   
   # Check Qdrant logs
   docker-compose -f docker-compose-n8n-qdrant.yml logs qdrant
   ```

4. **Workflow Execution Errors**
   - Check n8n logs for detailed error messages
   - Verify Qdrant collection exists
   - Ensure Shopware API credentials are correct

### Performance Tuning

For better performance with large datasets:

1. **Increase Qdrant Memory**:
   ```yaml
   # In docker-compose-n8n-qdrant.yml
   qdrant:
     deploy:
       resources:
         limits:
           memory: 2G
   ```

2. **Optimize Collection Settings**:
   ```bash
   # Recreate with optimized settings
   curl -X PUT "http://localhost:6333/collections/shopware_products" \
     -H "Content-Type: application/json" \
     -d '{
       "vectors": {
         "size": 1536,
         "distance": "Cosine"
       },
       "optimizers_config": {
         "default_segment_number": 4,
         "max_segment_size": 20000
       }
     }'
   ```

## 🔄 Migration from Cloud Qdrant

If you're migrating from the cloud version:

1. **Export Data** (if needed):
   ```bash
   # Export points from cloud Qdrant
   # (Implementation depends on your cloud setup)
   ```

2. **Update Workflow**:
   - Import the new local workflow
   - Deactivate the cloud workflow
   - Test the local workflow

3. **Verify Data**:
   ```bash
   # Check point count
   curl http://localhost:6333/collections/shopware_products/points/count
   ```

## 📊 Monitoring & Analytics

### Collection Statistics

```bash
# Get collection info
curl http://localhost:6333/collections/shopware_products | jq '.'

# Point count
curl http://localhost:6333/collections/shopware_products/points/count | jq '.'

# Collection metrics
curl http://localhost:6333/metrics
```

### n8n Workflow Monitoring

- Access n8n at http://localhost:5678
- Check execution history
- Monitor workflow performance
- Review error logs

## 🔐 Security Considerations

### Local Development

- No authentication required for local Qdrant
- Services only accessible on localhost
- Use environment variables for sensitive data

### Production Deployment

For production use, consider:
- Enable Qdrant authentication
- Use HTTPS/TLS
- Implement proper firewall rules
- Regular backups

## 📚 Additional Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [n8n Documentation](https://docs.n8n.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Shopware API Documentation](https://shopware.stoplight.io/docs/store-api)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review service logs
3. Verify all prerequisites are met
4. Check Docker and Docker Compose versions

---

**Last Updated**: 2025-01-26  
**Version**: 1.0  
**Compatibility**: n8n latest, Qdrant latest, Docker Compose v3.8+