# Data Model: UV-Based RAG Chatbot Backend

**Feature**: 006-uv-rag-backend
**Date**: 2025-11-30
**Status**: Phase 1 Design
**Purpose**: Define entities, relationships, validation rules, and state transitions

---

## Entity Definitions

### 1. Document

**Description**: Represents a single markdown file from the Physical AI textbook (`my-website/docs/physical-ai/`).

**Fields**:
| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `file_path` | `str` | ✅ | Relative path from `docs/physical-ai/` (e.g., `intro/01-what-is-physical-ai.md`) | Must be valid path, end with `.md` |
| `title` | `str` | ✅ | Document title (extracted from frontmatter `title` or derived from filename) | Non-empty, max 200 chars |
| `content` | `str` | ✅ | Full markdown text (excluding frontmatter) | Non-empty |
| `metadata` | `dict` | ❌ | Additional frontmatter fields (`description`, `sidebar_position`, etc.) | Valid YAML dict |

**Relationships**:
- One Document → Many Chunks (1:N)

**Validation Rules**:
```python
from pydantic import BaseModel, field_validator

class Document(BaseModel):
    file_path: str
    title: str
    content: str
    metadata: dict = {}

    @field_validator('file_path')
    def validate_file_path(cls, v):
        if not v.endswith('.md'):
            raise ValueError('file_path must end with .md')
        if '..' in v or v.startswith('/'):
            raise ValueError('file_path must be relative and not contain ..')
        return v

    @field_validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('title cannot be empty')
        if len(v) > 200:
            raise ValueError('title must be ≤200 characters')
        return v.strip()

    @field_validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('content cannot be empty')
        return v
```

---

### 2. Chunk

**Description**: A semantically coherent segment of a Document, generated during indexing with embeddings for vector search.

**Fields**:
| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `chunk_id` | `UUID` | ✅ | Unique identifier for this chunk | Valid UUID v4 |
| `source_document` | `str` | ✅ | Relative file path of parent Document | Same as Document.file_path |
| `chunk_index` | `int` | ✅ | 0-indexed position in document (chunk 0, 1, 2, ...) | ≥0 |
| `text` | `str` | ✅ | Chunk content (plain text, no markdown frontmatter) | Non-empty, max 4000 chars |
| `token_count` | `int` | ✅ | Number of tokens (tiktoken encoding) | Range [400, 1200] |
| `embedding` | `List[float]` | ✅ | 384-dimensional vector (from BAAI/bge-small-en-v1.5) | Length == 384 |
| `metadata` | `dict` | ❌ | Inherited from Document + chunk-specific (e.g., `title`, `chapter_module`) | Valid dict |

**Relationships**:
- Many Chunks → One Document (N:1)
- Stored in Qdrant as a Point with `id=chunk_id`, `vector=embedding`, `payload=metadata`

**Validation Rules**:
```python
from uuid import UUID
from pydantic import BaseModel, field_validator

class Chunk(BaseModel):
    chunk_id: UUID
    source_document: str
    chunk_index: int
    text: str
    token_count: int
    embedding: List[float]
    metadata: dict = {}

    @field_validator('chunk_index')
    def validate_chunk_index(cls, v):
        if v < 0:
            raise ValueError('chunk_index must be ≥0')
        return v

    @field_validator('token_count')
    def validate_token_count(cls, v):
        if not (400 <= v <= 1200):
            raise ValueError('token_count must be in range [400, 1200]')
        return v

    @field_validator('embedding')
    def validate_embedding(cls, v):
        if len(v) != 384:
            raise ValueError('embedding must have 384 dimensions')
        return v

    @field_validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('text cannot be empty')
        if len(v) > 4000:
            raise ValueError('text must be ≤4000 characters')
        return v.strip()
```

