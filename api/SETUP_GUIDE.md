# Complete Setup Guide - RAG Chatbot with Qdrant Cloud

This guide provides step-by-step instructions to set up the complete RAG chatbot system using Qdrant Cloud and FastEmbed.

## Prerequisites

- Python 3.11 or higher
- Google Gemini API key (for LLM responses)
- Qdrant Cloud account (free tier available at https://cloud.qdrant.io)

## Step 1: Get Qdrant Cloud Credentials

### 1.1 Create Qdrant Cloud Account

1. Go to https://cloud.qdrant.io/signup
2. Sign up with email, Google, or GitHub
3. Verify your email if required

### 1.2 Create a Cluster

1. In the Cloud Dashboard, go to **Clusters**
2. Click **Create First Cluster** (or **Create Cluster** if you have existing clusters)
3. Choose a cluster name and region
4. Select the free tier (if available) or your preferred plan
5. Wait for cluster creation (usually 1-2 minutes)

### 1.3 Get API Key and URL

1. Once cluster is created, go to the **Cluster Detail Page**
2. Navigate to the **API Keys** section
3. Click **Create** to generate a new API key
4. **IMPORTANT**: Copy the API key immediately - it's only shown once!
5. Copy your cluster URL from the cluster details (format: `https://your-cluster-id.cloud-region.cloud-provider.cloud.qdrant.io`)

**Note**: According to Qdrant documentation:
- API keys can have granular access control (for clusters v1.11.0+)
- You can set expiration dates for security
- API keys are required for all REST and gRPC requests

## Step 2: Install Dependencies

```bash
cd api
pip install -e .
```

Or using `uv` (recommended for faster installs):
```bash
cd api
uv pip install -e .
```

This installs:
- `fastapi` - Web framework
- `qdrant-client` - Qdrant Python client
- `fastembed` - FastEmbed for embeddings
- `google-generativeai` - Google Gemini API client
- `tiktoken` - Token counting
- Other dependencies

## Step 3: Configure Environment Variables

Create a `.env` file in the `api/` directory:

```bash
# Required: Qdrant Cloud Configuration
QDRANT_API_KEY=your-api-key-from-step-1-3
QDRANT_URL=https://your-cluster-id.cloud-region.cloud-provider.cloud.qdrant.io

# Required: Google Gemini Configuration
GEMINI_API_KEY=sk-your-openai-api-key

# Optional: API Configuration
API_BASE_URL=http://localhost:8000
ENVIRONMENT=development
```

**Security Note**: 
- Never commit `.env` to version control
- Use environment variables in production
- Rotate API keys regularly (Qdrant recommends setting expiration)

## Step 4: Index Book Content

Run the indexing script to populate Qdrant Cloud with all book content:

```bash
python scripts/index_chapters.py
```

### What the Script Does:

1. **Finds all markdown files** recursively in `../my-website/docs/physical-ai/`
2. **Chunks content** using token-aware splitting (512 tokens per chunk, 64 token overlap)
3. **Generates embeddings** using FastEmbed with `BAAI/bge-small-en-v1.5` (384 dimensions)
4. **Uploads to Qdrant Cloud** in batches of 100 points

### Expected Output:

```
Found 25 markdown files
Processing (1/25): introduction-overview.md
  Read 1234 characters
  Chapter ID: physical-ai/introduction/introduction-overview
  Created 3 chunks
  Generated 3 embeddings
  ✅ Processed introduction-overview.md: 3 chunks
...
✅ All points uploaded successfully
Collection Info:
  Name: book_chapters
  Vectors: 1250
  Points: 1250
  Status: green
```

### Troubleshooting Indexing:

- **"Failed to connect to Qdrant"**: Check your `QDRANT_URL` and `QDRANT_API_KEY`
- **"No .md files found"**: Verify `my-website/docs/physical-ai/` directory exists
- **"Embedding generation failed"**: FastEmbed downloads model on first use (may take 1-2 minutes)

## Step 5: Start the API Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Verify Connection:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-XX..."
}
```

## Step 6: Test the Endpoints

### Test Global Search (Full-Book)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ROS 2?"
  }'
```

