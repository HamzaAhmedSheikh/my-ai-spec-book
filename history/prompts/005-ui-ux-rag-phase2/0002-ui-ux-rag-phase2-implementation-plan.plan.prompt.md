---
id: 0002
title: UI/UX Rework and RAG Phase 2 Implementation Plan
stage: plan
date: 2025-11-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-ui-ux-rag-phase2
branch: 005-ui-ux-rag-phase2
user: IC Traders
command: /sp.plan
labels: ["ui-ux", "rag-chatbot", "phase2", "planning", "architecture", "design"]
links:
  spec: ../../../specs/005-ui-ux-rag-phase2/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-ui-ux-rag-phase2/plan.md
  - specs/005-ui-ux-rag-phase2/research.md
  - specs/005-ui-ux-rag-phase2/data-model.md
  - specs/005-ui-ux-rag-phase2/contracts/openapi.yaml
  - specs/005-ui-ux-rag-phase2/contracts/types.ts
  - specs/005-ui-ux-rag-phase2/quickstart.md
  - CLAUDE.md
tests:
  - Constitution Check gates (all 6 principles PASS)
  - Data model entity validation
  - API contract OpenAPI 3.0 compliance
---

## Prompt

```
/sp.plan
```

## Response snapshot

Successfully generated comprehensive implementation plan for UI/UX rework and Phase 2 RAG chatbot integration.

**Phase 0: Research Completed**
- 7 technology decisions documented with rationale and alternatives
- Key choices: Docusaurus built-in dark mode, global text selection listener, hybrid FastAPI + LangChain, multi-layer grounding enforcement, text-embedding-3-small (1024 token chunks), CORS middleware, 5-part sidebar structure

**Phase 1: Design Artifacts Created**
1. **plan.md** (594 lines): Complete technical architecture including:
   - Constitution Check (all 6 principles PASS)
   - Project structure (web application pattern)
   - 8 major design decisions with rationale
   - Risk mitigation strategies for 5 identified risks
   - Deployment strategy (GitHub Pages + Render/Railway + Qdrant Cloud)
   - Success criteria mapping (SC-001 to SC-013)

2. **research.md** (7 investigations): Technology research findings covering:
   - Docusaurus dark mode (built-in vs custom)
   - Text selection capture (global listener vs component-level)
   - RAG backend architecture (hybrid FastAPI + LangChain utilities)
   - Grounding prompt engineering (3-layer defense-in-depth)
   - Vector search optimization (text-embedding-3-small, 1024 tokens, 128 overlap)
   - CORS configuration (explicit origins, no wildcard)
   - Sidebar reorganization (5-part pedagogical structure)

3. **data-model.md** (11 entities): Complete entity definitions with:
   - Frontend domain: Theme Preference, Selected Text Context, Chat UI State
   - API domain: ChatRequest, GroundedChatRequest, ChatResponse, SourceCitation
   - Vector store domain: Document Chunk, Embedding Vector
   - Configuration domain: Navigation Part, Sidebar Configuration
   - Entity relationship diagram + data flow diagrams (2 scenarios)

4. **contracts/openapi.yaml** (OpenAPI 3.0 spec): 3 endpoints documented:
   - GET /health (health check)
   - POST /chat (global context mode)
   - POST /chat/grounded (selected text mode)
   - Complete request/response schemas with validation rules

5. **contracts/types.ts** (TypeScript definitions): Frontend type definitions including:
   - API request/response types
   - Frontend-specific types (ChatMessage, ChatUIState, SelectionContext)
   - Type guards for runtime validation
   - Constants (validation rules, endpoints, defaults)
   - Example usage documentation

6. **quickstart.md** (3 integration scenarios): Step-by-step implementation guides:
   - Scenario 1: Selected text grounding (frontend + backend + E2E tests)
   - Scenario 2: Global context search (full implementation)
   - Scenario 3: Dark mode persistence (Docusaurus integration)
   - Common pitfalls and troubleshooting (CORS, text detection, persistence)

**Agent Context Updated**:
- CLAUDE.md now includes: TypeScript 5.6+ (frontend), Python 3.11+ (backend)

## Outcome

- ✅ Impact: Comprehensive implementation plan created for Feature 005 with all Phase 0 (research) and Phase 1 (design) artifacts completed. Ready for `/sp.tasks` to generate implementation task list.
- 🧪 Tests: Constitution Check validation (6/6 PASS). Data model entity relationship validation. OpenAPI schema compliance check.
- 📁 Files: Created 6 planning artifacts (plan.md, research.md, data-model.md, openapi.yaml, types.ts, quickstart.md). Updated CLAUDE.md with technology stack.
- 🔁 Next prompts: `/sp.tasks` to generate dependency-ordered task list, then `/sp.implement` for execution.
- 🧠 Reflection: Plan establishes strong architectural foundation with defense-in-depth grounding (3 layers), clear separation of concerns (frontend/backend), and MVP scope adherence. Key differentiator is "Magna Carta" selected-text feature with explicit UX patterns.

## Evaluation notes (flywheel)

- Failure modes observed: None. All artifacts generated successfully with comprehensive detail.
- Graders run and results (PASS/FAIL): Constitution Check - PASS (6/6 principles). Data model completeness - PASS (11 entities with relationships). API contract validation - PASS (OpenAPI 3.0 spec valid). Quickstart scenario coverage - PASS (3 scenarios with frontend + backend + tests).
- Prompt variant (if applicable): Standard `/sp.plan` workflow executed according to template.
- Next experiment (smallest change to try): During `/sp.tasks`, consider creating a "phased rollout" task structure where dark mode (P3) and sidebar reorganization (P2) can be implemented independently before RAG chatbot (P1) to de-risk frontend changes.
