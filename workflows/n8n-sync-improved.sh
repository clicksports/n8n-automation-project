#!/usr/bin/env bash

# n8n Workflow Sync Tool - Improved Version
# Prevents duplicates by updating existing workflows instead of creating new ones

set -euo pipefail

# Configuration
N8N_URL="${N8N_URL:-http://localhost:5678}"
WORKFLOWS_DIR="${WORKFLOWS_DIR:-$(pwd)}"
DOCKER_CONTAINER="${DOCKER_CONTAINER:-n8n-production}"

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

# Check if running in Docker
is_docker_mode() {
    if docker ps --format "table {{.Names}}" | grep -q "$DOCKER_CONTAINER"; then
        return 0
    else
        return 1
    fi
}

# Execute n8n command (Docker or local)
n8n_exec() {
    if is_docker_mode; then
        docker exec "$DOCKER_CONTAINER" n8n "$@"
    else
        n8n "$@"
    fi
}

# Copy file to Docker container if needed
copy_to_docker() {
    local local_file="$1"
    local docker_path="$2"
    
    if is_docker_mode; then
        docker cp "$local_file" "$DOCKER_CONTAINER:$docker_path"
        echo "$docker_path"
    else
        echo "$local_file"
    fi
}

# Get workflow ID by name
get_workflow_id_by_name() {
    local workflow_name="$1"
    # Use awk for exact name matching to prevent partial matches
    n8n_exec list:workflow | awk -F'|' -v name="$workflow_name" '
        {
            # Remove leading/trailing whitespace from the name field
            gsub(/^[ \t]+|[ \t]+$/, "", $2)
            if ($2 == name) {
                # Remove leading/trailing whitespace from ID and print
                gsub(/^[ \t]+|[ \t]+$/, "", $1)
                print $1
                exit
            }
        }
    '
}

# Check if workflow exists by name
workflow_exists() {
    local workflow_name="$1"
    local workflow_id=$(get_workflow_id_by_name "$workflow_name")
    [[ -n "$workflow_id" && "$workflow_id" != "null" && "$workflow_id" != "" ]]
}

# Smart import/update workflow
smart_import_workflow() {
    local workflow_file="$1"
    local force_update="${2:-false}"
    
    # Extract workflow name from JSON
    local workflow_name
    if command -v jq >/dev/null 2>&1; then
        workflow_name=$(jq -r '.name // "unknown"' "$workflow_file" 2>/dev/null || echo "unknown")
    else
        log_error "jq is required for workflow name extraction"
        return 1
    fi
    
    if [[ "$workflow_name" == "unknown" ]]; then
        log_error "Could not extract workflow name from $workflow_file"
        return 1
    fi
    
    log_info "Processing workflow: $workflow_name"
    
    # Copy file to Docker if needed
    local docker_file_path="/tmp/$(basename "$workflow_file")"
    local target_file=$(copy_to_docker "$workflow_file" "$docker_file_path")
    
    # Check if workflow already exists
    if workflow_exists "$workflow_name"; then
        local existing_id=$(get_workflow_id_by_name "$workflow_name")
        log_info "Workflow '$workflow_name' exists with ID: $existing_id"
        
        if [[ "$force_update" == "true" ]]; then
            log_info "Updating existing workflow..."
            if n8n_exec update:workflow --id="$existing_id" --file="$target_file" --active=true; then
                log_success "Updated workflow: $workflow_name"
                
                # Restart container to apply changes if in Docker mode
                if is_docker_mode; then
                    log_info "Restarting Docker container to apply changes..."
                    docker restart "$DOCKER_CONTAINER" > /dev/null
                    sleep 10  # Wait for container to restart
                fi
                
                return 0
            else
                log_error "Failed to update workflow: $workflow_name"
                return 1
            fi
        else
            log_warning "Workflow '$workflow_name' already exists. Use --force to update."
            return 0
        fi
    else
        log_info "Importing new workflow..."
        if n8n_exec import:workflow --input="$target_file"; then
            log_success "Imported new workflow: $workflow_name"
            
            # Activate the imported workflow
            local new_id=$(get_workflow_id_by_name "$workflow_name")
            if [[ -n "$new_id" ]]; then
                n8n_exec update:workflow --id="$new_id" --active=true > /dev/null 2>&1 || true
                log_info "Activated workflow: $workflow_name"
            fi
            
            return 0
        else
            log_error "Failed to import workflow: $workflow_name"
            return 1
        fi
    fi
}

