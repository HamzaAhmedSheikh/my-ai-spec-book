# Implementation Plan: UV-Based RAG Chatbot Backend

**Branch**: `006-uv-rag-backend` | **Date**: 2025-11-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-uv-rag-backend/spec.md`

## Summary

Build a Python-based RAG (Retrieval-Augmented Generation) chatbot backend using `uv` package manager, FastAPI, and Qdrant vector database. The system will index the Physical AI textbook content (42 chapters, ~100+ markdown files in `my-website/docs/physical-ai/`), chunk documents into semantically coherent segments, generate embeddings using fastembed, and provide two query modes: (1) global question answering across the entire book, and (2) grounded question answering constrained to user-selected text passages. The backend exposes RESTful API endpoints for indexing, health checks, and chat interactions, designed for integration with a Docusaurus-based frontend.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.104+, uvicorn 0.24+, fastembed 0.2+, qdrant-client 1.7+, openai 1.3+, python-frontmatter 1.0+, tiktoken 0.5+, pydantic 2.5+
**Storage**: Qdrant Cloud Free Tier (vector database, 1GB limit), Environment variables (.env file for configuration)
**Testing**: pytest 7.4+, httpx 0.25+ (async client for FastAPI testing), pytest-asyncio 0.21+
**Target Platform**: Linux/Windows server (development: local, production: Render/Railway)
**Project Type**: Backend API (web application - Option 2 from template)
**Performance Goals**: p95 latency <3s for `/chat`, <2s for `/chat/grounded`, <500ms for `/health`, indexing throughput >10 files/min
**Constraints**: Qdrant storage <1GB for full corpus (~200k-300k tokens), OpenAI API cost-effective (use GPT-3.5-turbo for dev, GPT-4 for prod), 100 concurrent requests supported
**Scale/Scope**: ~100+ markdown files, ~42 chapters, estimated 5,000-10,000 chunks after segmentation, <100 concurrent users (demo/development use)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase-Driven Architecture ✅ PASS
- **Requirement**: Complete Phase 1 (Book) before Phase 2 (RAG)
- **Status**: This feature IS Phase 2 - assumes Phase 1 (Docusaurus book with `docs/physical-ai/` content) is complete
- **Verification**: Backend will fail gracefully if `docs/physical-ai/` directory is not accessible

### Spec-Driven Development ✅ PASS
- **Requirement**: Feature starts with spec → plan → tasks → code
- **Status**: Spec completed (`specs/006-uv-rag-backend/spec.md`), plan in progress
- **Artifacts**: Spec includes acceptance criteria, user stories, functional requirements

### Quality-First (Testing) ✅ PASS
- **Requirement**: All code must be runnable and tested
- **Status**: Plan includes pytest test structure for unit, integration, and contract tests
- **Coverage**: Tests for chunking logic, embedding generation, API endpoints, Qdrant integration
- **Gates**: CI/CD runs `pytest` + linting (`black`, `pylint`) before merge

### Security (Non-Negotiable) ✅ PASS
- **Requirement**: Secrets must never appear in code
- **Status**: All API keys (OpenAI, Qdrant) stored in `.env` file (gitignored)
- **Configuration**: `.env.example` provided with placeholder values
- **Documentation**: README includes security setup instructions

### Simplicity Over Perfection ✅ PASS
- **Requirement**: Start with MVP, no premature optimization
- **Status**: MVP focuses on three core endpoints (`/health`, `/chat`, `/chat/grounded`, `/index`)
- **Scope**: Out-of-scope items clearly defined (auth, rate limiting, caching, multi-language)
- **Iteration**: Advanced features (semantic chunking, A/B testing) deferred to future iterations

**Overall Assessment**: ✅ ALL GATES PASSED - Proceed to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/006-uv-rag-backend/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (entity definitions)
├── quickstart.md        # Phase 1 output (integration scenarios)
├── contracts/           # Phase 1 output (API contracts)
│   ├── health.yaml      # GET /health OpenAPI spec
│   ├── chat.yaml        # POST /chat OpenAPI spec
│   ├── grounded.yaml    # POST /chat/grounded OpenAPI spec
│   └── index.yaml       # POST /index OpenAPI spec
└── checklists/
    └── requirements.md  # Spec quality validation (completed)
```

