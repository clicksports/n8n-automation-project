#!/bin/bash

# n8n Workflow Sync Tool
# Bidirectional sync between n8n instance and local workflow files
# Avoids GUI usage and provides comprehensive CLI-based workflow management

set -euo pipefail

# Configuration
N8N_URL="${N8N_URL:-http://localhost:5678}"
WORKFLOWS_DIR="${WORKFLOWS_DIR:-$(pwd)}"
EXPORT_DIR="${EXPORT_DIR:-${WORKFLOWS_DIR}/exported}"
BACKUP_DIR="${BACKUP_DIR:-${WORKFLOWS_DIR}/backups}"
CONFIG_FILE="${CONFIG_FILE:-${WORKFLOWS_DIR}/.n8n-sync-config}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Help function
show_help() {
    cat << EOF
n8n Workflow Sync Tool - Bidirectional CLI-based workflow management

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    export-all          Export all workflows from n8n to files
    import-all          Import all workflow files to n8n
    sync-to-n8n         Sync local files to n8n (one-way)
    sync-from-n8n       Sync from n8n to local files (one-way)
    sync-bidirectional  Intelligent bidirectional sync
    list-local          List local workflow files
    list-remote         List workflows in n8n
    compare             Compare local files with n8n workflows
    backup              Create backup of current n8n workflows
    restore             Restore workflows from backup
    watch               Watch for file changes and auto-sync
    init                Initialize sync configuration

OPTIONS:
    --dry-run           Show what would be done without executing
    --force             Force operations without confirmation
    --backup            Create backup before operations
    --exclude PATTERN   Exclude files matching pattern
    --include PATTERN   Only include files matching pattern
    --verbose           Verbose output
    --help              Show this help

EXAMPLES:
    $0 export-all                    # Export all workflows to files
    $0 import-all --backup           # Import all files with backup
    $0 sync-bidirectional --dry-run  # Preview bidirectional sync
    $0 watch                         # Auto-sync on file changes
    $0 compare                       # Compare local vs remote

ENVIRONMENT VARIABLES:
    N8N_URL             n8n instance URL (default: http://localhost:5678)
    WORKFLOWS_DIR       Directory for workflow files (default: current dir)
    EXPORT_DIR          Directory for exported files (default: ./exported)
    BACKUP_DIR          Directory for backups (default: ./backups)

EOF
}

# Initialize configuration
init_config() {
    log_info "Initializing n8n sync configuration..."
    
    mkdir -p "$EXPORT_DIR" "$BACKUP_DIR"
    
    cat > "$CONFIG_FILE" << EOF
# n8n Sync Configuration
N8N_URL=$N8N_URL
WORKFLOWS_DIR=$WORKFLOWS_DIR
EXPORT_DIR=$EXPORT_DIR
BACKUP_DIR=$BACKUP_DIR
LAST_SYNC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
AUTO_BACKUP=true
EXCLUDE_PATTERNS=("*.log" "*.tmp" "*~")
INCLUDE_PATTERNS=("*.json")
EOF
    
    log_success "Configuration initialized at $CONFIG_FILE"
}

# Load configuration
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        source "$CONFIG_FILE"
    fi
}

# Check if n8n is accessible
check_n8n_connection() {
    if ! curl -s "$N8N_URL" > /dev/null 2>&1; then
        log_error "n8n is not accessible at $N8N_URL"
        log_info "Please ensure n8n is running or set correct N8N_URL"
        exit 1
    fi
    log_success "n8n connection verified"
}

# Create backup with timestamp
create_backup() {
    local backup_name="backup-$(date +%Y%m%d-%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    log_info "Creating backup: $backup_name"
    mkdir -p "$backup_path"
    
    if n8n export:workflow --backup --output="$backup_path/" > /dev/null 2>&1; then
        log_success "Backup created at $backup_path"
        echo "$backup_path"
    else
        log_error "Failed to create backup"
        exit 1
    fi
}

