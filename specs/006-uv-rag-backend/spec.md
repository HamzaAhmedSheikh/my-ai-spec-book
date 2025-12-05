# Feature Specification: UV-Based RAG Chatbot Backend

**Feature Branch**: `006-uv-rag-backend`
**Created**: 2025-11-30
**Status**: Draft
**Input**: User description: "Create a backend project using uv for a RAG chatbot that integrates with a Docusaurus book stored in my-website/docs/physical-ai/."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Global Book Question Answering (Priority: P1)

A reader visits the Physical AI textbook website and wants to ask questions about robotics concepts covered across multiple chapters. They open the chatbot interface, type "What are the main differences between ROS2 nodes and services?", and receive an accurate answer synthesized from relevant sections across the entire book.

**Why this priority**: This is the core value proposition of the RAG chatbot - enabling readers to get instant answers from the comprehensive knowledge base without manually searching through 42 chapters. This delivers immediate learning value.

**Independent Test**: Can be fully tested by indexing the book content, sending test queries via API, and verifying retrieved context includes relevant chapters and the generated response accurately synthesizes information from multiple sources.

**Acceptance Scenarios**:

1. **Given** all markdown files are indexed in Qdrant, **When** a user asks "What is Physical AI?", **Then** the system retrieves context from relevant chapters and returns a coherent answer citing multiple sources
2. **Given** the chatbot is running, **When** a user asks about a specific technical concept like "URDF", **Then** the response includes definitions, examples, and references to specific chapter sections
3. **Given** a query about a topic not covered in the book, **When** the user asks the question, **Then** the system responds that the information is not available in the current knowledge base

---

### User Story 2 - Text Selection Grounding ("Magna Carta" Feature) (Priority: P2)

A reader is studying Chapter 14 about Gazebo and highlights a specific paragraph about sensor integration. They click "Ask about this selection" and type "How does this apply to humanoid robots?". The chatbot answers using only the highlighted text as context, providing focused clarification without introducing information from other chapters.

**Why this priority**: This "Magna Carta" feature enables precise, context-aware learning where users can drill down into specific passages. It's the second-highest priority because it significantly enhances learning effectiveness but depends on the global RAG system being functional first.

**Independent Test**: Can be tested by providing a text selection payload to the grounded chat endpoint, verifying that only the selected text is used as context (not the full book), and confirming the response stays within the scope of the selection.

**Acceptance Scenarios**:

1. **Given** a user has selected 2-3 paragraphs from a chapter, **When** they submit a question via the grounded endpoint, **Then** the response uses only the selected text as context
2. **Given** a selected text snippet about ROS2 nodes, **When** the user asks "What are the limitations?", **Then** the answer addresses only limitations mentioned in the selection, not the entire book
3. **Given** a very short selection (1 sentence), **When** the user asks a broad question, **Then** the system acknowledges the limited context and provides the best answer possible from the selection

---

### User Story 3 - Content Indexing and Updates (Priority: P3)

An administrator or automated process needs to index or re-index the Physical AI book content after chapters are updated. They trigger the indexing endpoint, and the system recursively reads all markdown files from `my-website/docs/physical-ai/`, chunks the content, generates embeddings, and stores them in Qdrant with metadata (chapter title, file path, section).

**Why this priority**: While essential for the system to function, indexing is a one-time or periodic operation that happens behind the scenes. It's lower priority than the user-facing query features because users don't directly interact with it, but it must be reliable.

