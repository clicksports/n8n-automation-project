#!/bin/bash
# PostgreSQL Import Script
# Run this script to import data into PostgreSQL

set -e

echo "🚀 Starting PostgreSQL data import..."

# Database connection parameters
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-n8n}"
DB_USER="${DB_USER:-postgres}"

echo "📊 Importing to: $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"

# Create schema
echo "📋 Creating database schema..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f schema/complete_schema.sql

# Import data
echo "📥 Importing data..."

echo "   Importing execution_data..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\COPY execution_data FROM '/Users/christian.gick/Documents/VisualStudio/n8n/migration_export/data/execution_data.csv' WITH CSV HEADER;"

echo "   Importing execution_entity..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\COPY execution_entity FROM '/Users/christian.gick/Documents/VisualStudio/n8n/migration_export/data/execution_entity.csv' WITH CSV HEADER;"

echo "   Importing invalid_auth_token..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\COPY invalid_auth_token FROM '/Users/christian.gick/Documents/VisualStudio/n8n/migration_export/data/invalid_auth_token.csv' WITH CSV HEADER;"

echo "   Importing workflow_statistics..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\COPY workflow_statistics FROM '/Users/christian.gick/Documents/VisualStudio/n8n/migration_export/data/workflow_statistics.csv' WITH CSV HEADER;"

echo "   Importing tag_entity..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\COPY tag_entity FROM '/Users/christian.gick/Documents/VisualStudio/n8n/migration_export/data/tag_entity.csv' WITH CSV HEADER;"

echo "   Importing project..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\COPY project FROM '/Users/christian.gick/Documents/VisualStudio/n8n/migration_export/data/project.csv' WITH CSV HEADER;"

echo "   Importing workflows_tags..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\COPY workflows_tags FROM '/Users/christian.gick/Documents/VisualStudio/n8n/migration_export/data/workflows_tags.csv' WITH CSV HEADER;"

echo "   Importing migrations..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\COPY migrations FROM '/Users/christian.gick/Documents/VisualStudio/n8n/migration_export/data/migrations.csv' WITH CSV HEADER;"

echo "   Importing workflow_entity..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\COPY workflow_entity FROM '/Users/christian.gick/Documents/VisualStudio/n8n/migration_export/data/workflow_entity.csv' WITH CSV HEADER;"

echo "   Importing shared_workflow..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\COPY shared_workflow FROM '/Users/christian.gick/Documents/VisualStudio/n8n/migration_export/data/shared_workflow.csv' WITH CSV HEADER;"

echo "   Importing user..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\COPY user FROM '/Users/christian.gick/Documents/VisualStudio/n8n/migration_export/data/user.csv' WITH CSV HEADER;"

echo "   Importing project_relation..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\COPY project_relation FROM '/Users/christian.gick/Documents/VisualStudio/n8n/migration_export/data/project_relation.csv' WITH CSV HEADER;"

echo "   Importing settings..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\COPY settings FROM '/Users/christian.gick/Documents/VisualStudio/n8n/migration_export/data/settings.csv' WITH CSV HEADER;"

echo "✅ PostgreSQL import completed successfully!"
