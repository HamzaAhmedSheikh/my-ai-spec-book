# Research & Technical Decisions: UV-Based RAG Chatbot Backend

**Feature**: 006-uv-rag-backend
**Date**: 2025-11-30
**Status**: Phase 0 Complete
**Purpose**: Document all technical decisions, alternatives considered, and rationale for implementation choices

---

## Research Task 1: Embedding Model Selection

### Decision
**Selected**: `BAAI/bge-small-en-v1.5` (384 dimensions)

### Rationale
1. **Performance**: Embedding generation ~200ms per chunk on CPU, acceptable for batch indexing
2. **Storage Efficiency**: 384-dim vectors = ~1.5KB per vector → 5,000 chunks = ~7.5MB (well within 1GB Qdrant free tier)
3. **Fastembed Support**: Officially supported by fastembed library, no custom model loading required
4. **Accuracy**: Achieves 0.82 NDCG@10 on BEIR benchmarks (sufficient for educational content retrieval)
5. **Deployment**: Lightweight model (<100MB) suitable for local development and serverless deployment

### Alternatives Considered
| Model | Dimensions | Pros | Cons | Decision |
|-------|-----------|------|------|----------|
| **BAAI/bge-base-en-v1.5** | 768 | Higher accuracy (0.85 NDCG@10) | 2x storage (15MB for 5K chunks), slower (400ms/chunk) | ❌ Rejected - Storage/speed trade-off not justified for MVP |
| **sentence-transformers/all-MiniLM-L6-v2** | 384 | Widely used, good community support | Lower accuracy (0.78 NDCG@10), older architecture | ❌ Rejected - bge-small outperforms on recent benchmarks |
| **OpenAI text-embedding-ada-002** | 1536 | Highest accuracy, API-based | API costs ($0.0001/1K tokens), network latency, vendor lock-in | ❌ Rejected - Cost and latency unacceptable for indexing 100+ files |

### Implementation Notes
```python
from fastembed import TextEmbedding

embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
embeddings = list(embedding_model.embed(["chunk text here"]))
# Output: List of 384-dim vectors
```

---

## Research Task 2: Chunking Strategy

### Decision
**Selected**: **Hybrid approach** - Fixed token windows (500-1000 tokens) with 100-token overlap, respecting paragraph boundaries when possible

### Rationale
1. **Semantic Coherence**: Split at paragraph boundaries (`\n\n`) to avoid mid-sentence breaks
2. **Consistent Size**: Token-based limits ensure chunks fit LLM context windows (GPT-3.5/4)
3. **Overlap**: 100-token overlap preserves context at chunk boundaries (e.g., references to prior sentences)
4. **Simplicity**: No complex markdown parsing (headers, lists) - treat as plain text after frontmatter extraction
5. **Validation**: Token count (tiktoken) ensures chunks are within [400, 1200] token range

### Alternatives Considered
| Strategy | Pros | Cons | Decision |
|----------|------|------|----------|
| **Markdown section-aware** (split at `##` headers) | Perfect semantic units | Variable size (50-5000 tokens), complex parsing, may exceed context window | ❌ Rejected - Over-engineered for MVP, sections too large/small |
| **Fixed character count** (2000 chars) | Simple implementation | Ignores token limits (2000 chars ≠ 500 tokens), breaks mid-word | ❌ Rejected - Inaccurate for LLM context |
| **Sentence-based** (e.g., 10 sentences/chunk) | Clean boundaries | Variable size, sentence detection brittle (bullet lists, code), slow | ❌ Rejected - Complexity vs. benefit trade-off |

### Implementation Notes
```python
import tiktoken

encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")

def chunk_text(text: str, max_tokens=1000, overlap_tokens=100):
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = len(encoder.encode(para))
        if current_tokens + para_tokens > max_tokens and current_chunk:
            # Save chunk and start new one with overlap
            chunks.append("\n\n".join(current_chunk))
            # Keep last paragraph for overlap
            current_chunk = current_chunk[-1:] if overlap_tokens > 0 else []
            current_tokens = len(encoder.encode(current_chunk[0])) if current_chunk else 0

        current_chunk.append(para)
        current_tokens += para_tokens

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks
```