### Source Code (repository root)

```text
backend/                 # UV-initialized Python project
├── pyproject.toml       # UV project configuration
├── uv.lock              # UV dependency lock file
├── .env.example         # Environment variable template
├── .env                 # Actual secrets (gitignored)
├── README.md            # Setup and deployment instructions
├── app/                 # FastAPI application package
│   ├── __init__.py
│   ├── main.py          # FastAPI app entry point, CORS, lifespan events
│   ├── config.py        # Environment configuration (Pydantic Settings)
│   ├── routes.py        # API route definitions (/health, /chat, /chat/grounded, /index)
│   ├── models.py        # Pydantic request/response models
│   ├── rag.py           # RAG orchestration (query → retrieve → generate)
│   ├── embeddings.py    # Embedding generation (fastembed wrapper)
│   ├── chunking.py      # Markdown chunking logic (token-based with overlap)
│   ├── indexing.py      # File discovery, frontmatter parsing, Qdrant upsert
│   ├── qdrant_client.py # Qdrant connection and collection management
│   └── llm.py           # OpenAI ChatCompletion wrapper (ChatKit SDK)
└── tests/               # Pytest test suite
    ├── __init__.py
    ├── conftest.py      # Shared fixtures (test client, mock Qdrant, temp files)
    ├── unit/            # Unit tests (pure functions)
    │   ├── test_chunking.py
    │   ├── test_embeddings.py
    │   └── test_frontmatter.py
    ├── integration/     # Integration tests (Qdrant, OpenAI mocked/stubbed)
    │   ├── test_indexing.py
    │   ├── test_rag.py
    │   └── test_qdrant.py
    └── contract/        # API contract tests (FastAPI TestClient)
        ├── test_health.py
        ├── test_chat.py
        ├── test_grounded.py
        └── test_index.py

my-website/              # Docusaurus book (assumed to exist from Phase 1)
└── docs/
    └── physical-ai/     # Target markdown content
        ├── intro/
        ├── module-1-ros2/
        ├── module-2-gazebo/
        ├── module-3-isaac/
        ├── module-4-vla/
        ├── hardware/
        ├── capstone/
        └── glossary/
```

**Structure Decision**: Selected **Option 2: Web application** because the feature is explicitly a backend API designed to integrate with a Docusaurus frontend. The `backend/` directory contains the Python FastAPI application, while `my-website/` (existing from Phase 1) contains the Docusaurus book content. This separation aligns with the constitution's Phase-Driven Architecture (Phase 1: Book, Phase 2: Backend).

## Complexity Tracking

> **Not applicable** - No constitution violations detected. All gates passed.

---

## Phase 0: Research & Technical Decisions

**Status**: To be completed during `/sp.plan` execution

The following research tasks resolve unknowns from Technical Context and Open Questions from spec.md:

### Research Task 1: Embedding Model Selection
**Question**: BAAI/bge-small-en-v1.5 (lightweight, fast) vs. BAAI/bge-base-en-v1.5 (better accuracy)?

**To Investigate**:
- Performance benchmarks (embedding generation time, retrieval precision)
- Model size and memory footprint
- Fastembed library support and compatibility
- Trade-offs for educational content (Physical AI textbook domain)

### Research Task 2: Chunking Strategy
**Question**: Fixed token windows with overlap vs. markdown section-aware chunking?

**To Investigate**:
- Token counting library (tiktoken for OpenAI models)
- Markdown parsing libraries (python-frontmatter, markdown-it-py)
- Chunking algorithms preserving semantic coherence
- Impact on retrieval relevance (paragraph boundaries vs. arbitrary splits)

### Research Task 3: Re-Indexing Strategy
**Question**: Full Qdrant collection replacement vs. incremental upsert?