**Qdrant Storage Format**:
```python
{
    "id": "chunk_id",  # UUID as string
    "vector": [0.123, -0.456, ...],  # 384 floats
    "payload": {
        "source_document": "intro/01-what-is-physical-ai.md",
        "chunk_index": 0,
        "text": "Physical AI refers to...",
        "token_count": 512,
        "title": "What is Physical AI?",
        "chapter_module": "intro"
    }
}
```

---

### 3. Query

**Description**: A user question submitted to the chatbot, with optional selected text for grounded mode.

**Fields**:
| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `question` | `str` | ✅ | User's question | Non-empty, max 500 chars |
| `mode` | `Literal["global", "grounded"]` | ✅ | Query mode (global RAG or text selection grounding) | Must be "global" or "grounded" |
| `selected_text` | `Optional[str]` | ❌ | User-highlighted text (required for grounded mode) | Max 10,000 chars, required if mode="grounded" |
| `timestamp` | `datetime` | ✅ | Query submission time (ISO 8601) | Valid datetime |

**Validation Rules**:
```python
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, field_validator, model_validator

class Query(BaseModel):
    question: str
    mode: Literal["global", "grounded"]
    selected_text: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('question cannot be empty')
        if len(v) > 500:
            raise ValueError('question must be ≤500 characters')
        return v.strip()

    @field_validator('selected_text')
    def validate_selected_text(cls, v):
        if v and len(v) > 10000:
            raise ValueError('selected_text must be ≤10,000 characters')
        return v.strip() if v else None

    @model_validator(mode='after')
    def validate_grounded_mode(self):
        if self.mode == "grounded" and not self.selected_text:
            raise ValueError('selected_text is required when mode is "grounded"')
        return self
```

**API Request Example**:
```json
{
    "question": "What are the main differences between ROS2 nodes and services?",
    "mode": "global"
}
```

```json
{
    "question": "How does this apply to humanoid robots?",
    "mode": "grounded",
    "selected_text": "ROS2 services provide request-response communication..."
}
```

---

### 4. Response

**Description**: The LLM-generated answer to a Query, including retrieved sources and metadata.

**Fields**:
| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `answer` | `str` | ✅ | LLM-generated answer text | Non-empty |
| `sources` | `List[ChunkReference]` | ✅ | Retrieved chunks used as context (empty for grounded mode) | List of valid ChunkReference |
| `context_used` | `List[str]` | ✅ | Text snippets provided to LLM (sources or selected text) | Non-empty list |
| `latency` | `float` | ✅ | Query processing time in seconds | ≥0 |

**Sub-Entity: ChunkReference**:
| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `file_path` | `str` | Source document path | Same as Document.file_path |
| `chunk_index` | `int` | Chunk position in document | ≥0 |
| `similarity_score` | `float` | Cosine similarity score (0-1) | Range [0, 1] |

**Validation Rules**:
```python
from pydantic import BaseModel, field_validator

class ChunkReference(BaseModel):
    file_path: str
    chunk_index: int
    similarity_score: float

    @field_validator('similarity_score')
    def validate_similarity_score(cls, v):
        if not (0 <= v <= 1):
            raise ValueError('similarity_score must be in range [0, 1]')
        return v

class Response(BaseModel):
    answer: str
    sources: List[ChunkReference]
    context_used: List[str]
    latency: float

    @field_validator('answer')
    def validate_answer(cls, v):
        if not v.strip():
            raise ValueError('answer cannot be empty')
        return v.strip()

    @field_validator('latency')
    def validate_latency(cls, v):
        if v < 0:
            raise ValueError('latency must be ≥0')
        return v
```

**API Response Example**:
```json
{
    "answer": "ROS2 nodes are independent processes that communicate via topics (pub/sub), while services provide synchronous request-response communication. Nodes are used for continuous data streams (e.g., sensor data), whereas services handle one-time requests (e.g., triggering an action).",
    "sources": [
        {
            "file_path": "module-1-ros2/02-nodes-topics-services.md",
            "chunk_index": 1,
            "similarity_score": 0.89
        },
        {
            "file_path": "module-1-ros2/02-nodes-topics-services.md",
            "chunk_index": 3,
            "similarity_score": 0.82
        }
    ],
    "context_used": [
        "ROS2 nodes are independent processes...",
        "Services in ROS2 follow a request-response pattern..."
    ],
    "latency": 2.34
}
```

