<!--# Physical AI Book RAG Chatbot Backend

FastAPI backend for the Physical AI & Humanoid Robotics book chatbot. Provides RAG (Retrieval-Augmented Generation) capabilities with two query modes:

1. **Global Search**: Full-book semantic search with citations
2. **Grounded Search**: Answers based strictly on selected text (Magna Carta feature)

## Features

- **FastEmbed Integration**: Uses `BAAI/bge-small-en-v1.5` for efficient embeddings (384 dimensions)
- **Qdrant Cloud**: Vector store for semantic search
- **OpenAI GPT-4**: LLM for generating responses
- **Automatic Indexing**: Script to index all book content from `my-website/docs`

## Setup

### 1. Install Dependencies

```bash
cd api
pip install -e .
# Or using uv:
uv pip install -e .
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `QDRANT_API_KEY`: Your Qdrant Cloud API key
- `QDRANT_URL`: Your Qdrant Cloud cluster URL

### 3. Index Book Content

Run the indexing script to populate Qdrant with book content:

```bash
python scripts/index_chapters.py
```

This will:
- Recursively find all `.md` files in `my-website/docs/physical-ai/`
- Chunk the content using the configured chunker
- Generate embeddings using FastEmbed
- Upload to Qdrant Cloud

### 4. Start the API Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /health
```

### Global Chat (Full-Book Search)
```
POST /chat
Body: {
  "query": "What is ROS 2?",
  "conversation_id": "optional-session-id"
}
```

### Grounded Chat (Selected Text Mode)
```
POST /chat/grounded
Body: {
  "query": "Explain this concept",
  "selected_text": "ROS 2 is a middleware...",
  "source_chapter": "module-1-ros2/chapter-1-introduction",
  "conversation_id": "optional-session-id"
}
```

## Architecture

```
┌─────────────┐
│   FastAPI   │
│   Backend   │
└──────┬──────┘
       │
       ├─── FastEmbed (BAAI/bge-small-en-v1.5)
       │    └─── Generates 384-dim embeddings
       │
       ├─── Qdrant Cloud
       │    └─── Vector store for semantic search
       │
       └─── OpenAI GPT-4
            └─── Generates responses
```

## Configuration

All configuration is in `app/config.py`. Key settings:

- **Embedding Model**: `BAAI/bge-small-en-v1.5` (384 dimensions)
- **Chunk Size**: 512 tokens
- **Chunk Overlap**: 64 tokens
- **Top-K Results**: 5 chunks per query
- **Similarity Threshold**: 0.7

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

```
api/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── models/              # Pydantic models
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic
│   │   ├── embedder.py      # FastEmbed service
│   │   ├── qdrant_client.py # Qdrant client
│   │   ├── retriever.py     # Vector retrieval
│   │   └── llm.py           # OpenAI LLM service
│   └── utils/               # Utilities
│       └── chunking.py      # Text chunking
└── scripts/
    └── index_chapters.py    # Indexing script
```

## Troubleshooting

### Qdrant Connection Issues

- Verify `QDRANT_URL` and `QDRANT_API_KEY` are correct
- Check that your Qdrant Cloud cluster is active
- Ensure the collection exists (run indexing script)

### Embedding Issues

- FastEmbed will download the model on first use (may take time)
- Ensure you have internet connection for model download
- Check disk space for model cache

### Indexing Issues

- Verify `my-website/docs/physical-ai/` directory exists
- Check that markdown files are readable
- Review logs for specific file errors

## License

Part of the Physical AI & Humanoid Robotics textbook project.
-->
