<!--# Quick Start Guide - RAG Chatbot Backend

This guide will help you set up and run the RAG chatbot backend in minutes.

## Prerequisites

- Python 3.11 or higher
- OpenAI API key
- Qdrant Cloud account (free tier available)

## Step 1: Install Dependencies

```bash
cd api
pip install -e .
```

Or using `uv` (faster):
```bash
cd api
uv pip install -e .
```

## Step 2: Get Qdrant Cloud Credentials

1. Go to https://cloud.qdrant.io/
2. Sign up for a free account
3. Create a new cluster
4. Copy your API key and cluster URL

## Step 3: Configure Environment

Create a `.env` file in the `api/` directory:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key-here
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_URL=https://your-cluster-id.qdrant.io

# Optional (defaults work fine)
ENVIRONMENT=development
```

## Step 4: Index Book Content

Run the indexing script to populate Qdrant with all book content:

```bash
python scripts/index_chapters.py
```

This will:
- Find all `.md` files in `../my-website/docs/physical-ai/`
- Chunk the content (512 tokens per chunk)
- Generate embeddings using FastEmbed (`BAAI/bge-small-en-v1.5`)
- Upload to Qdrant Cloud

**Expected output:**
```
Found 25 markdown files
Processing (1/25): introduction-overview.md
...
✅ All points uploaded successfully
Collection Info:
  Vectors: 1250
  Points: 1250
```

## Step 5: Start the API Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## Step 6: Test the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Global Chat (Full-Book Search)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ROS 2?"
  }'
```

### Grounded Chat (Selected Text Mode)
```bash
curl -X POST http://localhost:8000/chat/grounded \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain this concept",
    "selected_text": "ROS 2 is the backbone of modern robotics development..."
  }'
```

## Troubleshooting

### "Qdrant client not connected"
- Check your `.env` file has correct `QDRANT_API_KEY` and `QDRANT_URL`
- Verify your Qdrant Cloud cluster is active
- Run the indexing script to create the collection

### "Embedder not initialized"
- FastEmbed downloads the model on first use (may take 1-2 minutes)
- Ensure you have internet connection
- Check disk space for model cache (~100MB)

### "No chunks found"
- Verify `my-website/docs/physical-ai/` directory exists
- Check that markdown files are readable
- Review script logs for specific errors

### Indexing takes too long
- This is normal for first run (model download + embedding generation)
- Subsequent runs are faster (model is cached)
- Large books may take 5-10 minutes

## Next Steps

- Integrate with frontend: Update `my-website/src/utils/config.ts` with API URL
- Test both query modes: Global search and grounded search
- Monitor Qdrant Cloud dashboard for usage

## Architecture Overview

```
User Query
    ↓
FastAPI Backend
    ↓
┌───────────┬───────────┐
│  Global   │ Grounded  │
│  Search   │  Search   │
└─────┬─────┴─────┬─────┘
      │           │
      ↓           ↓
  Qdrant      Selected
  Vector      Text
  Search      Only
      │           │
      └─────┬─────┘
            ↓
      OpenAI GPT-4
            ↓
      Response
```

## Support

For issues or questions, check:
- `README.md` for detailed documentation
- API docs at `http://localhost:8000/docs` (Swagger UI)
- Logs in console for debugging
-->