---

### 5. IndexingJob

**Description**: Represents a background indexing operation, tracking progress and status.

**Fields**:
| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `job_id` | `UUID` | ✅ | Unique identifier for this indexing job | Valid UUID v4 |
| `status` | `Literal["pending", "running", "completed", "failed"]` | ✅ | Current job status | Valid enum value |
| `files_processed` | `int` | ✅ | Count of markdown files processed | ≥0 |
| `chunks_created` | `int` | ✅ | Count of chunks generated and stored | ≥0 |
| `started_at` | `datetime` | ✅ | Job start time (ISO 8601) | Valid datetime |
| `completed_at` | `Optional[datetime]` | ❌ | Job completion time (null if still running/failed) | Valid datetime or null |
| `error` | `Optional[str]` | ❌ | Error message if status is "failed" | Max 1000 chars |

**State Transitions**:
```
pending → running → completed
                 ↘ failed
```

**Validation Rules**:
```python
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel, field_validator, model_validator

class IndexingJob(BaseModel):
    job_id: UUID
    status: Literal["pending", "running", "completed", "failed"]
    files_processed: int = 0
    chunks_created: int = 0
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    @field_validator('files_processed', 'chunks_created')
    def validate_counts(cls, v):
        if v < 0:
            raise ValueError('counts must be ≥0')
        return v

    @field_validator('error')
    def validate_error(cls, v):
        if v and len(v) > 1000:
            raise ValueError('error message must be ≤1000 characters')
        return v

    @model_validator(mode='after')
    def validate_completed_state(self):
        if self.status in ["completed", "failed"] and not self.completed_at:
            raise ValueError('completed_at must be set when status is completed or failed')
        if self.status == "failed" and not self.error:
            raise ValueError('error must be set when status is failed')
        return self
```

**API Response Example** (synchronous indexing):
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

## Entity Relationships Diagram

```
Document (1) ──────< (N) Chunk
                         │
                         │ stored in
                         ↓
                    Qdrant Collection
                         ↑
                         │ retrieved by
                         │
Query (global) ─────────┘
Query (grounded) ───> uses selected_text (no Qdrant retrieval)
                         │
                         ↓
                      Response

IndexingJob ───> creates Chunks → stores in Qdrant
```

---

## Storage Strategy

### Qdrant Collection
- **Collection Name**: `physical_ai_book`
- **Vector Config**: 384 dimensions, Cosine distance
- **Payload**: chunk metadata (source_document, chunk_index, text, token_count, title, chapter_module)
- **Indexing**: HNSW (M=16, ef_construct=100)

### File System
- **Markdown Files**: Read-only from `my-website/docs/physical-ai/` (not modified by backend)
- **Configuration**: `.env` file for secrets (OpenAI API key, Qdrant URL/key, content path)

### In-Memory State
- **IndexingJob**: Stored in-memory dict (MVP - no persistent storage)
- **Future**: Consider PostgreSQL/SQLite for job persistence if async indexing needed

---

## Validation Summary

| Entity | Key Validations |
|--------|-----------------|
| **Document** | file_path ends with `.md`, title non-empty (≤200 chars), content non-empty |
| **Chunk** | chunk_index ≥0, token_count in [400, 1200], embedding is 384-dim, text non-empty (≤4000 chars) |
| **Query** | question non-empty (≤500 chars), selected_text ≤10,000 chars if grounded mode |
| **Response** | answer non-empty, latency ≥0, similarity_score in [0, 1] |
| **IndexingJob** | counts ≥0, completed_at required if completed/failed, error required if failed |

---

**Data Model Status**: ✅ COMPLETE - Ready for contract generation
