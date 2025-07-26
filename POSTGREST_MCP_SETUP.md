# PostgREST MCP Server Setup Guide

## Overview
The PostgREST MCP server provides direct database access through the Model Context Protocol, enabling AI assistants to perform database queries and operations on PostgreSQL databases via PostgREST.

## Installation

### Method 1: NPX (Recommended)
```bash
npx @supabase-community/mcp-server-postgrest
```

### Method 2: Global Installation
```bash
npm install -g @supabase-community/mcp-server-postgrest
```

### Method 3: Local Project Installation
```bash
npm install @supabase-community/mcp-server-postgrest
```

## Configuration

### Required Parameters

#### PostgREST API URL
- **Parameter**: `PostgREST API URL`
- **Format**: `https://your-project-ref.supabase.co/rest/v1`
- **Example**: `https://abcdefghijklmnop.supabase.co/rest/v1`

#### PostgREST API Key (Optional)
- **Parameter**: `PostgREST API Key`
- **Description**: API key for authentication (use service_role key for full access)
- **Example**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

#### PostgREST Schema
- **Parameter**: `PostgREST Schema`
- **Default**: `public`
- **Description**: Database schema to access

## VSCode MCP Configuration

Add to your `.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "postgrest": {
      "command": "npx",
      "args": ["@supabase-community/mcp-server-postgrest"],
      "env": {
        "POSTGREST_URL": "https://your-project-ref.supabase.co/rest/v1",
        "POSTGREST_API_KEY": "your-service-role-key",
        "POSTGREST_SCHEMA": "public"
      }
    }
  }
}
```

## Environment Variables

Create or update your `.env` file:

```env
# PostgREST MCP Configuration
POSTGREST_URL=https://your-project-ref.supabase.co/rest/v1
POSTGREST_API_KEY=your-service-role-key
POSTGREST_SCHEMA=public

# Supabase Configuration (for reference)
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
```

## Getting Your Supabase Credentials

### 1. PostgREST API URL
- Go to your Supabase project dashboard
- Navigate to **Settings > API**
- Copy the **URL** field
- Append `/rest/v1` to get: `https://your-project-ref.supabase.co/rest/v1`

### 2. API Key
- In the same **Settings > API** section
- Copy the **service_role** key (for full database access)
- Or use **anon** key (for public access only)

### 3. Schema
- Default is `public`
- You can specify other schemas if needed

## Capabilities

The PostgREST MCP server provides:

### Database Operations
- **SELECT**: Query data from tables
- **INSERT**: Add new records
- **UPDATE**: Modify existing records
- **DELETE**: Remove records
- **UPSERT**: Insert or update records

### Advanced Features
- **Filtering**: Complex WHERE clauses
- **Ordering**: Sort results
- **Pagination**: Limit and offset
- **Joins**: Relationship queries
- **Aggregation**: Count, sum, avg, etc.
- **Full-text Search**: PostgreSQL text search

### Real-time Capabilities
- **Subscriptions**: Live data updates
- **Change Streams**: Monitor data changes
- **Event Triggers**: React to database events

## Example Usage

Once configured, you can use natural language to interact with your database:

```
"Show me all active workflows"
"Create a new workflow with name 'Test Workflow'"
"Update the workflow with ID 'abc123' to set active = false"
"Count how many executions happened today"
"Find workflows created in the last week"
```

## Security Considerations

### API Key Selection
- **service_role**: Full database access (use for admin operations)
- **anon**: Limited access based on RLS policies (safer for general use)

### Row Level Security (RLS)
- Enable RLS on sensitive tables
- Create policies to control access
- Use anon key with RLS for secure operations

### Environment Protection
- Never commit API keys to version control
- Use environment variables for credentials
- Rotate keys regularly

## Testing the Setup

### 1. Test MCP Server
```bash
npx @supabase-community/mcp-server-postgrest --help
```

### 2. Test Database Connection
Create a test script:

```javascript
// test-postgrest.js
const fetch = require('node-fetch');

const POSTGREST_URL = process.env.POSTGREST_URL;
const API_KEY = process.env.POSTGREST_API_KEY;

async function testConnection() {
  try {
    const response = await fetch(`${POSTGREST_URL}/workflow_entity?limit=1`, {
      headers: {
        'apikey': API_KEY,
        'Authorization': `Bearer ${API_KEY}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ PostgREST connection successful');
      console.log('Sample data:', data);
    } else {
      console.log('❌ PostgREST connection failed:', response.status);
    }
  } catch (error) {
    console.log('❌ Error:', error.message);
  }
}

testConnection();
```

Run with:
```bash
node test-postgrest.js
```

## Troubleshooting

### Common Issues

1. **Invalid API URL**
   - Ensure URL ends with `/rest/v1`
   - Check project reference in URL
   - Verify project is active

2. **Authentication Errors**
   - Check API key is correct
   - Ensure key has required permissions
   - Verify key type (anon vs service_role)

3. **Schema Not Found**
   - Verify schema name (usually 'public')
   - Check if tables exist in specified schema
   - Ensure database migration completed

4. **CORS Issues**
   - Configure CORS in Supabase dashboard
   - Add your domain to allowed origins

### Debug Mode
Enable debug logging:
```bash
DEBUG=* npx @supabase-community/mcp-server-postgrest
```

## Integration with n8n Migration

After migrating n8n to PostgreSQL:

1. **Complete the database migration** using the migration scripts
2. **Import your data** to Supabase
3. **Configure PostgREST MCP** with your Supabase credentials
4. **Test the connection** with sample queries
5. **Start using AI** to interact with your n8n database

## Next Steps

1. Complete n8n PostgreSQL migration
2. Set up PostgREST MCP server
3. Configure AI assistant with MCP
4. Test database operations
5. Explore advanced PostgREST features

---

**Repository**: [supabase-community/supabase-mcp](https://github.com/supabase-community/supabase-mcp/tree/HEAD/packages/mcp-server-postgrest)

**Documentation**: [PostgREST Documentation](https://postgrest.org/en/stable/)