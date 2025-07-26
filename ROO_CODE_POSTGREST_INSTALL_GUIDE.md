# Roo Code PostgREST Installation Guide

## 🎯 Quick Installation Steps

### Option 1: Install via Roo Marketplace (Recommended)
1. **Open Roo Marketplace** in VSCode (as shown in your screenshot)
2. **Find "Postgrest"** (the bottom option by supabase-community)
3. **Click "Install"** button for the Postgrest MCP server
4. **Configure Environment Variables** (see below)

### Option 2: Use Local Installation (Already Done)
The local PostgREST MCP server is already built and configured in:
- **Location**: `supabase-mcp/packages/mcp-server-postgrest/dist/stdio.cjs`
- **Configuration**: `.vscode/mcp.json` (just created)

## 🔧 Configuration Files Created

### `.vscode/mcp.json`
```json
{
  "mcpServers": {
    "postgrest": {
      "command": "node",
      "args": ["${workspaceFolder}/supabase-mcp/packages/mcp-server-postgrest/dist/stdio.cjs"],
      "env": {
        "POSTGREST_URL": "${POSTGREST_URL}",
        "POSTGREST_API_KEY": "${POSTGREST_API_KEY}",
        "POSTGREST_SCHEMA": "${POSTGREST_SCHEMA:-public}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## 🌐 Required Environment Variables

Add to your `.env` file:

```env
# PostgREST MCP Configuration
POSTGREST_URL=https://your-project-ref.supabase.co/rest/v1
POSTGREST_API_KEY=your-service-role-key
POSTGREST_SCHEMA=public

# GitHub Token (optional)
GITHUB_TOKEN=your_github_personal_access_token

# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## 📋 Installation Options

### From Roo Marketplace
- **PostgreSQL Reader**: Read-only access to PostgreSQL databases
- **Neon Database**: Specifically for Neon PostgreSQL databases
- **Postgrest** ⭐: Full PostgREST functionality (recommended)

### Which One to Choose?
**Choose "Postgrest"** (the bottom option) because it provides:
- Full CRUD operations (Create, Read, Update, Delete)
- Advanced querying capabilities
- Real-time subscriptions
- Schema introspection
- Direct PostgREST API access

## 🚀 After Installation

### 1. Verify Installation
- Check if the "Install" button changes to "Installed" or disappears
- Look for PostgREST in Roo Code's MCP settings panel

### 2. Configure Credentials
- Complete your Supabase project setup
- Update `.env` file with actual credentials
- Restart VSCode to load new environment variables

### 3. Test Integration
Once configured, you can ask Roo Code:
- "Show me all tables in the database"
- "List active workflows"
- "Count total executions"

## 🔄 Next Steps

1. **Install from Marketplace**: Click "Install" on the Postgrest option
2. **Complete Migration**: Run `./quick_start_migration.sh`
3. **Setup Supabase**: Create project and get credentials
4. **Test Database Operations**: Use Roo Code with natural language

## 🛠️ Troubleshooting

### If Install Button Remains Active
1. Try refreshing the Roo Marketplace
2. Restart VSCode
3. Check if environment variables are properly set
4. Verify the local build is working: `node supabase-mcp/packages/mcp-server-postgrest/dist/stdio.cjs`

### If MCP Server Not Detected
1. Ensure `.vscode/mcp.json` exists (✅ created)
2. Check environment variables in `.env` file
3. Restart Roo Code extension
4. Verify file paths are correct

---

**Current Status**: 
- ✅ Local PostgREST MCP server built and ready
- ✅ MCP configuration files created
- 🔄 Ready for Roo Marketplace installation
- 🔄 Awaiting Supabase credentials for full functionality