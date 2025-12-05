# Quickstart Guide: UV-Based RAG Chatbot Backend

**Feature**: 006-uv-rag-backend
**Date**: 2025-11-30
**Purpose**: Integration scenarios and step-by-step setup instructions

---

## Prerequisites

- **Python**: 3.11 or higher ([python.org](https://python.org))
- **UV Package Manager**: Install with `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Qdrant Cloud Account**: Free tier at [cloud.qdrant.io](https://cloud.qdrant.io)
- **OpenAI API Key**: From [platform.openai.com](https://platform.openai.com)
- **Docusaurus Book Content**: Physical AI book must exist at `my-website/docs/physical-ai/`

---

## Scenario 1: Local Development Setup

### Step 1: Clone Repository and Navigate to Backend
```bash
cd F:/my-ai-book/my-ai-spec-book
# Backend directory will be created during implementation
cd backend
```

### Step 2: Initialize UV Project (if not already done)
```bash
uv init
# Creates pyproject.toml and uv.lock
```

### Step 3: Install Dependencies
```bash
uv sync
# Installs FastAPI, uvicorn, fastembed, qdrant-client, openai, etc.
```

### Step 4: Configure Environment Variables
Create a `.env` file in the `backend/` directory:

```bash
# .env
OPENAI_API_KEY=sk-your-openai-api-key-here
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key-here
BOOK_CONTENT_PATH=../my-website/docs/physical-ai
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Security Note**: Never commit `.env` to git. Use `.env.example` as a template.

### Step 5: Run the Backend Server
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 6: Verify Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "timestamp": "2025-11-30T10:00:00Z"
}
```

If `qdrant_connected: false`, check your Qdrant URL and API key in `.env`.

---

## Scenario 2: First-Time Indexing

### Step 1: Trigger Indexing Endpoint
```bash
curl -X POST http://localhost:8000/index
```

### Step 2: Wait for Completion
Indexing runs synchronously. For ~100 files, expect 2-5 minutes. Monitor terminal logs:

```
INFO:     Indexing started: job_id=a1b2c3d4...
INFO:     Discovered 105 markdown files
INFO:     Processing intro/01-what-is-physical-ai.md...
INFO:     Chunking: 3 chunks created
INFO:     Generating embeddings...
INFO:     Upserting to Qdrant...
...
INFO:     Indexing completed: 105 files, 5234 chunks
```

### Step 3: Verify Qdrant Collection
Check Qdrant dashboard or query via API:

```bash
curl -X GET "https://your-cluster.qdrant.io:6333/collections/physical_ai_book" \
  -H "api-key: your-qdrant-api-key"
```

Expected response:
```json
{
  "result": {
    "status": "green",
    "vectors_count": 5234,
    "points_count": 5234,
    ...
  }
}
```

### Step 4: Expected Response from `/index` Endpoint
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "files_processed": 105,
  "chunks_created": 5234,
  "started_at": "2025-11-30T10:00:00Z",
  "completed_at": "2025-11-30T10:04:32Z",
  "error": null
}
```

---

## Scenario 3: Global Chat Query

### Step 1: Ask a Question About the Book
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Physical AI?"}'
```

### Step 2: Inspect Response
```json
{
  "answer": "Physical AI refers to artificial intelligence systems that interact with the physical world through sensors, actuators, and robotic embodiment. It combines machine learning with robotics to enable autonomous agents that perceive, reason about, and manipulate their environment.",
  "sources": [
    {
      "file_path": "intro/01-what-is-physical-ai.md",
      "chunk_index": 0,
      "similarity_score": 0.92
    },
    {
      "file_path": "intro/02-embodied-intelligence.md",
      "chunk_index": 1,
      "similarity_score": 0.85
    }
  ],
  "context_used": [
    "Physical AI is the intersection of artificial intelligence and robotics...",
    "Embodied intelligence emphasizes the importance of physical interaction..."
  ],
  "latency": 2.34
}
```

### Step 3: Verify Retrieved Sources
- **sources** array shows which chunks were retrieved from Qdrant
- **similarity_score** indicates relevance (higher = more similar to query)
- **context_used** shows the actual text snippets provided to the LLM

---

## Scenario 4: Grounded Chat Query (Text Selection)

### Step 1: Simulate User Text Selection
User highlights this paragraph from a chapter:

> "ROS2 services provide request-response communication patterns. Unlike topics (pub/sub), services are synchronous and return a response. This is useful for triggering actions like 'grasp object' or 'move to position'."

### Step 2: Ask a Question About the Selection
```bash
curl -X POST http://localhost:8000/chat/grounded \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does this apply to humanoid robots?",
    "selected_text": "ROS2 services provide request-response communication patterns. Unlike topics (pub/sub), services are synchronous and return a response. This is useful for triggering actions like '\''grasp object'\'' or '\''move to position'\''."
  }'