**To Investigate**:
- Qdrant collection management (delete + recreate vs. upsert by document ID)
- Idempotency guarantees (preventing duplicate chunks)
- Performance implications (indexing time for 100+ files)
- Error recovery strategies (partial indexing failures)

### Research Task 4: OpenAI ChatKit SDK Integration
**Question**: Best practices for OpenAI API integration in RAG pipelines?

**To Investigate**:
- ChatKit SDK vs. direct OpenAI Python SDK
- Prompt engineering for RAG (system messages, context injection)
- Rate limiting and error handling (retries, exponential backoff)
- Cost optimization (GPT-3.5-turbo vs. GPT-4, token usage tracking)

### Research Task 5: Qdrant Cloud Configuration
**Question**: Optimal Qdrant collection settings for 200k-300k token corpus?

**To Investigate**:
- Vector dimensions (fastembed model output size)
- Distance metric (Cosine vs. Euclidean for semantic search)
- HNSW indexing parameters (M, ef_construct for sub-100ms search)
- Storage estimation (chunk count → vector storage → free tier limits)

### Research Task 6: CORS Configuration
**Question**: Secure CORS settings for Docusaurus frontend integration?

**To Investigate**:
- Allowed origins (localhost for dev, GitHub Pages URL for prod)
- Allowed methods (GET, POST) and headers (Content-Type, Authorization if needed)
- Credentials handling (cookies, if applicable)
- Security best practices (prevent CORS misconfigurations)

**Output**: `research.md` documenting all decisions with rationale and alternatives considered.

---

## Phase 1: Design & Contracts

**Status**: To be completed after Phase 0

### Phase 1a: Data Model (`data-model.md`)

Extract entities from spec.md Key Entities section:

1. **Document**
   - Fields: file_path (str), title (str), content (str), metadata (dict)
   - Validation: file_path must be valid relative path, title non-empty
   - Relationships: One Document → Many Chunks

2. **Chunk**
   - Fields: chunk_id (UUID), source_document (str), chunk_index (int), text (str), token_count (int), embedding (List[float]), metadata (dict)
   - Validation: token_count in range [400, 1200], chunk_index >= 0
   - Relationships: Many Chunks → One Document

3. **Query**
   - Fields: question (str), mode (enum: "global" | "grounded"), selected_text (Optional[str]), timestamp (datetime)
   - Validation: question non-empty and max 500 chars, selected_text max 10,000 chars

4. **Response**
   - Fields: answer (str), sources (List[ChunkReference]), context_used (List[str]), latency (float)
   - ChunkReference: file_path (str), chunk_index (int), similarity_score (float)

5. **IndexingJob**
   - Fields: job_id (UUID), status (enum: "pending" | "running" | "completed" | "failed"), files_processed (int), chunks_created (int), started_at (datetime), completed_at (Optional[datetime]), error (Optional[str])
   - State Transitions: pending → running → (completed | failed)

### Phase 1b: API Contracts (`contracts/`)

Generate OpenAPI 3.0 YAML specs for each endpoint:

**`contracts/health.yaml`**:
```yaml
GET /health
Response 200:
  status: "healthy" | "degraded"
  qdrant_connected: bool
  timestamp: ISO 8601 datetime
```

**`contracts/chat.yaml`**:
```yaml
POST /chat
Request:
  question: string (required, 1-500 chars)
Response 200:
  answer: string
  sources: array of {file_path, chunk_index, similarity_score}
  context_used: array of strings
  latency: float
Response 400: {error: "Invalid request"}
Response 500: {error: "Internal server error"}
Response 503: {error: "Service unavailable"}
```

**`contracts/grounded.yaml`**:
```yaml
POST /chat/grounded
Request:
  question: string (required, 1-500 chars)
  selected_text: string (required, 1-10,000 chars)
Response 200: (same as /chat)
Response 400: {error: "Invalid request"}
```

