# Physical AI RAG Chatbot - API Documentation

**Version**: 1.0.0
**Base URL**: `http://localhost:8000` (development) | `https://api.your-domain.com` (production)

---

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Global Chat](#global-chat)
  - [Grounded Chat](#grounded-chat)
  - [Content Indexing](#content-indexing)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

---

## Overview

The Physical AI RAG Chatbot API provides intelligent question-answering capabilities over the Physical AI textbook corpus using Retrieval-Augmented Generation (RAG). The API supports two query modes:

1. **Global Mode** (`/chat`): Questions answered using vector search across the entire book
2. **Grounded Mode** (`/chat/grounded`): Questions answered using only user-selected text ("Magna Carta" feature)

### Key Features

- 📚 **42-chapter coverage**: Complete Physical AI textbook indexed
- 🔍 **Semantic search**: Qdrant vector database with fastembed embeddings
- 🤖 **LLM-powered**: OpenAI GPT for answer generation
- ⚡ **Low latency**: p95 < 3s for global chat, < 2s for grounded chat
- 🔒 **Production-ready**: CORS support, health checks, error handling

---

## Authentication

**Current version**: No authentication required (development)

**Future versions**: Will support API key authentication via `Authorization: Bearer <token>` header.

---

## Endpoints

### Health Check

**GET** `/health`

Check service availability and Qdrant connectivity.

#### Response 200 (Healthy)

```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "timestamp": "2025-12-01T10:00:00Z"
}
```

#### Response 200 (Degraded)

```json
{
  "status": "degraded",
  "qdrant_connected": false,
  "timestamp": "2025-12-01T10:00:00Z"
}
```

#### Example Request

```bash
curl -X GET http://localhost:8000/health
```

---

### Global Chat

**POST** `/chat`

Ask a question about the Physical AI book. The system retrieves relevant chunks from the vector database and generates an answer using the LLM.

#### Request Body

| Field      | Type   | Required | Constraints      | Description                  |
| ---------- | ------ | -------- | ---------------- | ---------------------------- |
| `question` | string | Yes      | 1-500 characters | User's question about the book |

#### Request Example

```json
{
  "question": "What is Physical AI?"
}
```

#### Response 200 (Success)

```json
{
  "answer": "Physical AI refers to artificial intelligence systems that interact with the physical world through sensors, actuators, and robotic embodiment. It combines perception, reasoning, and action to enable intelligent behavior in real-world environments.",
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
    "Physical AI is the intersection of artificial intelligence...",
    "Embodied intelligence emphasizes the importance..."
  ],
  "latency": 2.34
}
```

#### Response Schema

| Field          | Type     | Description                              |
| -------------- | -------- | ---------------------------------------- |
| `answer`       | string   | LLM-generated answer                     |
| `sources`      | array    | Retrieved chunks (see ChunkReference)    |
| `context_used` | string[] | Text snippets provided to LLM as context |
| `latency`      | float    | Query processing time in seconds         |

#### ChunkReference Schema

| Field              | Type   | Description                         |
| ------------------ | ------ | ----------------------------------- |
| `file_path`        | string | Relative path to source markdown    |
| `chunk_index`      | int    | Chunk position in document (0-indexed) |
| `similarity_score` | float  | Cosine similarity (0-1)             |

#### Error Responses

- **400 Bad Request**: Empty or invalid question
- **500 Internal Server Error**: LLM failure, unexpected error
- **503 Service Unavailable**: Qdrant disconnected, OpenAI API down

#### Example Requests

```bash
# Basic question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Physical AI?"}'

# Technical question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main differences between ROS2 nodes and services?"}'
```

---

### Grounded Chat

**POST** `/chat/grounded`

Ask a question about user-selected text. The "Magna Carta" feature enables focused Q&A on specific passages without vector search.

#### Request Body

| Field           | Type   | Required | Constraints         | Description                       |
| --------------- | ------ | -------- | ------------------- | --------------------------------- |
| `question`      | string | Yes      | 1-500 characters    | User's question about the text    |
| `selected_text` | string | Yes      | 1-10,000 characters | User-highlighted text snippet     |

#### Request Example

```json
{
  "question": "How does this apply to humanoid robots?",
  "selected_text": "ROS2 services provide request-response communication patterns. Unlike topics (pub/sub), services are synchronous and return a response. This is useful for triggering actions like 'grasp object' or 'move to position'."
}
```

#### Response 200 (Success)

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

#### Key Differences from Global Chat

- **No vector search**: Uses only `selected_text` as context
- **Empty sources**: `sources` array is always `[]`
- **Faster latency**: No database retrieval (< 2s typical)

#### Error Responses

- **400 Bad Request**: Missing `selected_text`, text too long (> 10,000 chars)
- **422 Unprocessable Entity**: Invalid request format
- **500 Internal Server Error**: LLM failure

#### Example Request

```bash
curl -X POST http://localhost:8000/chat/grounded \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does this apply to humanoid robots?",
    "selected_text": "ROS2 services provide request-response communication patterns. Unlike topics (pub/sub), services are synchronous and return a response."
  }'
```

---

### Content Indexing

**POST** `/index`

Index or re-index book content. Discovers all markdown files in `docs/physical-ai/`, chunks content, generates embeddings, and stores in Qdrant.

**⚠️ Note**: This endpoint runs **synchronously** and may take 2-5 minutes for 100+ files.

#### Request Body (Optional)

| Field           | Type    | Required | Default | Description                          |
| --------------- | ------- | -------- | ------- | ------------------------------------ |
| `force_reindex` | boolean | No       | `false` | Force re-index even if collection exists |

#### Request Example

```json
{
  "force_reindex": true
}
```

#### Response 200 (Success)

```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "files_processed": 105,
  "chunks_created": 5234,
  "started_at": "2025-12-01T10:00:00Z",
  "completed_at": "2025-12-01T10:04:32Z",
  "error": null
}
```

#### Response Schema

| Field             | Type     | Description                            |
| ----------------- | -------- | -------------------------------------- |
| `job_id`          | string   | Unique job identifier (UUID)           |
| `status`          | string   | `pending`, `running`, `completed`, `failed` |
| `files_processed` | int      | Number of markdown files processed     |
| `chunks_created`  | int      | Number of chunks stored in Qdrant      |
| `started_at`      | datetime | Job start timestamp (ISO 8601)         |
| `completed_at`    | datetime | Job completion timestamp (nullable)    |
| `error`           | string   | Error message if `status` is `failed`  |

#### Error Responses

- **409 Conflict**: Indexing already in progress
- **500 Internal Server Error**: File read error, Qdrant error, embedding failure

#### Example Requests

```bash
# Default indexing (empty body)
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{}'

# Force re-index
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"force_reindex": true}'
```

---

## Error Handling

### Standard Error Response

All error responses follow this schema:

```json
{
  "error": "Descriptive error message"
}
```

### HTTP Status Codes

| Code | Meaning                | When It Occurs                          |
| ---- | ---------------------- | --------------------------------------- |
| 200  | OK                     | Request succeeded                       |
| 400  | Bad Request            | Invalid input (empty question, etc.)    |
| 409  | Conflict               | Resource conflict (indexing in progress) |
| 422  | Unprocessable Entity   | Validation error (Pydantic)             |
| 500  | Internal Server Error  | Unexpected server error                 |
| 503  | Service Unavailable    | External service down (Qdrant, OpenAI)  |

### Common Error Messages

```json
// Empty question
{"error": "question cannot be empty"}

// Question too long
{"error": "question must be ≤500 characters"}

// Missing selected text (grounded mode)
{"error": "selected_text is required for grounded mode"}

// Selected text too long
{"error": "selected_text must be ≤10,000 characters"}

// Qdrant unavailable
{"error": "Vector database unavailable"}

// Indexing conflict
{"error": "Indexing already in progress"}
```

---

## Rate Limiting

**Current version**: No rate limiting (development)

**Future versions**:
- 100 requests/minute per IP
- Response header: `X-RateLimit-Remaining: 95`

---

## Examples

### Complete Workflow Example

```bash
# 1. Check service health
curl -X GET http://localhost:8000/health

# 2. Index book content (first-time setup)
curl -X POST http://localhost:8000/index

# 3. Ask a global question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Physical AI?"}'

# 4. Ask a grounded question
curl -X POST http://localhost:8000/chat/grounded \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain this concept",
    "selected_text": "Physical AI combines artificial intelligence with physical systems..."
  }'
```

### Python SDK Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Global chat
response = requests.post(
    f"{BASE_URL}/chat",
    json={"question": "What is Physical AI?"}
)
data = response.json()
print(f"Answer: {data['answer']}")
print(f"Sources: {len(data['sources'])} chunks")
print(f"Latency: {data['latency']:.2f}s")

# Grounded chat
response = requests.post(
    f"{BASE_URL}/chat/grounded",
    json={
        "question": "What does this mean?",
        "selected_text": "ROS2 provides communication protocols..."
    }
)
data = response.json()
print(f"Answer: {data['answer']}")
```

### JavaScript/TypeScript Example

```typescript
const BASE_URL = "http://localhost:8000";

// Global chat
async function askQuestion(question: string) {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  const data = await response.json();
  return data;
}

// Grounded chat
async function askGroundedQuestion(question: string, selectedText: string) {
  const response = await fetch(`${BASE_URL}/chat/grounded`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, selected_text: selectedText }),
  });
  const data = await response.json();
  return data;
}

// Usage
const result = await askQuestion("What is Physical AI?");
console.log(result.answer);
```

---

## OpenAPI Specification

Full OpenAPI 3.0.3 specifications are available in:
- `specs/006-uv-rag-backend/contracts/health.yaml`
- `specs/006-uv-rag-backend/contracts/chat.yaml`
- `specs/006-uv-rag-backend/contracts/grounded.yaml`
- `specs/006-uv-rag-backend/contracts/index.yaml`

---

## Support

For issues, questions, or feature requests:
- **Repository**: [GitHub Repository URL]
- **Documentation**: `backend/README.md`
- **Quickstart**: `specs/006-uv-rag-backend/quickstart.md`

---

**Last Updated**: 2025-12-01
**API Version**: 1.0.0
