# n8n Workflow Sync Guide

## Overview

This guide provides the **best practices for keeping n8n workflows in sync** between your local files and n8n instance using **CLI-only approaches** that avoid GUI dependency.

## 🎯 Recommended Sync Solution

Based on comprehensive research and analysis, here are the optimal approaches ranked by effectiveness:

### 1. **n8n CLI with Custom Sync Script** (⭐ RECOMMENDED)

**File**: [`n8n-sync.sh`](n8n-sync.sh)

This is the **best solution** that combines n8n's native CLI with intelligent sync logic:

```bash
# Quick start
./n8n-sync.sh init                    # Initialize configuration
./n8n-sync.sh sync-bidirectional      # Intelligent two-way sync
./n8n-sync.sh watch                   # Auto-sync on file changes
```

**Advantages:**
- ✅ Uses native n8n CLI (no GUI required)
- ✅ Bidirectional sync with conflict detection
- ✅ Automatic backups before operations
- ✅ File watching for real-time sync
- ✅ Dry-run mode for safe testing
- ✅ Comprehensive error handling
- ✅ Version control friendly

### 2. **Third-Party Solutions**

**n8n2git** (https://n8n2git.com/)
- Git-powered version control
- Seamless GitHub integration
- Works with self-hosted instances
- Commercial solution with advanced features

**Community Workflows**
- [Bidirectional GitHub Workflow Sync](https://n8n.io/workflows/5081)
- [Workflow Repos8r](https://n8n.io/workflows/3014)

### 3. **Native n8n CLI** (Basic)

Direct use of n8n's built-in commands:

```bash
# Export all workflows
n8n export:workflow --backup --output=./exported/

# Import workflows
n8n import:workflow --separate --input=./exported/

# List workflows
n8n list:workflow
```

## 🚀 Quick Setup

### Prerequisites

1. **n8n CLI installed and accessible**:
   ```bash
   which n8n  # Should return path to n8n
   ```

2. **n8n instance running**:
   ```bash
   curl -s http://localhost:5678 > /dev/null && echo "n8n accessible" || echo "n8n not accessible"
   ```

3. **Optional tools for enhanced functionality**:
   ```bash
   # For file watching
   brew install fswatch  # macOS
   # apt-get install fswatch  # Linux
   
   # For JSON processing
   brew install jq  # macOS
   # apt-get install jq  # Linux
   ```

### Initial Setup

1. **Initialize the sync environment**:
   ```bash
   cd /path/to/your/n8n/project
   ./workflows/n8n-sync.sh init
   ```

2. **Test the connection**:
   ```bash
   ./workflows/n8n-sync.sh list-remote
   ```

3. **Compare current state**:
   ```bash
   ./workflows/n8n-sync.sh compare
   ```

## 📋 Common Workflows

### Daily Development Workflow

```bash
# 1. Start your day - sync from n8n to get latest changes
./workflows/n8n-sync.sh sync-from-n8n

# 2. Work on your workflows locally (edit JSON files)

# 3. Test changes by syncing to n8n
./workflows/n8n-sync.sh sync-to-n8n --dry-run  # Preview first
./workflows/n8n-sync.sh sync-to-n8n --backup   # Sync with backup

# 4. End of day - ensure everything is in sync
./workflows/n8n-sync.sh sync-bidirectional
```

### Continuous Development

```bash
# Start file watcher for automatic sync
./workflows/n8n-sync.sh watch
```

### Team Collaboration

```bash
# Before starting work
./workflows/n8n-sync.sh backup                 # Create backup
./workflows/n8n-sync.sh sync-from-n8n         # Get latest from n8n

# After making changes
./workflows/n8n-sync.sh sync-to-n8n --backup  # Push changes with backup
```

### Production Deployment

```bash
# Export production workflows
./workflows/n8n-sync.sh export-all

# Deploy to new environment
./workflows/n8n-sync.sh import-all --backup
```

## 🔧 Advanced Configuration

### Environment Variables

```bash
export N8N_URL="http://localhost:5678"        # n8n instance URL
export WORKFLOWS_DIR="/path/to/workflows"     # Workflow files directory
export EXPORT_DIR="./exported"                # Export destination
export BACKUP_DIR="./backups"                 # Backup location
```

### Configuration File

The sync tool creates `.n8n-sync-config` with customizable settings:

```bash
# n8n Sync Configuration
N8N_URL=http://localhost:5678
WORKFLOWS_DIR=/path/to/workflows
EXPORT_DIR=./exported
BACKUP_DIR=./backups
LAST_SYNC=2025-01-23T10:30:00Z
AUTO_BACKUP=true
EXCLUDE_PATTERNS=("*.log" "*.tmp" "*~")
INCLUDE_PATTERNS=("*.json")
```

## 📊 Comparison with Current Approach

| Feature | Current Scripts | n8n-sync.sh | Native CLI | Third-Party |
|---------|----------------|-------------|------------|-------------|
| **Bidirectional Sync** | ❌ | ✅ | ❌ | ✅ |
| **Conflict Detection** | ❌ | ✅ | ❌ | ✅ |
| **Auto Backup** | ❌ | ✅ | ❌ | ✅ |
| **File Watching** | ❌ | ✅ | ❌ | ✅ |
| **Dry Run Mode** | ❌ | ✅ | ❌ | ✅ |
| **Error Handling** | Basic | Advanced | Basic | Advanced |
| **Version Control** | Manual | Friendly | Manual | Integrated |
| **GUI Dependency** | Manual | None | None | None |
| **Setup Complexity** | Low | Medium | Low | High |
| **Cost** | Free | Free | Free | Paid |

## 🛠️ Migration from Current Setup

### Step 1: Backup Current State

```bash
# Backup existing workflows
cp -r workflows workflows-backup-$(date +%Y%m%d)

# Export current n8n state
./workflows/n8n-sync.sh backup
```

### Step 2: Initialize New Sync System

```bash
# Initialize sync configuration
./workflows/n8n-sync.sh init

# Compare current state
./workflows/n8n-sync.sh compare
```

### Step 3: Test Sync Operations

```bash
# Test export (dry run)
./workflows/n8n-sync.sh export-all --dry-run

# Test import (dry run)
./workflows/n8n-sync.sh import-all --dry-run

# Test bidirectional sync (dry run)
./workflows/n8n-sync.sh sync-bidirectional --dry-run
```

### Step 4: Replace Old Scripts

```bash
# Rename old scripts for reference
mv workflows/import-workflow.sh workflows/import-workflow.sh.old
mv workflows/import-all-workflows.sh workflows/import-all-workflows.sh.old

# Create convenience aliases
ln -s n8n-sync.sh workflows/sync
```

## 🔍 Troubleshooting

### Common Issues

1. **n8n not accessible**:
   ```bash
   # Check if n8n is running
   curl -s http://localhost:5678
   
   # Check n8n process
   ps aux | grep n8n
   ```

2. **Permission errors**:
   ```bash
   # Fix script permissions
   chmod +x workflows/n8n-sync.sh
   
   # Fix n8n config permissions
   chmod 600 ~/.n8n/config
   ```

3. **Import failures**:
   ```bash
   # Check workflow JSON validity
   jq . workflows/your-workflow.json
   
   # Import individual workflow for debugging
   n8n import:workflow --input=workflows/your-workflow.json
   ```

4. **File watching not working**:
   ```bash
   # Install fswatch
   brew install fswatch  # macOS
   
   # Test file watching
   fswatch -o workflows/ | head -5
   ```

### Debug Mode

```bash
# Enable verbose output
./workflows/n8n-sync.sh sync-bidirectional --verbose

# Check configuration
cat workflows/.n8n-sync-config

# Manual CLI testing
n8n list:workflow
n8n export:workflow --help
```

## 📈 Best Practices

### 1. **Version Control Integration**

```bash
# Add to .gitignore
echo "workflows/exported/" >> .gitignore
echo "workflows/backups/" >> .gitignore
echo "workflows/.n8n-sync-config" >> .gitignore

# Track only source workflow files
git add workflows/*.json
git add workflows/n8n-sync.sh
```

### 2. **Automated Workflows**

Create a Git hook for automatic sync:

```bash
# .git/hooks/pre-commit
#!/bin/bash
cd workflows
./n8n-sync.sh sync-from-n8n --force
git add *.json
```

### 3. **CI/CD Integration**

```yaml
# .github/workflows/n8n-sync.yml
name: n8n Workflow Sync
on: [push, pull_request]
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate workflows
        run: |
          for file in workflows/*.json; do
            jq . "$file" > /dev/null || exit 1
          done
```

### 4. **Monitoring and Alerts**

```bash
# Add to crontab for regular sync
0 */6 * * * cd /path/to/project && ./workflows/n8n-sync.sh sync-bidirectional --force

# Log sync operations
./workflows/n8n-sync.sh sync-bidirectional 2>&1 | tee -a sync.log
```

## 🎯 Conclusion

The **n8n-sync.sh** script provides the optimal solution for keeping n8n workflows in sync without GUI dependency. It combines:

- **Native n8n CLI** for reliable operations
- **Intelligent sync logic** for conflict resolution
- **Automation capabilities** for continuous development
- **Safety features** like backups and dry-run mode
- **Developer-friendly** workflow integration

This approach significantly improves upon the current manual import scripts and provides a production-ready solution for workflow management.

## 📚 Additional Resources

- [n8n CLI Documentation](https://docs.n8n.io/hosting/cli-commands/)
- [n8n Workflow Export/Import](https://docs.n8n.io/workflows/export-import/)
- [n8n2git - Commercial Solution](https://n8n2git.com/)
- [Community Sync Workflows](https://n8n.io/workflows/?search=sync)

---

**Next Steps**: Start with `./workflows/n8n-sync.sh init` and follow the Quick Setup guide above.