```

### Step 3: Verify Response is Constrained to Selection
```json
{
  "answer": "In the context of humanoid robots, ROS2 services can trigger actions like grasping objects (hand control) or moving to specific positions (locomotion). The synchronous nature ensures the robot waits for action completion before proceeding, which is critical for sequential tasks.",
  "sources": [],
  "context_used": [
    "ROS2 services provide request-response communication patterns..."
  ],
  "latency": 1.89
}
```

**Key Observations**:
- **sources** is empty (no Qdrant retrieval)
- **context_used** contains only the selected_text
- Answer stays within the scope of the selection (no information from other chapters)

---

## Scenario 5: Docusaurus Integration

### Step 1: Create React Chatbot Widget

In `my-website/src/components/ChatWidget.tsx`:

```tsx
import React, { useState } from 'react';

const API_URL = 'http://localhost:8000';  // Change to production URL for deployment

export default function ChatWidget() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    setLoading(true);
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await response.json();
    setAnswer(data.answer);
    setLoading(false);
  };

  return (
    <div className="chat-widget">
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question about Physical AI..."
      />
      <button onClick={askQuestion} disabled={loading}>
        {loading ? 'Loading...' : 'Ask'}
      </button>
      {answer && <div className="answer">{answer}</div>}
    </div>
  );
}
```

### Step 2: Embed Widget in Docusaurus Page

In `my-website/docs/intro.md` (or any MDX page):

```mdx
import ChatWidget from '@site/src/components/ChatWidget';

# Introduction to Physical AI

Welcome to the Physical AI textbook!

<ChatWidget />

## What is Physical AI?
...
```

### Step 3: Configure CORS for Production

Update `.env` for production deployment:

```bash
CORS_ALLOWED_ORIGINS=https://yourusername.github.io
```

Restart backend server.

### Step 4: Deploy Backend to Render/Railway

**Render.com Deployment**:
1. Create new Web Service
2. Connect GitHub repository (select `backend/` directory as root)
3. Set build command: `uv sync`
4. Set start command: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables: `OPENAI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `BOOK_CONTENT_PATH`, `CORS_ALLOWED_ORIGINS`
6. Deploy

**Railway.app Deployment**:
1. New Project → Deploy from GitHub
2. Select `backend/` as root directory
3. Railway auto-detects Python and runs `uvicorn`
4. Add environment variables in settings
5. Deploy

### Step 5: Update Frontend API URL

In `ChatWidget.tsx`, change:
```tsx
const API_URL = 'https://your-backend.onrender.com';  // Production URL
```

Rebuild Docusaurus and deploy to GitHub Pages.

---

## Scenario 6: Testing with Curl Scripts

### Global Chat Test Script
```bash
#!/bin/bash
# test-chat.sh

API_URL="http://localhost:8000"

echo "Testing global chat..."
curl -X POST ${API_URL}/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is ROS2?"}' | jq .

echo -e "\nTesting grounded chat..."
curl -X POST ${API_URL}/chat/grounded \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain this in simple terms",
    "selected_text": "URDF (Unified Robot Description Format) is an XML specification for representing robot models."
  }' | jq .

echo -e "\nTesting health check..."
curl ${API_URL}/health | jq .
```

Run with:
```bash
chmod +x test-chat.sh
./test-chat.sh
```

---

## Troubleshooting

### Issue: `qdrant_connected: false` in Health Check
**Solution**:
- Verify Qdrant URL and API key in `.env`
- Check network connectivity to Qdrant Cloud
- Ensure Qdrant cluster is active (not paused)

### Issue: Indexing Fails with "File not found"
**Solution**:
- Verify `BOOK_CONTENT_PATH` in `.env` points to correct directory
- Check that `my-website/docs/physical-ai/` exists and contains `.md` files
- Use absolute path if relative path fails: `BOOK_CONTENT_PATH=/full/path/to/my-website/docs/physical-ai`

### Issue: CORS Error in Frontend
**Solution**:
- Ensure `CORS_ALLOWED_ORIGINS` includes frontend URL (e.g., `http://localhost:3000`)
- Check browser console for exact error
- For production, add GitHub Pages URL: `https://yourusername.github.io`

### Issue: Chat Returns Empty Answer
**Solution**:
- Check if indexing completed successfully (re-run `/index`)
- Verify Qdrant collection has vectors: `curl https://your-cluster.qdrant.io:6333/collections/physical_ai_book -H "api-key: YOUR_KEY"`
- Inspect retrieved `sources` in response (should have similarity_score > 0.7)

### Issue: OpenAI API Rate Limit
**Solution**:
- Wait 60 seconds and retry
- Consider upgrading OpenAI plan for higher rate limits
- Use GPT-3.5-turbo for development (lower cost, higher limits)

---

## Next Steps

1. **Run Tests**: `pytest` in `backend/` directory
2. **Generate API Docs**: Visit `http://localhost:8000/docs` (Swagger UI)
3. **Monitor Logs**: Check uvicorn logs for errors
4. **Optimize Performance**: Tune chunk size, top-k, LLM temperature based on user feedback
5. **Add Features**: Implement authentication, caching, or advanced chunking strategies

---

**Quickstart Status**: ✅ COMPLETE - All integration scenarios documented