**`contracts/index.yaml`**:
```yaml
POST /index
Request: (empty or optional: {force_reindex: bool})
Response 202:
  job_id: UUID
  status: "pending"
Response 200 (if synchronous):
  job_id: UUID
  status: "completed"
  files_processed: int
  chunks_created: int
Response 409: {error: "Indexing already in progress"}
```

### Phase 1c: Quickstart (`quickstart.md`)

Document integration scenarios:

1. **Local Development Setup**
   - Install UV, Python 3.11+
   - Clone repo, run `uv sync` in `backend/`
   - Configure `.env` (OpenAI API key, Qdrant URL/key, book content path)
   - Run `uvicorn app.main:app --reload`

2. **First-Time Indexing**
   - `curl -X POST http://localhost:8000/index`
   - Wait for completion (~2-5 minutes for 100 files)
   - Verify Qdrant collection created

3. **Global Chat Query**
   - `curl -X POST http://localhost:8000/chat -d '{"question": "What is Physical AI?"}'`
   - Inspect `sources` array for retrieved chunks

4. **Grounded Chat Query**
   - `curl -X POST http://localhost:8000/chat/grounded -d '{"question": "Explain this", "selected_text": "..."}'`
   - Verify response stays within selected text context

5. **Docusaurus Integration**
   - Add React chatbot widget to Docusaurus `src/components/`
   - Configure CORS allowed origin (GitHub Pages URL)
   - Deploy backend to Render/Railway, update frontend API URL

### Phase 1d: Agent Context Update

Run `.specify/scripts/bash/update-agent-context.sh claude` to add new technologies to `CLAUDE.md`:

- Python 3.11+ (backend)
- FastAPI, uvicorn, pydantic
- fastembed (BAAI/bge-small-en-v1.5 embedding model)
- qdrant-client (Qdrant Cloud integration)
- openai (ChatKit SDK / ChatCompletion API)
- tiktoken (token counting for chunking)
- python-frontmatter (YAML frontmatter parsing)

**Output**: Updated `CLAUDE.md` with backend tech stack, preserving existing Phase 1 (Docusaurus) technologies.

---

## Phase 2: Task Generation

**Not executed by `/sp.plan`** - Use `/sp.tasks` command to generate `tasks.md` from this plan.

Expected task structure (preview):

1. **Setup Tasks** (T001-T005): UV project init, directory structure, .env configuration
2. **Indexing Pipeline** (T006-T015): File discovery, frontmatter parsing, chunking, embedding, Qdrant upsert
3. **RAG Service** (T016-T025): Query embedding, vector search, context assembly, LLM prompting
4. **API Endpoints** (T026-T035): FastAPI routes, request validation, error handling, CORS
5. **Testing** (T036-T050): Unit tests, integration tests, contract tests, fixtures
6. **Documentation** (T051-T055): README, API docs, deployment guide, .env.example
7. **Deployment** (T056-T060): Render/Railway config, GitHub Actions CI/CD (if applicable)

---

## Open Questions (Resolved in research.md)

The following questions from spec.md will be answered in Phase 0 research:

1. ✅ Embedding Model Selection → Research Task 1
2. ✅ Chunk Strategy → Research Task 2
3. ✅ Re-Indexing Strategy → Research Task 3
4. ✅ Grounded Mode Context Length → Addressed in FR-015 (max 10,000 chars)
5. ✅ Source Citation Format → Addressed in contracts/chat.yaml (structured `sources` array)

---

## Next Steps

1. ✅ **Phase 0 Complete**: Generate `research.md` with all technical decisions
2. ✅ **Phase 1 Complete**: Generate `data-model.md`, `contracts/`, `quickstart.md`
3. ✅ **Update Agent Context**: Add Python backend tech stack to `CLAUDE.md`
4. ⏭️ **Phase 2 (Next Command)**: Run `/sp.tasks` to generate dependency-ordered task list
5. ⏭️ **Implementation**: Run `/sp.implement` to execute tasks from `tasks.md`
6. ⏭️ **Git Workflow**: Run `/sp.git.commit_pr` to commit changes and create PR

---

**Plan Status**: ✅ Ready for Phase 0 research execution
