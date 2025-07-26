# Qdrant Cloud Configuration

## Connection Details

Your Qdrant Cloud instance is configured with the following details:

- **Cluster URL**: `https://8ec957ec-27b4-4041-9714-f8dde751b007.europe-west3-0.gcp.cloud.qdrant.io:6333`
- **API Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.50x-a9c0zTX_dzWnKjq-xM7rJ0ym6_yZ-D_eN_Idft4`
- **Region**: Europe West 3 (GCP)

## n8n Credential Setup

### 1. Create Qdrant Credential in n8n

1. Go to **Settings** → **Credentials** in your n8n instance
2. Click **Add Credential**
3. Search for and select **Qdrant**
4. Configure with these values:
   - **Host**: `8ec957ec-27b4-4041-9714-f8dde751b007.europe-west3-0.gcp.cloud.qdrant.io`
   - **Port**: `6333`
   - **API Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.50x-a9c0zTX_dzWnKjq-xM7rJ0ym6_yZ-D_eN_Idft4`
   - **Use SSL**: `true` (enabled)
5. **Test Connection** to verify
6. **Save** the credential

### 2. Collection Setup

Before running the workflow, ensure you have created the collection in Qdrant:

```bash
curl -X PUT 'https://8ec957ec-27b4-4041-9714-f8dde751b007.europe-west3-0.gcp.cloud.qdrant.io:6333/collections/shopware_products' \
  --header 'api-key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.50x-a9c0zTX_dzWnKjq-xM7rJ0ym6_yZ-D_eN_Idft4' \
  --header 'Content-Type: application/json' \
  --data '{
    "vectors": {
      "size": 1536,
      "distance": "Cosine"
    },
    "optimizers_config": {
      "default_segment_number": 2
    },
    "replication_factor": 1
  }'
```

### 3. Test Collection (Optional)

For testing purposes, create a separate test collection:

```bash
curl -X PUT 'https://8ec957ec-27b4-4041-9714-f8dde751b007.europe-west3-0.gcp.cloud.qdrant.io:6333/collections/shopware_products_test' \
  --header 'api-key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.50x-a9c0zTX_dzWnKjq-xM7rJ0ym6_yZ-D_eN_Idft4' \
  --header 'Content-Type: application/json' \
  --data '{
    "vectors": {
      "size": 1536,
      "distance": "Cosine"
    },
    "optimizers_config": {
      "default_segment_number": 1
    },
    "replication_factor": 1
  }'
```

## Verification Commands

### Check Cluster Status
```bash
curl -X GET 'https://8ec957ec-27b4-4041-9714-f8dde751b007.europe-west3-0.gcp.cloud.qdrant.io:6333' \
  --header 'api-key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.50x-a9c0zTX_dzWnKjq-xM7rJ0ym6_yZ-D_eN_Idft4'
```

### List Collections
```bash
curl -X GET 'https://8ec957ec-27b4-4041-9714-f8dde751b007.europe-west3-0.gcp.cloud.qdrant.io:6333/collections' \
  --header 'api-key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.50x-a9c0zTX_dzWnKjq-xM7rJ0ym6_yZ-D_eN_Idft4'
```

### Check Collection Info
```bash
curl -X GET 'https://8ec957ec-27b4-4041-9714-f8dde751b007.europe-west3-0.gcp.cloud.qdrant.io:6333/collections/shopware_products' \
  --header 'api-key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.50x-a9c0zTX_dzWnKjq-xM7rJ0ym6_yZ-D_eN_Idft4'
```

### Count Points in Collection
```bash
curl -X GET 'https://8ec957ec-27b4-4041-9714-f8dde751b007.europe-west3-0.gcp.cloud.qdrant.io:6333/collections/shopware_products/points/count' \
  --header 'api-key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.50x-a9c0zTX_dzWnKjq-xM7rJ0ym6_yZ-D_eN_Idft4'
```

## Security Notes

- Keep your API key secure and never commit it to version control
- The API key provided has management access to your Qdrant cluster
- Consider rotating the API key periodically for security
- Monitor usage and access logs in your Qdrant Cloud dashboard

## Troubleshooting

### Connection Issues
- Verify the cluster URL is accessible
- Check that the API key is correctly formatted
- Ensure SSL/TLS is enabled in n8n Qdrant credential
- Confirm firewall/network access to the cluster

### Collection Issues
- Verify collections exist before running import
- Check vector dimensions match (1536 for OpenAI text-embedding-3-small)
- Ensure sufficient storage space in your Qdrant plan
- Monitor collection performance and optimize as needed