Expected response includes:
- `answer`: LLM-generated response
- `sources`: Array of chapter citations
- `conversation_id`: Session identifier
- `grounded`: `false` (global mode)

### Test Grounded Search (SelectionContext)

```bash
curl -X POST http://localhost:8000/chat/grounded \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain this concept",
    "selected_text": "ROS 2 is the backbone of modern robotics development...",
    "source_chapter": "module-1-ros2/chapter-1-introduction"
  }'
```

Expected response includes:
- `answer`: Response based ONLY on selected text
- `grounded_in`: Preview of selected text
- `conversation_id`: Session identifier
- `grounded`: `true` (grounded mode)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   /chat      │  │ /chat/      │  │   /health    │  │
│  │  (Global)    │  │ grounded    │  │              │  │
│  └──────┬───────┘  └──────┬──────┘  └──────────────┘  │
└─────────┼──────────────────┼───────────────────────────┘
          │                  │
          │                  │ (No vector search)
          │                  │
          ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│  FastEmbed      │  │  OpenAI GPT-4   │
│  (Embeddings)   │  │  (LLM)          │
└────────┬────────┘  └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Qdrant Cloud   │
│  (Vector Store)  │
│  - Collection:   │
│    book_chapters │
│  - Dimensions:   │
│    384           │
│  - Distance:     │
│    Cosine        │
└─────────────────┘
```

## Qdrant Cloud Best Practices

Based on official Qdrant documentation:

1. **API Key Security**:
   - Set expiration dates (default: 90 days)
   - Rotate keys regularly
   - Use granular access control for production (v1.11.0+)

2. **Connection**:
   - Use HTTPS URLs provided by Qdrant Cloud
   - Include API key in all requests
   - Handle connection timeouts gracefully (we use 30s timeout)

3. **Collection Management**:
   - Use descriptive collection names
   - Match vector dimensions to your embedding model (384 for bge-small-en-v1.5)
   - Use Cosine distance for semantic similarity

4. **Performance**:
   - Batch operations when possible (we batch in 100s)
   - Use appropriate `limit` values for searches
   - Set `score_threshold` to filter low-quality results

## Troubleshooting

### Connection Issues

**Error**: "Failed to connect to Qdrant"
- Verify `QDRANT_URL` format: `https://cluster-id.region.provider.cloud.qdrant.io`
- Check `QDRANT_API_KEY` is correct
- Ensure cluster is active in Qdrant Cloud dashboard
- Check firewall/network settings

**Error**: "Authentication failed"
- Verify API key hasn't expired
- Check API key has correct permissions (read/write for indexing)
- Try creating a new API key

### Embedding Issues

**Error**: "Embedder not initialized"
- FastEmbed downloads model on first use (~100MB)
- Ensure internet connection is available
- Check disk space for model cache
- Wait 1-2 minutes for initial download

### Indexing Issues

**Error**: "No .md files found"
- Verify path: `my-website/docs/physical-ai/`
- Check file permissions
- Ensure files are readable

**Error**: "Collection not found"
- Run indexing script to create collection
- Check collection name matches config (`book_chapters`)

## Next Steps

1. **Integrate with Frontend**: Update `my-website/src/utils/config.ts` with API URL
2. **Monitor Usage**: Check Qdrant Cloud dashboard for usage metrics
3. **Optimize**: Adjust `TOP_K_RESULTS` and `SIMILARITY_THRESHOLD` based on results
4. **Scale**: Upgrade Qdrant Cloud plan if needed for production

## Resources

- [Qdrant Cloud Documentation](https://qdrant.tech/documentation/cloud-intro/)
- [Qdrant Python Client](https://qdrant.tech/documentation/guides/python-client/)
- [FastEmbed Documentation](https://github.com/qdrant/fastembed)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For issues:
1. Check logs in console for detailed error messages
2. Verify all environment variables are set correctly
3. Test Qdrant connection using Qdrant Cloud dashboard
4. Review API documentation at `http://localhost:8000/docs`