**Independent Test**: Can be tested by pointing the indexing process at a test directory with sample markdown files, verifying all files are discovered recursively, checking that chunks are created with appropriate size and overlap, confirming embeddings are generated and stored with correct metadata, and validating idempotency (re-indexing doesn't create duplicates).

**Acceptance Scenarios**:

1. **Given** 10 markdown files in nested folders under `docs/physical-ai/`, **When** the indexing process runs, **Then** all 10 files are discovered and processed
2. **Given** a markdown file with 5000 words, **When** chunking occurs, **Then** the content is split into appropriately sized chunks (500-1000 tokens) with metadata preserved
3. **Given** an existing index in Qdrant, **When** re-indexing is triggered, **Then** old content is replaced or updated without creating duplicate entries
4. **Given** a markdown file with frontmatter (title, description), **When** indexing occurs, **Then** metadata is extracted and stored with each chunk for enhanced retrieval

---

### Edge Cases

- What happens when a markdown file is empty or contains only frontmatter?
- How does the system handle markdown files with code blocks, tables, or Mermaid diagrams during chunking?
- What happens if the Qdrant connection fails during indexing?
- How does the system behave when a user query is empty or contains only special characters?
- What happens if the selected text for grounded queries is extremely long (>5000 tokens)?
- How does the system handle concurrent indexing requests?
- What happens when OpenAI API rate limits are hit during question answering?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST initialize a Python project using `uv` package manager with project structure: `backend/app/main.py`, `backend/app/routes.py`, `backend/app/rag.py`, `backend/app/embeddings.py`, `requirements.txt`, and `pyproject.toml`
- **FR-002**: System MUST recursively discover and read all markdown (`.md`) files from the directory `my-website/docs/physical-ai/` and its subdirectories
- **FR-003**: System MUST chunk markdown content into semantically coherent segments of 500-1000 tokens with 100-token overlap between consecutive chunks to preserve context
- **FR-004**: System MUST generate vector embeddings for each chunk using the `fastembed` library with a model suitable for semantic search (default: `BAAI/bge-small-en-v1.5`)
- **FR-005**: System MUST store embeddings in Qdrant Cloud Free Tier with metadata including: source file path, chapter title, chunk index, and original text
- **FR-006**: System MUST provide a FastAPI-based REST API with CORS enabled for Docusaurus website integration
- **FR-007**: System MUST implement a `/health` endpoint that returns service status and confirms Qdrant connectivity
- **FR-008**: System MUST implement a `POST /chat` endpoint that accepts a user question, retrieves top-k relevant chunks from Qdrant (k=5), constructs a prompt with context, and returns an LLM-generated answer using OpenAI ChatKit SDK
- **FR-009**: System MUST implement a `POST /chat/grounded` endpoint that accepts a user question and selected text snippet, uses only the provided text as context (no Qdrant retrieval), and returns an LLM-generated answer
- **FR-010**: System MUST implement a `POST /index` endpoint (or background task) that triggers the indexing process: discovers markdown files, chunks content, generates embeddings, and stores in Qdrant
- **FR-011**: System MUST extract markdown frontmatter (title, description, sidebar_position) and include it as metadata for enhanced search relevance
- **FR-012**: System MUST handle errors gracefully: return appropriate HTTP status codes (400 for bad requests, 500 for server errors, 503 for service unavailable) with descriptive error messages
- **FR-013**: System MUST log all API requests, embedding generation operations, and errors for debugging and monitoring
- **FR-014**: System MUST support environment-based configuration via `.env` file for secrets: OpenAI API key, Qdrant URL, Qdrant API key
- **FR-015**: System MUST validate user input: ensure questions are non-empty, selected text length is within limits (max 10,000 characters), and reject malformed requests

### Key Entities

- **Document**: Represents a single markdown file from `docs/physical-ai/`. Attributes: file_path (string), title (string from frontmatter or filename), content (full markdown text), metadata (dict with frontmatter fields).
- **Chunk**: A semantically coherent segment of a Document. Attributes: chunk_id (UUID), source_document (file path), chunk_index (integer position in document), text (chunk content), token_count (integer), embedding (vector array), metadata (dict inheriting from document + chunk-specific info).
- **Query**: A user question submitted to the chatbot. Attributes: question (string), mode (enum: "global" or "grounded"), selected_text (optional string for grounded mode), timestamp.
- **Response**: The LLM-generated answer to a Query. Attributes: answer (string), sources (list of chunk references: file path + chunk index), context_used (list of text snippets), latency (float in seconds).
- **IndexingJob**: Represents an indexing operation. Attributes: job_id (UUID), status (enum: "pending", "running", "completed", "failed"), files_processed (integer count), chunks_created (integer count), started_at (datetime), completed_at (datetime), error (optional string).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can ask questions about the Physical AI book and receive accurate answers synthesized from relevant chapters in under 3 seconds (p95 latency)
- **SC-002**: The system correctly retrieves relevant context for 90% of test queries (precision evaluated against ground truth chapter associations)
- **SC-003**: The "Ask about selection" grounded mode restricts answers to only the provided text without hallucinating information from the broader knowledge base (verified through test cases)
- **SC-004**: The indexing process completes for all 42 chapters (approximately 100+ markdown files) in under 5 minutes on initial run
- **SC-005**: The system handles at least 100 concurrent chat requests without degradation in response quality or latency exceeding 5 seconds
- **SC-006**: Embedding storage in Qdrant Cloud Free Tier stays within 1GB limit for the complete Physical AI book (estimated 200,000-300,000 tokens across all chapters)
- **SC-007**: The chatbot achieves at least 85% user satisfaction for answer relevance and accuracy (measured through user feedback or evaluation set)
- **SC-008**: System maintains 99% uptime when deployed (health check endpoint responds within 500ms)

## Scope *(mandatory)*

### In Scope

- UV-based Python project initialization with FastAPI framework
- Recursive markdown file discovery from `my-website/docs/physical-ai/` directory
- Text chunking with semantic awareness (preserving paragraph/section boundaries when possible)
- Embedding generation using fastembed library
- Vector storage in Qdrant Cloud Free Tier
- RESTful API with three core endpoints: `/health`, `POST /chat`, `POST /chat/grounded`, `POST /index`
- OpenAI integration via ChatKit SDK for answer generation
- Environment-based configuration for API keys and service URLs
- Basic error handling and logging
- CORS configuration for Docusaurus website integration
- Metadata extraction from markdown frontmatter
- Documentation: README with setup instructions, API endpoint documentation, environment variable requirements

### Out of Scope

- Authentication/authorization (no user login required for MVP)
- Rate limiting or API quotas per user
- Caching of query results
- Advanced chunking strategies (semantic splitting based on topics/embeddings)
- Multi-language support (English only for MVP)
- Real-time indexing triggered by file system changes
- UI/frontend components (frontend integration is handled by separate Docusaurus feature)
- Vector database migration tools or backup/restore functionality
- A/B testing of different embedding models or chunk sizes
- Performance optimization beyond basic implementation (profiling, caching layers)
- Deployment configuration (Render, Railway, or other platforms - handled separately)

## Dependencies & Assumptions *(mandatory)*

### Dependencies

- **External Services**:
  - Qdrant Cloud Free Tier account and API key
  - OpenAI API account and API key (GPT-4 or GPT-4 Turbo access)
  - Internet connectivity for API calls
- **File System**:
  - Access to `my-website/docs/physical-ai/` directory (assumes this path exists relative to backend or via configuration)
  - Read permissions for all markdown files in the target directory
- **Development Tools**:
  - Python 3.11 or higher
  - `uv` package manager installed (`pip install uv` or system package)
  - Node.js environment for running Docusaurus (separate, not part of backend)

### Assumptions

- **Content Assumptions**:
  - Markdown files in `docs/physical-ai/` are well-formed with valid frontmatter (YAML)
  - Content is primarily English text suitable for embedding models
  - Average chapter length is 2000-5000 words
  - Total corpus size is approximately 200,000-300,000 tokens across 42 chapters
- **Infrastructure Assumptions**:
  - Qdrant Cloud Free Tier (1GB storage) is sufficient for the entire book corpus
  - OpenAI API costs are acceptable for estimated query volume (development/demo use)
  - Backend and Docusaurus site may run on different ports/domains (CORS required)
- **Usage Assumptions**:
  - Initial use is for demo/development, not high-traffic production
  - Concurrent users will be low (<100 simultaneous requests)
  - Re-indexing is infrequent (only when chapters are updated)
- **Technical Assumptions**:
  - FastAPI auto-generates OpenAPI docs at `/docs` and `/redoc`
  - Embeddings from fastembed are compatible with Qdrant vector similarity search
  - OpenAI ChatKit SDK provides a straightforward interface for chat completion

## Non-Functional Requirements *(optional)*

### Performance

- API response time (p95) for `/chat` endpoint: <3 seconds
- API response time (p95) for `/chat/grounded` endpoint: <2 seconds (no vector search overhead)
- Health check endpoint response time: <500ms
- Indexing throughput: Process at least 10 markdown files per minute
- Concurrent request handling: Support 100 simultaneous chat requests without queueing

### Scalability

- Vector storage: Designed to handle up to 500,000 chunks (expandable beyond current 42-chapter corpus)
- Qdrant collection: Use appropriate indexing strategy (HNSW) for sub-100ms vector search at scale

### Reliability

- Error recovery: API endpoints return appropriate HTTP status codes and error messages
- Graceful degradation: If Qdrant is unavailable, health check reports degraded status; chat endpoints return 503
- Idempotency: Re-running indexing process updates existing chunks without duplication

### Security

- API keys stored in `.env` file (never committed to version control)
- `.env.example` provided with placeholder values for required secrets
- CORS configured to allow requests only from specified Docusaurus domains (configurable via environment)
- Input validation: Sanitize user queries to prevent injection attacks (though LLM context is isolated)

### Maintainability

- Code structure: Modular design with separation of concerns (routes, RAG logic, embedding generation)
- Type hints: Use Python type annotations throughout for IDE support and type checking
- Logging: Structured logging with log levels (INFO for requests, ERROR for failures)
- Documentation: Inline docstrings for functions, README with setup and API usage

## Risks & Mitigations *(optional)*

### Risk 1: Qdrant Free Tier Storage Limit

**Impact**: If the book corpus exceeds 1GB of vector storage, indexing will fail or be incomplete.

**Mitigation**:
- Monitor storage usage during initial indexing
- Implement chunk size optimization (target 500-800 tokens instead of 1000)
- Provide fallback: warn if approaching limit and suggest reducing chunk overlap or using smaller embedding model

### Risk 2: OpenAI API Rate Limits or Cost Overruns

**Impact**: High query volume could hit rate limits or incur unexpected costs during development/demo.

**Mitigation**:
- Implement basic logging of API call counts
- Document expected costs based on query volume
- Suggest using GPT-3.5-turbo for development, GPT-4 for production/demo
- Consider adding a simple request counter to warn when approaching cost thresholds

### Risk 3: Poor Retrieval Relevance

**Impact**: RAG system retrieves irrelevant chunks, leading to inaccurate or nonsensical answers.

**Mitigation**:
- Use a proven embedding model (BAAI/bge-small-en-v1.5 or similar) with good semantic search performance
- Tune retrieval parameters (top-k, similarity threshold) based on test queries
- Include metadata filtering (e.g., restrict to specific chapters/modules if needed)
- Implement a "confidence score" or "sources" display so users can verify retrieved context

### Risk 4: Path Resolution Issues Across Platforms

**Impact**: Hardcoded paths to `my-website/docs/physical-ai/` may fail on different operating systems or deployment environments.

**Mitigation**:
- Use environment variable for book content path (e.g., `BOOK_CONTENT_PATH`)
- Use `pathlib.Path` for cross-platform path handling
- Provide clear documentation on setting the path for local development vs. deployment

### Risk 5: Markdown Parsing Edge Cases

**Impact**: Complex markdown (nested lists, tables, code blocks, Mermaid diagrams) may break chunking or produce poor embeddings.

**Mitigation**:
- Test chunking logic with sample chapters containing edge cases
- Strip or handle code blocks specially (e.g., exclude from embeddings or chunk separately)
- Use a markdown parser library (e.g., `markdown-it-py`) to preserve structure during chunking

## Open Questions *(optional)*

1. **Embedding Model Selection**: Should we use `BAAI/bge-small-en-v1.5` (lightweight, fast) or a larger model like `BAAI/bge-base-en-v1.5` (better accuracy but slower)? Trade-off between latency and retrieval quality.

2. **Chunk Strategy**: Should chunks respect markdown section boundaries (split at `##` headers) for better semantic coherence, or use fixed token windows with overlap? Header-aware chunking may improve relevance but is more complex.

3. **Re-Indexing Strategy**: Should the `/index` endpoint replace the entire Qdrant collection or update/upsert chunks incrementally? Full replacement is simpler but slower; incremental updates are more efficient but require tracking file changes.

4. **Grounded Mode Context Length**: What is the maximum allowed length for selected text in the grounded endpoint? Should we enforce a hard limit (e.g., 5000 characters) or allow up to the LLM context window limit?

5. **Source Citation Format**: How should the chatbot present sources in the response? Should it include chapter titles, file paths, or chunk indices? Should sources be returned as structured metadata or embedded in the answer text?

## Related Documentation *(optional)*

- [Docusaurus Physical AI Book Structure](../../docs/physical-ai/) - Target content directory
- [Project Constitution](../../.specify/memory/constitution.md) - Phase 2 RAG requirements and scoring criteria
- [FastAPI Official Documentation](https://fastapi.tiangolo.com/) - Framework reference
- [Qdrant Cloud Documentation](https://qdrant.tech/documentation/cloud/) - Vector database setup
- [Fastembed Documentation](https://qdrant.github.io/fastembed/) - Embedding generation library
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference) - LLM integration