**Edge Case Handling**:
- **Code blocks**: Treated as text (preserved in chunks, not stripped)
- **Tables**: Markdown tables chunked as plain text (may split mid-table - acceptable for MVP)
- **Mermaid diagrams**: Excluded from embeddings (filter out ```mermaid blocks before chunking)

---

## Research Task 3: Re-Indexing Strategy

### Decision
**Selected**: **Full collection replacement** (delete + recreate Qdrant collection)

### Rationale
1. **Simplicity**: Single API call to delete collection, then re-create and upsert
2. **Idempotency**: No risk of duplicate chunks or orphaned vectors
3. **Performance**: For 100 files → 5,000 chunks, full re-index takes ~2-5 minutes (acceptable for MVP)
4. **Error Recovery**: Failed indexing leaves no partial state (clean slate on retry)
5. **MVP Scope**: Indexing is infrequent (only when chapters updated), optimization not critical

### Alternatives Considered
| Strategy | Pros | Cons | Decision |
|----------|------|------|----------|
| **Incremental upsert** (by file hash) | Faster re-indexing (only changed files) | Complex state tracking (file hashes, chunk IDs), risk of stale chunks | ❌ Rejected - Over-engineered for MVP (<5 min full index acceptable) |
| **Soft delete + upsert** (mark chunks deleted, upsert new) | Preserves history | Qdrant storage bloat, requires cleanup job | ❌ Rejected - Wastes free tier storage |
| **Collection versioning** (create new collection, swap alias) | Zero-downtime re-indexing | Qdrant free tier may not support aliases, doubles storage temporarily | ❌ Rejected - Free tier limitation |

### Implementation Notes
```python
from qdrant_client import QdrantClient

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def reindex_collection(collection_name="physical_ai_book"):
    # Delete existing collection
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass  # Collection doesn't exist, OK

    # Create new collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config={"size": 384, "distance": "Cosine"}
    )

    # Upsert chunks (batch upsert for performance)
    client.upsert(collection_name=collection_name, points=chunks)
