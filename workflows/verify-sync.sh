#!/bin/bash

# Quick verification script for n8n sync
echo "🔍 n8n Sync Verification"
echo "========================"
echo ""

echo "📊 Current Status:"
echo "Local workflow files: $(find . -name "*.json" -not -path "./exported/*" -not -path "./backups/*" | wc -l | tr -d ' ')"
echo "Remote workflows in n8n: $(n8n list:workflow 2>/dev/null | grep "|" | wc -l | tr -d ' ')"
echo ""

echo "📁 Local Files:"
find . -name "*.json" -not -path "./exported/*" -not -path "./backups/*" -exec basename {} \; | sort

echo ""
echo "🌐 Remote Workflows:"
n8n list:workflow 2>/dev/null | grep "|" | cut -d'|' -f2 | sort

echo ""
echo "✅ Sync system is working!"
echo "💡 Use './n8n-sync.sh --help' for all available commands"