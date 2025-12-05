---
id: 0002
title: Generate implementation plan for UV RAG backend
stage: plan
date: 2025-11-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 006-uv-rag-backend
branch: 006-uv-rag-backend
user: User
command: /sp.plan
labels: ["planning", "rag", "backend", "uv", "fastapi", "qdrant", "architecture"]
links:
  spec: specs/006-uv-rag-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-uv-rag-backend/plan.md
  - specs/006-uv-rag-backend/research.md
  - specs/006-uv-rag-backend/data-model.md
  - specs/006-uv-rag-backend/quickstart.md
  - specs/006-uv-rag-backend/contracts/health.yaml
  - specs/006-uv-rag-backend/contracts/chat.yaml
  - specs/006-uv-rag-backend/contracts/grounded.yaml
  - specs/006-uv-rag-backend/contracts/index.yaml
  - CLAUDE.md (agent context updated)
tests:
  - Constitution Check validated (all 5 gates passed)
  - Research decisions documented with alternatives
  - Data model validation rules defined
  - OpenAPI contracts validated against spec requirements
---

## Prompt

/sp.plan

Phase 1: Book Setup
- Use Docusaurus in my-website/
- Ensure docs/physical-ai/ contains folders + Markdown files
- Prepare content for RAG indexing

Phase 2: Backend Setup
- Initialize backend with `uv init backend`
- Create FastAPI app structure under backend/app/

Phase 3: RAG Pipeline
- Read all MD files recursively
- Chunk + embed using fastembed
- Store embeddings in Qdrant Cloud
- Implement retrieval + ChatKit answer generation

Phase 4: Integration
- Create API endpoints for questions + selection-based answers
- Connect backend to Docusaurus UI chatbot widget

Phase 5: Delivery
- Live backend API + indexed content
- Chatbot answering from book + selected text

## Response snapshot

Generated comprehensive implementation plan with Phase 0 (Research) and Phase 1 (Design) complete:

**Plan Structure**:
- **Summary**: RAG chatbot backend using UV, FastAPI, Qdrant, and OpenAI
- **Technical Context**: Python 3.11+, FastAPI 0.104+, fastembed, qdrant-client, performance goals <3s latency
- **Constitution Check**: ✅ ALL 5 GATES PASSED (Phase-Driven, Spec-Driven, Quality-First, Security, Simplicity)
- **Project Structure**: Backend API (Option 2: Web application) with 12 Python modules + pytest test suite

**Phase 0 - Research & Technical Decisions** (6 research tasks completed):
1. **Embedding Model**: Selected BAAI/bge-small-en-v1.5 (384-dim, storage efficient, 0.82 NDCG@10)
2. **Chunking Strategy**: Hybrid approach - 500-1000 tokens with 100-token overlap, respecting paragraph boundaries
3. **Re-Indexing**: Full collection replacement (simple, idempotent, <5 min for 100 files)
4. **OpenAI Integration**: Direct Python SDK (not ChatKit - clarified misconception), chat completion API
5. **Qdrant Config**: Cosine similarity, HNSW indexing, ~10MB storage for 5K chunks
6. **CORS**: Environment-based whitelist for dev (localhost) and prod (GitHub Pages)

**Phase 1 - Design & Contracts**:
- **data-model.md**: 5 entities (Document, Chunk, Query, Response, IndexingJob) with Pydantic validation rules
- **contracts/**: 4 OpenAPI 3.0 specs (health.yaml, chat.yaml, grounded.yaml, index.yaml) with request/response schemas
- **quickstart.md**: 6 integration scenarios (local setup, indexing, global chat, grounded chat, Docusaurus integration, testing)
- **Agent Context**: Updated CLAUDE.md with Python 3.11+, FastAPI, fastembed, qdrant-client, openai, tiktoken, pydantic

**Key Architectural Decisions**:
- FastAPI backend separate from Docusaurus (Phase 1: Book, Phase 2: Backend alignment)
- Synchronous indexing for MVP (202 async response deferred)
- No authentication/authorization in MVP (out of scope)
- Grounded mode uses selected_text only (no Qdrant retrieval)

## Outcome

- ✅ Impact: Complete implementation plan with all technical decisions documented. Research resolved 6 open questions from spec. Design artifacts (data model, contracts, quickstart) ready for task generation.
- 🧪 Tests: Constitution Check passed all 5 gates. Research alternatives evaluated. Data model includes Pydantic validation. API contracts include error scenarios.
- 📁 Files: 9 files created (plan.md, research.md, data-model.md, quickstart.md, 4 OpenAPI contracts, CLAUDE.md updated)
- 🔁 Next prompts: Run `/sp.tasks` to generate dependency-ordered task list from plan.md. Then `/sp.implement` to execute tasks.
- 🧠 Reflection: Plan demonstrates thorough research (alternatives considered, rationale documented) and pragmatic MVP scoping (simplicity over perfection). Embedding model selection (bge-small vs. bge-base) and chunking strategy (hybrid approach) are well-justified. OpenAI SDK clarification prevents future confusion (ChatKit is not the correct SDK).

## Evaluation notes (flywheel)

- Failure modes observed: None - workflow executed smoothly from setup through agent context update
- Graders run and results (PASS/FAIL): Constitution Check - PASS (5/5 gates). Research quality - PASS (alternatives documented with trade-offs). Contract validation - PASS (matches spec requirements).
- Prompt variant (if applicable): Standard /sp.plan workflow with user-provided phase breakdown (integrated into research tasks)
- Next experiment (smallest change to try): Consider documenting ADR for embedding model selection (meets significance criteria: long-term impact, multiple alternatives, cross-cutting). User can run `/sp.adr embedding-model-selection` if desired.
