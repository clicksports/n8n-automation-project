#!/bin/bash

# Script to clean up old workflow versions in n8n
# Keep only one copy of "Shopware to Local Qdrant Production v1.0"

echo "🧹 Cleaning up old workflow versions in n8n..."

# List of workflow IDs to keep (we'll keep the first v1.0 version)
KEEP_WORKFLOW="GCFjIS1WoZAoWI1g"

# Get all workflows and extract IDs to delete
echo "📋 Getting list of workflows to delete..."

# Workflows to delete (all except the one we want to keep)
WORKFLOWS_TO_DELETE=(
    "zWbjNKpe1o6yWRSj"  # Shopware to Qdrant Product Import (Optimized)
    "ZbPkfDqQvO9e1D8k"  # Shopware Optimized Vectorization Workflow (Fixed)
    "R47Hzb2wpB0o5iUd"  # Shopware to Qdrant Product Import (Complete)
    "WEqUpSo3gpHu3cW6"  # HELD Product Vectorization (Optimized)
    "zCtyud7ywnumT7Py"  # Shopware to Qdrant Product Import (Enhanced)
    "fYt7IJen0aIvYo7t"  # Shopware to Qdrant Product Import (Enhanced)
    "RMr6XjGDVKvd4C4Y"  # Shopware Optimized Vectorization Workflow
    "i0hWxoLzDdOBGZL7"  # Shopware to Qdrant Product Import (Fixed)
    "bbiXOzcbIjjiiF3M"  # Shopware to Local Qdrant Production
    "YTtYsaYUGnufCSKI"  # Shopware to Local Qdrant Production
    "GLlhdjGFiak0nHY8"  # Shopware Optimized Vectorization Workflow (Fixed)
    "4DC7Vbg7ZswPlzaG"  # Shopware to Qdrant Product Import (Complete)
    "KW5S4aqJKl85UFnb"  # HELD Product Vectorization (Optimized)
    "tyZ8nv7yKOn6VE0b"  # Shopware to Qdrant Product Import (Complete)
    "Pnjfg3uAQcip6J6j"  # Shopware to Qdrant Product Import (Enhanced)
    "qBLfesuNCaAiyfn9"  # Shopware Optimized Vectorization Workflow
    "4sLblPhpPpYLyISa"  # Shopware to Qdrant Product Import (Fixed)
    "Ojd69ZQ3GsWLtbhF"  # Shopware to Local Qdrant Production
    "o0wn8zRfXvzQjpjH"  # Shopware to Local Qdrant Production
    "ExGbX40pB06BMVj1"  # Shopware Optimized Vectorization Workflow (Fixed)
    "5oCYMSg4ZfhEvkXw"  # Shopware to Qdrant Product Import (Complete)
    "ucas7bhBj67Vwmfg"  # HELD Product Vectorization (Optimized)
    "6RpHxIY2cKHX3Th5"  # Shopware to Qdrant Product Import (Complete)
    "3s5uxbtrTHMPF47x"  # Shopware to Qdrant Product Import (Enhanced)
    "ZP921HbcRlHimo6B"  # Shopware Optimized Vectorization Workflow
    "1mQ3sWCaCNEtDQ4D"  # Shopware to Qdrant Product Import (Fixed)
    "t7MD6SapUPT8UB9A"  # Shopware to Local Qdrant Production
    "ieMs9Cm0jxpAJzgM"  # Shopware to Local Qdrant Production (With Collection Auto-Create)
    "JjAts05lG6rY5GkF"  # Shopware to Local Qdrant Production (With Collection Auto-Create)
    "z2jTUspt7fozCAsP"  # Shopware to Qdrant Product Import (Best Version)
    "9a1d1efa-83b1-49da-b9f3-273dfe985133"  # Shopware to Local Qdrant Production (With Collection Auto-Create)
    "sO3iwoQsSArFAxOl"  # Shopware to Local Qdrant Production (With Collection Auto-Create)
    "54nCDTE86I89E2cr"  # Shopware to Local Qdrant Production (With Collection Auto-Create)
    "OH6zRxDEOgKG6dTs"  # Shopware to Local Qdrant Production (With Collection Auto-Create) - UPDATED
    "yy10q0PjaIQYAOvz"  # Shopware to Local Qdrant Production v1.0 (duplicate)
    "Hr151Ffr1qfqD3tV"  # Shopware to Local Qdrant Production v1.0 (duplicate)
)

echo "🗑️  Deleting ${#WORKFLOWS_TO_DELETE[@]} old workflow versions..."

# Delete workflows using docker exec (since API deletion had auth issues)
for workflow_id in "${WORKFLOWS_TO_DELETE[@]}"; do
    echo "Deleting workflow: $workflow_id"
    docker exec n8n-production n8n delete:workflow --id="$workflow_id" 2>/dev/null || echo "  ⚠️  Could not delete $workflow_id (may not exist)"
done

echo ""
echo "✅ Cleanup completed!"
echo "📋 Remaining workflows:"
./n8n-sync.sh list-remote