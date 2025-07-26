#!/bin/bash

# Backup and restart n8n with proper volume configuration
echo "🔄 Backing up current n8n data and restarting with proper volumes..."

# Stop the current n8n container
echo "⏹️  Stopping n8n container..."
docker-compose down

# Create backup of current data
BACKUP_DIR="./backups/volume-migration-$(date +%Y%m%d-%H%M%S)"
echo "💾 Creating backup at $BACKUP_DIR..."
mkdir -p "$BACKUP_DIR"
cp -r ./docker/* "$BACKUP_DIR/" 2>/dev/null || true

# Ensure docker directory exists and has proper permissions
echo "📁 Ensuring docker directory structure..."
mkdir -p ./docker/binaryData
mkdir -p ./docker/workflows
chmod -R 755 ./docker

# Start n8n with new volume configuration
echo "🚀 Starting n8n with improved volume configuration..."
docker-compose up -d

# Wait for n8n to be ready
echo "⏳ Waiting for n8n to be ready..."
sleep 10

# Check if n8n is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ n8n is running successfully!"
    echo "🌐 Access n8n at: http://localhost:5678"
    echo "📊 Check status with: docker-compose ps"
    echo "📋 View logs with: docker-compose logs -f"
else
    echo "❌ n8n failed to start. Check logs with: docker-compose logs"
    exit 1
fi

echo "✨ Migration complete! Your data is now stored in proper Docker volumes."