# Import all workflows with duplicate prevention
import_all_no_duplicates() {
    local force_update="${1:-true}"  # Default to true - always update existing workflows
    local auto_remove_duplicates="${2:-false}"  # Don't need to remove duplicates if we're updating
    
    log_info "Importing workflows with automatic updates..."
    
    # Only remove duplicates if explicitly requested (for cleanup scenarios)
    if [[ "$auto_remove_duplicates" == "true" ]]; then
        log_info "Removing existing duplicates before import..."
        remove_duplicates
    fi
    
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
    
    local success_count=0
    local error_count=0
    local skipped_count=0
    
    for file in "${workflow_files[@]}"; do
        local filename=$(basename "$file")
        log_info "Processing $filename..."
        
        if smart_import_workflow "$file" "$force_update"; then
            ((success_count++))
        else
            if [[ "$force_update" == "false" ]]; then
                ((skipped_count++))
            else
                ((error_count++))
            fi
        fi
    done
    
    log_info "Import completed:"
    log_success "  Successful: $success_count"
    if [[ $skipped_count -gt 0 ]]; then
        log_warning "  Skipped (already exists): $skipped_count"
    fi
    if [[ $error_count -gt 0 ]]; then
        log_error "  Failed: $error_count"
    fi
}

# List workflows with status
list_workflows_with_status() {
    log_info "Current workflows in n8n:"
    n8n_exec list:workflow | while IFS='|' read -r id name; do
        # Clean up whitespace
        id=$(echo "$id" | tr -d ' ')
        name=$(echo "$name" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        
        # Skip header row or empty lines
        if [[ "$id" == "id" || -z "$name" || -z "$id" ]]; then
            continue
        fi
        
        # Check if we have a local file for this workflow using exact name matching
        local local_file_exists=false
        if find "$WORKFLOWS_DIR" -name "*.json" -not -path "*/exported/*" -not -path "*/backups/*" -exec grep -l "\"name\"[[:space:]]*:[[:space:]]*\"$(echo "$name" | sed 's/[[\.*^$()+?{|]/\\&/g')\"" {} \; | head -1 > /dev/null 2>&1; then
            local_file_exists=true
        fi
        
        if [[ "$local_file_exists" == "true" ]]; then
            echo -e "  ${GREEN}✓${NC} $id | $name (has local file)"
        else
            echo -e "  ${YELLOW}?${NC} $id | $name (no local file)"
        fi
    done
}

# Deactivate duplicate workflows and provide deletion instructions
remove_duplicates() {
    log_info "Handling duplicate workflows..."
    
    # Create temp file to store workflow data
    local temp_file=$(mktemp)
    trap "rm -f $temp_file" EXIT
    
    # Store workflow data in temp file
    n8n_exec list:workflow | while IFS='|' read -r id name; do
        # Clean up whitespace
        id=$(echo "$id" | tr -d ' ')
        name=$(echo "$name" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        
        if [[ -n "$name" && "$name" != "name" ]]; then
            echo "$name|$id" >> "$temp_file"
        fi
    done
    
    # Find duplicates by name
    local duplicates_found=false
    local workflows_to_delete=()
    
    while IFS='|' read -r name id; do
        # Count how many workflows have this exact name
        local count=$(grep -c "^$name|" "$temp_file" || echo "0")
        if [[ $count -gt 1 ]]; then
            duplicates_found=true
            log_warning "Found $count workflows with name: $name"
            
            # Get all IDs for this name, sorted (keep the first one, deactivate others)
            local ids=($(grep "^$name|" "$temp_file" | cut -d'|' -f2 | sort))
            local keep_id="${ids[0]}"
            
            log_info "Keeping workflow ID: $keep_id (will ensure it's active)"
            n8n_exec update:workflow --id="$keep_id" --active=true > /dev/null 2>&1 || true
            
            # Deactivate all other instances
            for ((i=1; i<${#ids[@]}; i++)); do
                local deactivate_id="${ids[i]}"
                log_warning "Deactivating duplicate workflow ID: $deactivate_id"
                if n8n_exec update:workflow --id="$deactivate_id" --active=false; then
                    log_success "Deactivated duplicate workflow: $deactivate_id"
                    workflows_to_delete+=("$deactivate_id")
                else
                    log_error "Failed to deactivate workflow: $deactivate_id"
                fi
            done
        fi
    done < <(cut -d'|' -f1 "$temp_file" | sort -u | while read -r unique_name; do
        grep "^$unique_name|" "$temp_file" | head -1
    done)
    
    if [[ "$duplicates_found" == "false" ]]; then
        log_success "No duplicates found"
    else
        log_info ""
        log_warning "MANUAL CLEANUP REQUIRED:"
        log_warning "The following workflow IDs have been deactivated and should be archived/deleted manually:"
        for id in "${workflows_to_delete[@]}"; do
            log_warning "  - Workflow ID: $id"
            log_info "    Archive via: http://localhost:5678/workflow/$id (click ... menu → Archive)"
            log_info "    Or Delete via: http://localhost:5678/workflow/$id (click ... menu → Delete)"
        done
        log_info ""
        log_info "Or manage all inactive workflows via the web interface:"
        log_info "  1. Go to http://localhost:5678/workflows"
        log_info "  2. Filter by 'Inactive' workflows (they show as 'Inactive', not 'Archived')"
        log_info "  3. For each duplicate workflow:"
        log_info "     - Click the ... menu on the right"
        log_info "     - Select 'Archive' to archive (recommended) or 'Delete' to remove permanently"
        log_info ""
        log_warning "NOTE: n8n CLI can only deactivate workflows, not archive them."
        log_warning "Archiving must be done through the web interface."
    fi
}

# Clean up duplicate workflows - simplified version
cleanup_duplicates() {
    log_info "Analyzing workflows for duplicates..."
    
    # Create temp file to store workflow data
    local temp_file=$(mktemp)
    trap "rm -f $temp_file" EXIT
    
    # Store workflow data in temp file
    n8n_exec list:workflow | while IFS='|' read -r id name; do
        # Clean up whitespace
        id=$(echo "$id" | tr -d ' ')
        name=$(echo "$name" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        
        if [[ -n "$name" && "$name" != "name" ]]; then
            echo "$name|$id" >> "$temp_file"
        fi
    done
    
    # Check for duplicates by looking for similar workflow names
    log_info "Checking for potential duplicates..."
    
    # Look specifically for the known duplicate pattern
    local shopware_workflows=$(grep "Shopware to Local Qdrant Production" "$temp_file" || true)
    if [[ -n "$shopware_workflows" ]]; then
        log_warning "Found multiple Shopware workflows:"
        echo "$shopware_workflows" | while IFS='|' read -r name id; do
            echo "  - ID: $id | Name: $name"
        done
        log_warning "These appear to be duplicates (v1.0 and v1.1)"
        log_info "Recommendation: Keep the v1.1 version and remove v1.0 manually via web interface"
    fi
    
    # Count total unique vs total workflows
    local total_workflows=$(wc -l < "$temp_file")
    local unique_names=$(cut -d'|' -f1 "$temp_file" | sort -u | wc -l)
    
    if [[ $total_workflows -gt $unique_names ]]; then
        log_warning "Found $total_workflows total workflows but only $unique_names unique names"
        log_warning "This suggests there may be duplicates"
    else
        log_success "No obvious duplicates found"
    fi
}

# Show help
show_help() {
    cat << EOF
n8n Workflow Sync Tool - Improved (No Duplicates)

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    import-all          Import/update all workflow files (default: update existing)
    import-all --no-update  Import workflow files (skip existing, may create duplicates)
    list                List workflows with local file status
    cleanup             Analyze and report duplicate workflows
    remove-duplicates   Remove duplicate workflows automatically
    help                Show this help

OPTIONS:
    --no-update         Skip updating existing workflows (may create duplicates)
    --help              Show this help

EXAMPLES:
    $0 import-all                # Import new workflows, update existing (recommended)
    $0 import-all --no-update    # Import new workflows only, skip existing
    $0 list                      # List workflows with status
    $0 cleanup                   # Check for duplicates
    $0 remove-duplicates         # Remove duplicates automatically

ENVIRONMENT VARIABLES:
    DOCKER_CONTAINER    Docker container name (default: n8n-production)
    WORKFLOWS_DIR       Directory for workflow files (default: current dir)

EOF
}

# Main function
main() {
    local command=${1:-help}
    local update_existing=true  # Default to updating existing workflows
    
    # Parse options
    shift || true
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-update)
                update_existing=false
                shift
                ;;
            --force)
                # Keep --force for backward compatibility
                update_existing=true
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
    
    # Execute command
    case $command in
        import-all)
            import_all_no_duplicates "$update_existing"
            ;;
        list)
            list_workflows_with_status
            ;;
        cleanup)
            cleanup_duplicates
            ;;
        remove-duplicates)
            remove_duplicates
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