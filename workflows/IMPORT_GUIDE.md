# n8n Workflow Import Guide

## Current Status
You currently have **only 1 workflow** visible in your n8n UI, but there are **4 additional workflow versions** available for import.

## Available Workflows to Import

1. **shopware-to-qdrant-import.json** - Basic version
2. **shopware-to-qdrant-import-enhanced.json** - Enhanced with error handling
3. **shopware-to-qdrant-import-fixed.json** - Fixed version for testing
4. **shopware-to-qdrant-complete.json** - Complete version with all features

## Step-by-Step Import Instructions

### 1. Access n8n
1. Open your browser and go to: `http://localhost:5678`
2. Sign in with your n8n credentials

### 2. Import Each Workflow

For each workflow file, follow these steps:

#### Method 1: Create New Workflow
1. Click the **"+"** button or **"Create Workflow"**
2. In the new workflow editor, click the **menu (⋮)** in the top-right
3. Select **"Import from JSON"**
4. Copy the entire content from one of the JSON files
5. Paste it into the import dialog
6. Click **"Import"**
7. Save the workflow

#### Method 2: Import from Workflows Page
1. Go to the **Workflows** page
2. Click **"Import from JSON"** button
3. Copy the entire content from one of the JSON files
4. Paste and import

### 3. Workflow Descriptions

#### Basic Version (`shopware-to-qdrant-import.json`)
- Simple product import workflow
- Basic error handling
- Good for initial testing

#### Enhanced Version (`shopware-to-qdrant-import-enhanced.json`)
- Comprehensive error handling
- Better logging and monitoring
- Enhanced data transformation
- **Recommended for production use**

#### Fixed Version (`shopware-to-qdrant-import-fixed.json`)
- Optimized for testing with smaller batches
- Limited to 2 pages for quick testing
- Good for development and debugging

#### Complete Version (`shopware-to-qdrant-complete.json`)
- Most comprehensive version
- Advanced error handling
- Detailed logging and statistics
- **Best for full production deployment**

## Quick Copy Commands

To quickly copy workflow content, use these commands in your terminal:

```bash
# Copy Basic Version
cat workflows/shopware-to-qdrant-import.json | pbcopy

# Copy Enhanced Version (Recommended)
cat workflows/shopware-to-qdrant-import-enhanced.json | pbcopy

# Copy Fixed Version (For Testing)
cat workflows/shopware-to-qdrant-import-fixed.json | pbcopy

# Copy Complete Version (Full Featured)
cat workflows/shopware-to-qdrant-complete.json | pbcopy
```

## After Import Setup

Once you've imported the workflows, you'll need to:

### 1. Configure Credentials
- **OpenAI API Key**: For embedding generation
- **Qdrant Connection**: Your Qdrant Cloud credentials

### 2. Test the Workflows
1. Start with the **Fixed Version** for testing (limited to 2 pages)
2. Verify data appears in your Qdrant collection
3. Then use the **Enhanced** or **Complete** version for full imports

### 3. Workflow Comparison

| Feature | Basic | Enhanced | Fixed | Complete |
|---------|-------|----------|-------|----------|
| Error Handling | Basic | Advanced | Advanced | Advanced |
| Logging | Simple | Detailed | Detailed | Comprehensive |
| Testing Limits | No | No | Yes (2 pages) | No |
| Production Ready | ❌ | ✅ | ❌ | ✅ |
| Recommended Use | Learning | Production | Testing | Full Production |

## Troubleshooting

### If Import Fails
1. Ensure the JSON is valid (check for syntax errors)
2. Make sure you're copying the entire file content
3. Try importing one workflow at a time
4. Check n8n logs for specific error messages

### If Workflows Don't Appear
1. Refresh the n8n interface
2. Check the Workflows page
3. Look for any error notifications
4. Verify you're signed in with the correct account

## Next Steps

After successful import:
1. ✅ **Verify workflows appear in the UI**
2. 🔧 **Configure credentials**
3. 🧪 **Test with Fixed version first**
4. 🚀 **Run full import with Enhanced/Complete version**

## Support Files

- `README.md` - Detailed workflow documentation
- `import-workflow.sh` - Single workflow import script
- `import-all-workflows.sh` - Batch import script (requires API access)
- `qdrant-credentials.md` - Qdrant setup instructions