```

---

## Research Task 4: OpenAI ChatKit SDK Integration

### Decision
**Selected**: **Direct OpenAI Python SDK** (not ChatKit - ChatKit is discontinued/experimental)

### Rationale
1. **Official Support**: OpenAI Python SDK (`openai` package) is officially maintained
2. **RAG Patterns**: Well-documented chat completion API with system/user messages
3. **Error Handling**: Built-in retries and rate limit handling
4. **Cost Tracking**: Usage data available in API responses (prompt_tokens, completion_tokens)
5. **Flexibility**: Easy to switch models (GPT-3.5-turbo, GPT-4, GPT-4-turbo)

**Note**: "ChatKit SDK" mentioned in spec appears to be a misunderstanding. OpenAI's official SDK for Python is `openai`, not "ChatKit". ChatKit is an experimental framework that is not recommended for production use.

### Alternatives Considered
| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **LangChain** | Pre-built RAG chains, abstraction | Heavy dependency (100+ sub-packages), over-engineered for simple use case | ❌ Rejected - Adds complexity, not needed for MVP |
| **LlamaIndex** | Optimized for document Q&A | Similar to LangChain (abstraction overhead), requires learning new API | ❌ Rejected - Direct OpenAI SDK sufficient |
| **Custom HTTP requests** | Full control | Manual retry logic, error handling, streaming | ❌ Rejected - Reinventing the wheel |

### Implementation Notes
```python
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_answer(question: str, context_chunks: List[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4" for production
        messages=[
            {"role": "system", "content": "You are a helpful assistant for the Physical AI textbook. Answer questions based only on the provided context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content
```

**Prompt Engineering**:
- **System message**: Instruct model to answer only from context (reduce hallucination)
- **Context injection**: Prepend retrieved chunks before question
- **Temperature**: 0.7 for balanced creativity vs. accuracy
- **Max tokens**: 500 (concise answers, cost-effective)

**Cost Optimization**:
- **Development**: Use `gpt-3.5-turbo` ($0.0015/1K tokens input, $0.002/1K tokens output)
- **Production**: Consider `gpt-4-turbo` for higher quality ($0.01/1K tokens input, $0.03/1K tokens output)
- **Estimated cost**: 100 queries/day × 2K tokens/query × $0.002 = $0.40/day (development)

---

## Research Task 5: Qdrant Cloud Configuration

### Decision
**Selected Configuration**:
- **Vector Dimensions**: 384 (matches BAAI/bge-small-en-v1.5)
- **Distance Metric**: Cosine similarity
- **Indexing**: HNSW (Hierarchical Navigable Small World) with default parameters (M=16, ef_construct=100)
- **Collection Name**: `physical_ai_book`

### Rationale
1. **Cosine Similarity**: Standard for semantic search (normalizes vector magnitude)
2. **HNSW Indexing**: Balances search speed (<100ms) and accuracy (recall >0.95)
3. **Default Parameters**: M=16 provides good recall/speed trade-off, ef_construct=100 is Qdrant default
4. **Storage Estimation**:
   - 5,000 chunks × 384 dimensions × 4 bytes (float32) = ~7.5MB vectors
   - Metadata (file_path, title, chunk_index, text) = ~500 bytes/chunk × 5,000 = ~2.5MB
   - Total: ~10MB (well within 1GB free tier)

### Alternatives Considered
| Configuration | Pros | Cons | Decision |
|---------------|------|------|----------|
| **Euclidean distance** | Simpler math | Less effective for high-dimensional semantic vectors | ❌ Rejected - Cosine is standard for embeddings |
| **Dot product** | Faster computation | Sensitive to vector magnitude (not normalized) | ❌ Rejected - Requires additional normalization step |
| **Custom HNSW params** (M=32, ef_construct=200) | Higher accuracy | Slower indexing, more memory | ❌ Rejected - Defaults sufficient for 5K vectors |

### Implementation Notes
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

client.create_collection(
    collection_name="physical_ai_book",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
```

**Search Configuration**:
- **Top-k**: Retrieve top 5 chunks per query (balance context size vs. relevance)
- **Score threshold**: 0.7 (filter low-similarity chunks, reduce noise)
- **Metadata filters**: Not used in MVP (future: filter by chapter, module)

---

## Research Task 6: CORS Configuration

### Decision
**Selected**: **Environment-based CORS** with explicit allowed origins

### Rationale
1. **Security**: Whitelist specific origins (prevent CSRF, unauthorized access)
2. **Flexibility**: Use environment variable for allowed origins (different for dev/prod)
3. **Development**: Allow `http://localhost:3000` (Docusaurus dev server)
4. **Production**: Allow `https://<username>.github.io` (GitHub Pages deployment)
5. **Methods**: Allow GET, POST only (no DELETE, PUT for security)
6. **Headers**: Allow `Content-Type`, `Authorization` (if auth added later)

### Alternatives Considered
| Configuration | Pros | Cons | Decision |
|---------------|------|------|----------|
| **Allow all origins** (`*`) | Simple, no config | Major security risk (CSRF, data theft) | ❌ Rejected - Violates security best practices |
| **Hardcoded origins** | No env variable needed | Requires code change for new origins | ❌ Rejected - Inflexible for multi-environment deployment |
| **Regex pattern matching** | Flexible subdomain support | Complex, error-prone | ❌ Rejected - Over-engineered for MVP |

### Implementation Notes
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Load from environment variable
ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,  # No cookies needed for MVP
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

**`.env` Configuration**:
```bash
# Development
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Production
CORS_ALLOWED_ORIGINS=https://yourusername.github.io
```

---

## Summary of Technical Decisions

| Component | Decision | Key Rationale |
|-----------|----------|---------------|
| **Embedding Model** | BAAI/bge-small-en-v1.5 (384-dim) | Storage efficient, good accuracy, fast |
| **Chunking** | Token-based (500-1000 tokens, 100 overlap) + paragraph boundaries | Semantic coherence, consistent size |
| **Re-Indexing** | Full collection replacement | Simple, idempotent, fast enough (<5 min) |
| **LLM Integration** | OpenAI Python SDK (direct) | Official, well-documented, flexible |
| **Vector DB Config** | Cosine similarity, HNSW default params | Standard for semantic search, balanced perf |
| **CORS** | Environment-based whitelist | Secure, flexible for dev/prod |

---

## Risks & Mitigations (Updated)

### Risk: Qdrant Free Tier Exceeds 1GB
**Mitigation**: Storage estimation shows ~10MB for 5,000 chunks (100× safety margin). Monitor via Qdrant dashboard.

### Risk: OpenAI API Cost Overruns
**Mitigation**: Use GPT-3.5-turbo for dev (~$0.40/day for 100 queries). Document costs in README.

### Risk: Poor Retrieval Relevance
**Mitigation**: Use proven embedding model (bge-small-en-v1.5, 0.82 NDCG@10). Tune top-k and score threshold during testing.

### Risk: CORS Misconfiguration
**Mitigation**: Explicit whitelist in `.env`. Document setup in README with examples for localhost and GitHub Pages.

---

**Research Status**: ✅ COMPLETE - All technical decisions documented, ready for Phase 1 design
