# Shopware to Qdrant Product Import Workflow

This n8n workflow extracts product data from a Shopware store via the Admin API and imports it into a Qdrant vector database for AI-powered chatbot applications.

## Overview

The workflow performs a complete bulk import of all products from your Shopware store, transforming the data into vector embeddings suitable for semantic search and question-answering applications.

## Workflow Components

### 1. Authentication
- **OAuth2 Token Retrieval**: Uses client credentials flow to authenticate with Shopware API
- **Credentials**: Pre-configured with your Shopware API credentials
- **Token Management**: Automatically handles access token for subsequent API calls

### 2. Data Extraction
- **Paginated API Calls**: Fetches all products using pagination (50 products per page)
- **Complete Product Data**: Retrieves comprehensive product information including:
  - Product names and descriptions
  - Pricing information
  - Stock levels
  - Categories and properties
  - Manufacturer details
  - SEO information

### 3. Data Transformation
- **Text Preparation**: Combines relevant product fields into searchable content
- **Metadata Extraction**: Preserves structured data for filtering and retrieval
- **Content Optimization**: Formats data specifically for chatbot question-answering

### 4. Vector Storage
- **Embedding Generation**: Uses OpenAI's text-embedding-3-small model
- **Batch Processing**: Processes products in batches for efficiency
- **Qdrant Integration**: Stores vectors in your configured Qdrant collection

## Prerequisites

### Required n8n Nodes
Ensure these nodes are installed in your n8n instance:
- `@n8n/n8n-nodes-langchain.embeddingsOpenAi`
- `@n8n/n8n-nodes-langchain.vectorStoreQdrant`

### Required Credentials
1. **OpenAI API Key**: For embedding generation
2. **Qdrant Connection**: Your Qdrant Cloud credentials

## Setup Instructions

### 1. Import the Workflow
1. Copy the contents of `shopware-to-qdrant-import.json`
2. In n8n, go to Workflows → Import from JSON
3. Paste the JSON content and import

### 2. Configure Credentials

#### OpenAI Credentials
1. Go to Settings → Credentials
2. Create new "OpenAI" credential
3. Add your OpenAI API key

#### Qdrant Credentials
1. Create new "Qdrant" credential
2. Configure with your Qdrant Cloud details:
   - URL: Your Qdrant cluster URL
   - API Key: Your Qdrant API key

### 3. Configure Collection
1. Open the "Insert into Qdrant" node
2. Set the collection name to `shopware_products` (or your preferred name)
3. Ensure the collection exists in your Qdrant instance

### 4. Test the Workflow
1. Start with a small test by modifying the limit in "Initialize Pagination" to 5-10 products
2. Execute the workflow manually
3. Verify data appears correctly in Qdrant
4. Reset limit to 50 for full import

## Data Structure

### Vector Content
Each product is stored as a vector with combined text content:
```
Product Name | Description | Meta Description | Properties | Categories | Manufacturer Number | EAN
```

### Metadata Structure
```json
{
  "id": "product-uuid",
  "name": "Product Name",
  "price": 29.99,
  "currency": "EUR",
  "stock": 100,
  "active": true,
  "manufacturerNumber": "MFG123",
  "ean": "1234567890123",
  "categories": ["Category 1", "Category 2"],
  "properties": [{"name": "Color", "value": "Blue"}],
  "url": "product-seo-url",
  "createdAt": "2024-01-01T00:00:00.000Z",
  "updatedAt": "2024-01-01T00:00:00.000Z"
}
```

## Workflow Execution

### Manual Execution
1. Open the workflow in n8n
2. Click "Execute Workflow" 
3. Monitor progress in the execution log
4. Check completion status in the final log node

### Expected Execution Time
- Small catalogs (< 1000 products): 2-5 minutes
- Medium catalogs (1000-5000 products): 10-20 minutes
- Large catalogs (> 5000 products): 30+ minutes

## Troubleshooting

### Common Issues

#### Authentication Errors
- Verify Shopware API credentials are correct
- Check that the integration has proper permissions in Shopware admin

#### Rate Limiting
- Shopware may rate limit API calls
- The workflow includes reasonable delays between requests
- If needed, reduce batch sizes in the pagination logic

#### Embedding Errors
- Ensure OpenAI API key is valid and has sufficient credits
- Check that text content isn't exceeding OpenAI's token limits

#### Qdrant Connection Issues
- Verify Qdrant credentials and cluster URL
- Ensure the collection exists and is accessible
- Check Qdrant cluster status

### Monitoring Progress
The workflow includes logging at key stages:
- OAuth token acquisition
- Page fetching progress
- Data transformation completion
- Vector insertion status
- Final completion summary

## Customization Options

### Adjusting Batch Sizes
- **API Pagination**: Modify `limit` in "Initialize Pagination" (default: 50)
- **Embedding Batch**: Adjust `batchSize` in "Generate Embeddings" (default: 100)
- **Qdrant Insertion**: Modify `batchSize` in "Insert into Qdrant" (default: 50)

### Content Customization
Modify the "Transform Products for Vector Storage" node to:
- Include/exclude specific product fields
- Change text formatting for embeddings
- Add custom metadata fields
- Filter products by specific criteria

### Collection Configuration
- Change collection name in "Insert into Qdrant" node
- Modify vector dimensions if using different embedding models
- Adjust distance metrics in Qdrant collection settings

## Performance Optimization

### For Large Catalogs
1. **Increase Batch Sizes**: Higher batch sizes for API calls and vector operations
2. **Parallel Processing**: Consider splitting into multiple workflows by category
3. **Incremental Updates**: Implement delta sync for ongoing updates

### Memory Considerations
- Large product catalogs may require increased n8n memory limits
- Consider processing in smaller chunks if memory issues occur

## Next Steps

After successful import:
1. **Test Vector Search**: Query your Qdrant collection to verify data quality
2. **Implement Chatbot**: Connect your AI chatbot to the Qdrant collection
3. **Set Up Monitoring**: Implement alerts for failed imports
4. **Plan Updates**: Consider scheduling regular updates for product changes

## Support

For issues with:
- **n8n Workflow**: Check n8n community forums and documentation
- **Shopware API**: Refer to Shopware developer documentation
- **Qdrant Integration**: Consult Qdrant documentation and support
- **OpenAI Embeddings**: Check OpenAI API documentation

## API Endpoints Used

- **OAuth Token**: `POST https://shop.held.de/api/oauth/token`
- **Products**: `GET https://shop.held.de/api/product?page={page}&limit={limit}`

## Security Notes

- API credentials are embedded in the workflow - ensure n8n instance is secure
- Consider using n8n credential management for production deployments
- Regularly rotate API keys and tokens
- Monitor API usage and access logs