#!/bin/bash

# Script to copy workflow JSON content to clipboard for easy import into n8n

echo "🚀 n8n Workflow Copy Helper"
echo "=========================="
echo ""

# Array of workflow files
WORKFLOW_FILES=(
    "shopware-to-qdrant-import-enhanced.json:Enhanced Version (Recommended)"
    "shopware-to-qdrant-import-fixed.json:Fixed Version (For Testing)"
    "shopware-to-qdrant-complete.json:Complete Version (Full Featured)"
    "shopware-to-qdrant-import.json:Basic Version"
)

echo "Available workflows to copy:"
echo ""

# Display menu
for i in "${!WORKFLOW_FILES[@]}"; do
    IFS=':' read -r file desc <<< "${WORKFLOW_FILES[$i]}"
    echo "$((i+1)). $desc"
    echo "   File: $file"
    echo ""
done

echo "Enter the number of the workflow you want to copy (1-${#WORKFLOW_FILES[@]}):"
read -r choice

# Validate input
if [[ ! "$choice" =~ ^[1-4]$ ]]; then
    echo "❌ Invalid choice. Please enter a number between 1 and ${#WORKFLOW_FILES[@]}."
    exit 1
fi

# Get selected file
selected_index=$((choice-1))
IFS=':' read -r selected_file selected_desc <<< "${WORKFLOW_FILES[$selected_index]}"

if [ ! -f "$selected_file" ]; then
    echo "❌ Workflow file $selected_file not found!"
    exit 1
fi

echo ""
echo "📋 Copying $selected_desc to clipboard..."
echo "File: $selected_file"
echo ""

# Copy to clipboard (works on macOS)
if command -v pbcopy >/dev/null 2>&1; then
    cat "$selected_file" | pbcopy
    echo "✅ Workflow JSON copied to clipboard!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Go to http://localhost:5678 in your browser"
    echo "2. Sign in if needed"
    echo "3. Click 'Create Workflow' or '+' button"
    echo "4. Click the menu (⋮) → 'Import from File...' or 'Import from URL...'"
    echo "5. Paste the JSON content (Cmd+V)"
    echo "6. Click 'Import'"
    echo ""
    echo "🎯 You're importing: $selected_desc"
elif command -v xclip >/dev/null 2>&1; then
    cat "$selected_file" | xclip -selection clipboard
    echo "✅ Workflow JSON copied to clipboard!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Go to http://localhost:5678 in your browser"
    echo "2. Sign in if needed"
    echo "3. Click 'Create Workflow' or '+' button"
    echo "4. Click the menu (⋮) → 'Import from File...' or 'Import from URL...'"
    echo "5. Paste the JSON content (Ctrl+V)"
    echo "6. Click 'Import'"
    echo ""
    echo "🎯 You're importing: $selected_desc"
else
    echo "⚠️  Clipboard tool not found. Here's the JSON content:"
    echo "================================"
    cat "$selected_file"
    echo ""
    echo "================================"
    echo ""
    echo "📝 Copy the above JSON content and:"
    echo "1. Go to http://localhost:5678 in your browser"
    echo "2. Sign in if needed"
    echo "3. Click 'Create Workflow' or '+' button"
    echo "4. Click the menu (⋮) → 'Import from File...' or 'Import from URL...'"
    echo "5. Paste the JSON content"
    echo "6. Click 'Import'"
fi

echo ""
echo "🔄 Run this script again to copy another workflow!"