# Export all workflows from n8n
export_all_workflows() {
    local dry_run=${1:-false}
    local force=${2:-false}
    
    log_info "Exporting all workflows from n8n..."
    
    if [[ "$dry_run" == "true" ]]; then
        log_info "[DRY RUN] Would export workflows to: $EXPORT_DIR"
        n8n list:workflow
        return 0
    fi
    
    # Create export directory
    mkdir -p "$EXPORT_DIR"
    
    # Backup existing exports if they exist
    if [[ -d "$EXPORT_DIR" ]] && [[ "$(ls -A "$EXPORT_DIR" 2>/dev/null)" ]]; then
        if [[ "$force" != "true" ]]; then
            read -p "Export directory contains files. Overwrite? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Export cancelled"
                return 1
            fi
        fi
        
        # Move existing exports to backup
        local backup_name="export-backup-$(date +%Y%m%d-%H%M%S)"
        mv "$EXPORT_DIR" "$BACKUP_DIR/$backup_name"
        log_info "Existing exports backed up to $BACKUP_DIR/$backup_name"
        mkdir -p "$EXPORT_DIR"
    fi
    
    # Export workflows
    if n8n export:workflow --backup --output="$EXPORT_DIR/" > /dev/null 2>&1; then
        local count=$(ls -1 "$EXPORT_DIR"/*.json 2>/dev/null | wc -l)
        log_success "Exported $count workflows to $EXPORT_DIR"
        
        # Update last sync time
        sed -i.bak "s/LAST_SYNC=.*/LAST_SYNC=$(date -u +"%Y-%m-%dT%H:%M:%SZ")/" "$CONFIG_FILE" 2>/dev/null || true
    else
        log_error "Failed to export workflows"
        exit 1
    fi
}

# Import all workflow files to n8n
import_all_workflows() {
    local dry_run=${1:-false}
    local backup=${2:-false}
    local force=${3:-false}
    
    log_info "Importing workflow files to n8n..."
    
    # Find workflow JSON files
    local workflow_files=()
    while IFS= read -r -d '' file; do
        workflow_files+=("$file")
    done < <(find "$WORKFLOWS_DIR" -name "*.json" -not -path "*/exported/*" -not -path "*/backups/*" -print0)
    
    if [[ ${#workflow_files[@]} -eq 0 ]]; then
        log_warning "No workflow files found in $WORKFLOWS_DIR"
        return 1
    fi
    
    log_info "Found ${#workflow_files[@]} workflow files"
    
    if [[ "$dry_run" == "true" ]]; then
        log_info "[DRY RUN] Would import the following files:"
        printf '%s\n' "${workflow_files[@]}"
        return 0
    fi
    
    # Create backup if requested
    if [[ "$backup" == "true" ]]; then
        create_backup
    fi
    
    # Import each workflow file
    local success_count=0
    local error_count=0
    
    for file in "${workflow_files[@]}"; do
        local filename=$(basename "$file")
        log_info "Importing $filename..."
        
        if n8n import:workflow --input="$file" > /dev/null 2>&1; then
            log_success "✓ $filename"
            ((success_count++))
            
            # Activate the imported workflow
            local workflow_name=$(jq -r '.name // "unknown"' "$file" 2>/dev/null || echo "unknown")
            if [[ "$workflow_name" != "unknown" ]]; then
                # Get workflow ID by name and activate it
                local workflow_id=$(n8n list:workflow 2>/dev/null | grep "$workflow_name" | cut -d'|' -f1 | head -1)
                if [[ -n "$workflow_id" ]]; then
                    curl -s -X PATCH "http://localhost:5678/rest/workflows/$workflow_id" \
                        -H "Content-Type: application/json" \
                        -d '{"active": true}' > /dev/null 2>&1
                    log_info "  ⚡ Activated workflow"
                fi
            fi
        else
            log_error "✗ $filename"
            ((error_count++))
        fi
    done
    
    log_info "Import completed: $success_count successful, $error_count failed"
    
    if [[ $error_count -gt 0 ]]; then
        log_warning "Some imports failed. Check individual workflow files for issues."
    fi
}

# List local workflow files
list_local_workflows() {
    log_info "Local workflow files:"
    
    find "$WORKFLOWS_DIR" -name "*.json" -not -path "*/exported/*" -not -path "*/backups/*" | while read -r file; do
        local filename=$(basename "$file")
        local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "unknown")
        local modified=$(stat -f%Sm -t "%Y-%m-%d %H:%M" "$file" 2>/dev/null || stat -c%y "$file" 2>/dev/null | cut -d' ' -f1-2 || echo "unknown")
        
        # Try to extract workflow name from JSON
        local workflow_name="unknown"
        if command -v jq >/dev/null 2>&1; then
            workflow_name=$(jq -r '.name // "unknown"' "$file" 2>/dev/null || echo "unknown")
        fi
        
        printf "  %-30s %-40s %8s %s\n" "$filename" "$workflow_name" "$size" "$modified"
    done
}

# List remote workflows in n8n
list_remote_workflows() {
    log_info "Remote workflows in n8n:"
    n8n list:workflow
}

# Compare local and remote workflows
compare_workflows() {
    log_info "Comparing local files with n8n workflows..."
    
    # Export current n8n workflows to temp directory
    local temp_dir=$(mktemp -d)
    trap "rm -rf $temp_dir" EXIT
    
    if ! n8n export:workflow --backup --output="$temp_dir/" > /dev/null 2>&1; then
        log_error "Failed to export workflows for comparison"
        exit 1
    fi
    
    # Compare files
    local local_files=()
    local remote_files=()
    
    # Get local files
    while IFS= read -r -d '' file; do
        local_files+=("$(basename "$file")")
    done < <(find "$WORKFLOWS_DIR" -name "*.json" -not -path "*/exported/*" -not -path "*/backups/*" -print0)
    
    # Get remote files
    while IFS= read -r -d '' file; do
        remote_files+=("$(basename "$file")")
    done < <(find "$temp_dir" -name "*.json" -print0)
    
    # Find differences
    log_info "Comparison results:"
    
    # Files only in local
    for file in "${local_files[@]}"; do
        if [[ ! " ${remote_files[@]} " =~ " ${file} " ]]; then
            log_warning "Local only: $file"
        fi
    done
    
    # Files only in remote
    for file in "${remote_files[@]}"; do
        if [[ ! " ${local_files[@]} " =~ " ${file} " ]]; then
            log_warning "Remote only: $file"
        fi
    done
    
    # Files in both - check for differences
    for file in "${local_files[@]}"; do
        if [[ " ${remote_files[@]} " =~ " ${file} " ]]; then
            local local_file="$WORKFLOWS_DIR/$file"
            local remote_file="$temp_dir/$file"
            
            # Find the actual local file (might be in subdirectory)
            local actual_local_file=$(find "$WORKFLOWS_DIR" -name "$file" -not -path "*/exported/*" -not -path "*/backups/*" | head -1)
            
            if [[ -n "$actual_local_file" ]] && ! cmp -s "$actual_local_file" "$remote_file"; then
                log_info "Different: $file"
                
                if command -v jq >/dev/null 2>&1; then
                    local local_updated=$(jq -r '.updatedAt // "unknown"' "$actual_local_file" 2>/dev/null || echo "unknown")
                    local remote_updated=$(jq -r '.updatedAt // "unknown"' "$remote_file" 2>/dev/null || echo "unknown")
                    echo "  Local updated:  $local_updated"
                    echo "  Remote updated: $remote_updated"
                fi
            else
                log_success "Identical: $file"
            fi
        fi
    done
}

# Watch for file changes and auto-sync
watch_files() {
    log_info "Starting file watcher for auto-sync..."
    log_info "Watching directory: $WORKFLOWS_DIR"
    log_info "Press Ctrl+C to stop"
    
    if ! command -v fswatch >/dev/null 2>&1; then
        log_error "fswatch not found. Please install it for file watching functionality."
        log_info "macOS: brew install fswatch"
        log_info "Linux: apt-get install fswatch or yum install fswatch"
        exit 1
    fi
    
    fswatch -o "$WORKFLOWS_DIR" --exclude="$EXPORT_DIR" --exclude="$BACKUP_DIR" | while read -r num; do
        log_info "File changes detected, syncing..."
        sync_to_n8n false false
        log_success "Auto-sync completed"
    done
}

# Sync local files to n8n
sync_to_n8n() {
    local dry_run=${1:-false}
    local backup=${2:-true}
    
    log_info "Syncing local files to n8n..."
    import_all_workflows "$dry_run" "$backup" false
}

# Sync from n8n to local files
sync_from_n8n() {
    local dry_run=${1:-false}
    local force=${2:-false}
    
    log_info "Syncing from n8n to local files..."
    export_all_workflows "$dry_run" "$force"
}

# Intelligent bidirectional sync
sync_bidirectional() {
    local dry_run=${1:-false}
    
    log_info "Starting intelligent bidirectional sync..."
    
    if [[ "$dry_run" == "true" ]]; then
        log_info "[DRY RUN] Analyzing sync requirements..."
        compare_workflows
        return 0
    fi
    
    # Create backup before sync
    local backup_path=$(create_backup)
    
    # Export current state for comparison
    export_all_workflows false true
    
    # Import any new local files
    import_all_workflows false false false
    
    log_success "Bidirectional sync completed"
    log_info "Backup available at: $backup_path"
}

# Main function
main() {
    local command=${1:-help}
    local dry_run=false
    local force=false
    local backup=false
    local verbose=false
    
    # Parse options
    shift || true
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --force)
                force=true
                shift
                ;;
            --backup)
                backup=true
                shift
                ;;
            --verbose)
                verbose=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Load configuration
    load_config
    
    # Execute command
    case $command in
        init)
            init_config
            ;;
        export-all)
            check_n8n_connection
            export_all_workflows "$dry_run" "$force"
            ;;
        import-all)
            check_n8n_connection
            import_all_workflows "$dry_run" "$backup" "$force"
            ;;
        sync-to-n8n)
            check_n8n_connection
            sync_to_n8n "$dry_run" "$backup"
            ;;
        sync-from-n8n)
            check_n8n_connection
            sync_from_n8n "$dry_run" "$force"
            ;;
        sync-bidirectional)
            check_n8n_connection
            sync_bidirectional "$dry_run"
            ;;
        list-local)
            list_local_workflows
            ;;
        list-remote)
            check_n8n_connection
            list_remote_workflows
            ;;
        compare)
            check_n8n_connection
            compare_workflows
            ;;
        backup)
            check_n8n_connection
            create_backup
            ;;
        watch)
            check_n8n_connection
            watch_files
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"