# Tasks: UI/UX Rework and Phase 2 RAG Chatbot Integration

**Input**: Design documents from `/specs/005-ui-ux-rag-phase2/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Tests**: E2E tests included per constitution Quality-First requirement. Component and API tests integrated within user story phases.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Exact file paths included in all descriptions

## Path Conventions

**Web Application Pattern** (per plan.md):
- Frontend: `my-website/src/`, `my-website/docs/`
- Backend: `api/app/`, `api/tests/`
- E2E Tests: `tests/e2e/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment setup

- [X] T001 Create backend directory structure: api/app/{models,services,routers,utils}, api/scripts/, api/tests/
- [X] T002 Initialize FastAPI project with requirements.txt (FastAPI 0.115+, qdrant-client 1.11+, openai 1.54+, langchain 0.3+, python-dotenv, pytest, httpx)
- [X] T003 [P] Create .env.example template in api/ with placeholders for OPENAI_API_KEY, QDRANT_API_KEY, QDRANT_URL, API_BASE_URL
- [X] T004 [P] Add axios dependency to my-website/package.json for API client
- [X] T005 [P] Create .gitignore entries for api/.env, api/__pycache__/, .env.local
- [X] T006 [P] Setup Playwright E2E test framework in tests/e2e/ with playwright.config.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create FastAPI app entry point in api/app/main.py with CORS middleware configured for GitHub Pages origin (https://HamzaAhmedSheikh.github.io)
- [X] T008 Implement environment variable loader in api/app/config.py with validation for required keys
- [X] T009 [P] Create base Pydantic models in api/app/models/chat.py (ChatRequest, GroundedChatRequest, ChatResponse, SourceCitation per contracts/openapi.yaml)
- [X] T010 [P] Create Document/Chunk models in api/app/models/document.py for vector store payloads
- [X] T011 Implement Qdrant client wrapper in api/app/services/qdrant_client.py with connection validation
- [X] T012 [P] Implement OpenAI embedder service in api/app/services/embedder.py using text-embedding-3-small
- [X] T013 Implement health check router in api/app/routers/health.py (GET /health endpoint)
- [X] T014 [P] Copy TypeScript type definitions from specs/005-ui-ux-rag-phase2/contracts/types.ts to my-website/src/utils/types.ts
- [X] T015 Create API client utility in my-website/src/utils/api.ts with axios instance (baseURL from env, 30s timeout, chatGlobal and chatGrounded functions per quickstart.md)
- [X] T016 Create Docusaurus Root theme wrapper in my-website/src/theme/Root.tsx with SelectionContext provider (global window.getSelection() listener per research.md decision 2)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Context-Grounded Book Q&A (Priority: P1) 🎯 MVP

**Goal**: Enable readers to highlight text and ask questions grounded exclusively in the selected content ("Magna Carta" feature)

**Independent Test**: Load any chapter, highlight a paragraph, open chat widget, ask question about selected text, verify response uses only highlighted content

### Implementation for User Story 1

- [X] T017 [P] [US1] Create ChatWidget component in my-website/src/components/ChatWidget/ChatWidget.tsx with state management (isOpen, messages, isLoading, error) per data-model.md
- [X] T018 [P] [US1] Create ChatMessage subcomponent in my-website/src/components/ChatWidget/ChatMessage.tsx for rendering user/assistant messages
- [X] T019 [P] [US1] Create ChatInput subcomponent in my-website/src/components/ChatWidget/ChatInput.tsx with submit handling
- [X] T020 [P] [US1] Create ChatWidget styles in my-website/src/components/ChatWidget/styles.module.css (floating widget bottom-right, expand/collapse animations per plan.md decision 7)
- [X] T021 [US1] Integrate ChatWidget with SelectionContext in my-website/src/components/ChatWidget/ChatWidget.tsx (read selectedText, show grounded badge if present)
- [X] T022 [P] [US1] Implement grounding prompt templates in api/app/utils/grounding.py (3-layer system prompt, retrieval validation, few-shot examples per research.md decision 4)
- [X] T023 [P] [US1] Implement text chunking utility in api/app/utils/chunking.py using LangChain RecursiveCharacterTextSplitter (1024 tokens, 128 overlap per research.md decision 5)
- [X] T024 [US1] Implement LLM service in api/app/services/llm.py with generate_grounded_response function (GPT-4 Turbo, temperature 0.3, grounded system prompt)
- [X] T025 [US1] Implement /chat/grounded endpoint in api/app/routers/chat.py using LLM service per contracts/openapi.yaml
- [X] T026 [US1] Add selected text validation in api/app/models/chat.py (min 10 chars, max 10K chars, min 5 words)
- [X] T027 [US1] Test grounding enforcement: Create grounding test suite in api/tests/test_grounding.py with 20 queries (10 in-selection, 10 out-of-selection, verify refusal on out-of-scope)

### E2E Tests for User Story 1

- [X] T028 [US1] Create E2E test in tests/e2e/chatbot-grounding.spec.ts: Navigate to chapter, highlight text, verify grounded mode badge, ask question, verify response uses selected text only

**Checkpoint**: User Story 1 (MVP) should be fully functional - chatbot answers questions grounded in highlighted text

---

## Phase 4: User Story 4 - Global Book Knowledge Access (Priority: P2)

**Goal**: Enable readers to ask broad questions and receive synthesized answers from multiple chapters with citations

**Independent Test**: Open chatbot without text selection, ask "What is ROS 2?", verify response cites relevant chapters

### Implementation for User Story 4

- [X] T029 [P] [US4] Create chapter indexing script in api/scripts/index_chapters.py to read my-website/docs/physical-ai/*.md files, chunk with 1024 tokens/128 overlap, generate embeddings, upload to Qdrant collection "book_chapters"
- [X] T030 [US4] Run indexing script to populate Qdrant with ~1000 chunks from existing 10 chapters (manual execution: cd api && python scripts/index_chapters.py)
- [X] T031 [P] [US4] Implement vector retriever in api/app/services/retriever.py (retrieve_top_k_chunks function with k=5, score_threshold=0.7 per plan.md)
- [X] T032 [US4] Implement global context LLM service in api/app/services/llm.py with generate_global_response function (builds context from top-5 chunks, enforces grounding, extracts source citations)
- [X] T033 [US4] Implement /chat endpoint in api/app/routers/chat.py using retriever + global LLM service per contracts/openapi.yaml
- [X] T034 [US4] Update ChatWidget.tsx to call chatGlobal API when no selectedText present (detect mode automatically)
- [X] T035 [US4] Add source citations rendering in ChatMessage.tsx component (display chapter links with relevance scores per data-model.md)
- [X] T036 [US4] Test groundedness: Update api/tests/test_grounding.py to include 5 external knowledge queries (e.g., "What is the weather?"), verify refusal responses

### E2E Tests for User Story 4

- [X] T037 [US4] Create E2E test in tests/e2e/chatbot-global.spec.ts: Open chatbot, verify NO grounded badge, ask "What is ROS 2?", verify sources are included with chapter links
- [X] T038 [US4] Create E2E test in tests/e2e/chatbot-refusal.spec.ts: Ask external knowledge question ("What is the weather today?"), verify refusal message

**Checkpoint**: User Stories 1 AND 4 should work independently - chatbot supports both grounded and global modes

---

## Phase 5: User Story 2 - Enhanced Book Navigation and Discovery (Priority: P2)

**Goal**: Redesign homepage and reorganize sidebar into 4-5 thematic parts for improved discoverability

**Independent Test**: Load homepage, verify visual improvements, check sidebar shows 5 parts with chapters nested, confirm user can find topic within 30 seconds

### Implementation for User Story 2

- [ ] T039 [P] [US2] Update sidebars.ts in my-website/sidebars.ts with 5-part structure per research.md decision 7: Getting Started (5 ch), Core Technologies (22 ch), AI Integration (5 ch), Hardware & Deployment (4 ch), Capstone & Resources (7 ch)
- [ ] T040 [P] [US2] Redesign homepage in my-website/src/pages/index.tsx with hero section, feature highlights, part overviews, CTAs per FR-001 from spec.md
- [ ] T041 [P] [US2] Update HomepageFeatures component in my-website/src/components/HomepageFeatures/index.tsx to showcase 5 major parts with icons and descriptions per FR-004
- [ ] T042 [P] [US2] Update HomepageFeatures styles in my-website/src/components/HomepageFeatures/styles.module.css for improved visual hierarchy
- [ ] T043 [US2] Test sidebar navigation: Verify collapsible/expandable parts (FR-003), verify all 42 chapters present under correct parts
- [ ] T044 [US2] Test homepage build: Run npm run build in my-website/ and verify no errors (SC-001)

### E2E Tests for User Story 2

- [ ] T045 [US2] Create E2E test in tests/e2e/homepage.spec.ts: Load homepage, verify hero section present, verify 5 part overviews visible
- [ ] T046 [US2] Create E2E test in tests/e2e/sidebar-navigation.spec.ts: Open sidebar, verify 5 parts visible, expand/collapse parts, verify chapters nested correctly

**Checkpoint**: User Stories 1, 2, AND 4 should work independently - homepage redesigned, sidebar reorganized, chatbot functional

---

## Phase 6: User Story 3 - Personalized Reading Environment (Priority: P3)

**Goal**: Implement dark mode toggle with persistent theme preference across sessions

**Independent Test**: Click dark mode toggle, verify theme switches, close browser, reopen site, verify dark mode persists

### Implementation for User Story 3

- [ ] T047 [P] [US3] Update docusaurus.config.ts in my-website/docusaurus.config.ts with colorMode configuration (defaultMode: 'light', respectPrefersColorScheme: true per research.md decision 1)
- [ ] T048 [P] [US3] Create DarkModeToggle component in my-website/src/components/DarkModeToggle/DarkModeToggle.tsx using useColorMode() hook per quickstart.md Scenario 3
- [ ] T049 [P] [US3] Create DarkModeToggle styles in my-website/src/components/DarkModeToggle/styles.module.css with sun/moon icon toggle
- [ ] T050 [US3] Add dark mode CSS variables in my-website/src/css/custom.css for [data-theme='dark'] (--ifm-background-color, --ifm-font-color-base, --ifm-heading-color per plan.md)
- [ ] T051 [US3] Update ChatWidget styles.module.css to respect dark mode theme (use --ifm-color-* CSS variables)
- [ ] T052 [US3] Test contrast ratios: Use axe-core or manual check to verify all text in dark mode ≥4.5:1 contrast (SC-009)

### E2E Tests for User Story 3

- [ ] T053 [US3] Create E2E test in tests/e2e/dark-mode.spec.ts: Click toggle, verify html[data-theme='dark'], verify localStorage theme='dark', reload page, verify theme persists per quickstart.md Scenario 3

**Checkpoint**: All 4 user stories should work independently - full feature set complete

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, deployment preparation, and quality assurance

- [ ] T054 [P] Create Dockerfile in api/Dockerfile for FastAPI deployment (Python 3.11 base, requirements.txt, uvicorn entrypoint)
- [ ] T055 [P] Add comprehensive error handling in api/app/routers/chat.py (OpenAI API errors, Qdrant timeouts, validation errors with user-friendly messages per FR-025, FR-027)
- [ ] T056 [P] Add API request logging in api/app/main.py middleware (log query, response time, errors for monitoring)
- [ ] T057 [P] Update README.md with local development setup instructions (frontend: npm start, backend: uvicorn app.main:app --reload, env vars setup)
- [ ] T058 Validate quickstart.md scenarios: Manually test all 3 scenarios from specs/005-ui-ux-rag-phase2/quickstart.md (selected text grounding, global search, dark mode persistence)
- [ ] T059 Run full E2E test suite: npx playwright test tests/e2e/ and verify all tests pass
- [ ] T060 [P] Performance optimization: Test chatbot response time, verify <5 seconds p95 (SC-011), add loading indicators if needed
- [ ] T061 [P] Mobile responsiveness: Test ChatWidget on mobile viewport (320px width), verify floating widget collapses to icon, verify dark mode toggle accessible
- [ ] T062 Final build validation: Run npm run build in my-website/, verify bundle size <500KB gzipped, verify no console errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1 - MVP): Can start after Foundational ✅ Independent
  - User Story 4 (P2): Can start after Foundational ✅ Independent (but enhances US1)
  - User Story 2 (P2): Can start after Foundational ✅ Fully independent
  - User Story 3 (P3): Can start after Foundational ✅ Fully independent
- **Polish (Phase 7)**: Depends on desired user stories being complete (minimum: US1 for MVP)

### User Story Dependencies

```
Foundational (T007-T016) ← BLOCKS ALL STORIES
    ↓
    ├─→ US1 (T017-T028) [P1] ← MVP Deliverable (independent)
    ├─→ US4 (T029-T038) [P2] ← Enhances US1 but testable independently
    ├─→ US2 (T039-T046) [P2] ← Fully independent (UI/navigation only)
    └─→ US3 (T047-T053) [P3] ← Fully independent (theme only)
```

**Key Insight**: After Foundational phase, all 4 user stories can be implemented in parallel by different developers. No story blocks another.

### Within Each User Story

- **US1**: ChatWidget components (T017-T020) [P] → Integration (T021) → Backend services (T022-T024) [P] → Endpoint (T025) → Validation & Tests (T026-T028)
- **US4**: Indexing (T029-T030) → Retriever (T031) [P] + LLM (T032) [P] → Endpoint (T033) → Frontend integration (T034-T035) → Tests (T036-T038)
- **US2**: Sidebar (T039) [P] + Homepage (T040-T042) [P] → Tests (T043-T046)
- **US3**: Config (T047) [P] + Component (T048-T049) [P] + CSS (T050-T051) [P] → Tests (T052-T053)

### Parallel Opportunities

**Setup Phase**:
- T003, T004, T005, T006 can run in parallel

**Foundational Phase**:
- T009 [P] and T010 [P] can run in parallel (different model files)
- T012 [P] can run in parallel with T011 (different services)
- T014 [P] and T015 can run in parallel (frontend setup independent of backend)

**User Story 1**:
- T017, T018, T019, T020 can all run in parallel (different component files)
- T022, T023 can run in parallel (different utility files)

**User Story 4**:
- T029 and T031 can run in parallel after T030 completes

**User Story 2**:
- T039, T040, T041, T042 can all run in parallel (different files)

**User Story 3**:
- T047, T048, T049, T050, T051 can all run in parallel (different files)

**Polish Phase**:
- T054, T055, T056, T057, T060, T061 can all run in parallel (different concerns)

---

## Parallel Example: User Story 1 (MVP)

**After Foundational Phase Completes**:

```bash
# Launch all US1 ChatWidget components in parallel:
Task T017: "Create ChatWidget.tsx component"
Task T018: "Create ChatMessage.tsx subcomponent"
Task T019: "Create ChatInput.tsx subcomponent"
Task T020: "Create styles.module.css"

# Meanwhile, launch backend utilities in parallel:
Task T022: "Implement grounding.py"
Task T023: "Implement chunking.py"

# Then sequentially:
Task T021: "Integrate ChatWidget with SelectionContext"
Task T024: "Implement llm.py with grounded response"
Task T025: "Implement /chat/grounded endpoint"
Task T026: "Add validation"
Task T027: "Create grounding test suite"
Task T028: "Create E2E test"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. **Complete Phase 1**: Setup (T001-T006) → 6 tasks
2. **Complete Phase 2**: Foundational (T007-T016) → 10 tasks **← CRITICAL BLOCKER**
3. **Complete Phase 3**: User Story 1 (T017-T028) → 12 tasks
4. **STOP and VALIDATE**: Test US1 independently
   - Load chapter → Highlight text → Ask question → Verify grounded response
   - Run E2E test (T028)
   - Verify grounding test suite passes (T027)
5. **Deploy MVP**: Frontend to GitHub Pages, Backend to Render/Railway
6. **Total MVP Tasks**: 28 tasks

### Incremental Delivery (Recommended)

1. **Foundation** (Phases 1-2): T001-T016 → 16 tasks → Foundation ready ✅
2. **MVP Release** (Add US1): +T017-T028 → 12 tasks → Deploy 🚀
   - Value: Grounded Q&A works, readers can ask about selected text
3. **v1.1 Release** (Add US4): +T029-T038 → 10 tasks → Deploy 🚀
   - Value: Global search works, readers can ask broad questions
4. **v1.2 Release** (Add US2): +T039-T046 → 8 tasks → Deploy 🚀
   - Value: Improved homepage, better navigation
5. **v1.3 Release** (Add US3): +T047-T053 → 7 tasks → Deploy 🚀
   - Value: Dark mode for better reading experience
6. **v2.0 Release** (Polish): +T054-T062 → 9 tasks → Production ready 🎉

**Total Feature Tasks**: 62 tasks

### Parallel Team Strategy

With 3 developers after Foundational phase:

1. **Team completes Phases 1-2 together** (T001-T016)
2. **Once Foundational is done**:
   - **Developer A**: User Story 1 (T017-T028) ← MVP priority
   - **Developer B**: User Story 4 (T029-T038) ← Enhances A's work
   - **Developer C**: User Story 2 (T039-T046) ← Independent UI work
3. **Then Developer C continues**:
   - User Story 3 (T047-T053) ← Independent theme work
4. **Final integration**: All devs collaborate on Polish (T054-T062)

**Timeline Estimate**: ~2-3 weeks with 3 devs working in parallel

---

## Success Criteria Coverage

**From Spec (SC-001 to SC-013)** → **Task Mapping**:

| Success Criteria | Primary Tasks | Validation Method |
|---|---|---|
| SC-001: Homepage displays updates, build passes | T040, T041, T044 | npm run build succeeds |
| SC-002: Dark mode toggle functional | T048, T049 |
| SC-003: Dark mode persists | T047, T053 | E2E test with browser reload |
| SC-004: Sidebar shows 4-5 parts | T039, T043 | Visual inspection |
| SC-005: Chatbot embedded, accessible | T017, T021 | All pages show widget |
| SC-006: Selected text grounding works | T024, T025, T028 | E2E test + grounding suite (T027) |
| SC-007: Global context with citations | T032, T033, T037 | E2E test verifies sources |
| SC-008: External questions refused | T027, T036, T038 | Grounding tests + E2E refusal test |
| SC-009: Dark mode contrast ≥4.5:1 | T052 | axe-core automated check |
| SC-010: Navigate to chapter <30 sec | T039, T046 | User testing (manual) |
| SC-011: Response time <5 seconds | T060 | Load testing with performance monitoring |
| SC-012: Smooth dark mode transition | T050, T051 | Visual QA |
| SC-013: Understand structure <10 sec | T040, T045 | User testing (manual) |

**All success criteria have corresponding tasks for validation** ✅

---

## Notes

- **[P] tasks**: Different files, no dependencies → Can run in parallel
- **[Story] labels**: Map tasks to specific user stories for traceability
- **Independent testability**: Each user story can be completed and tested without others
- **MVP scope**: User Story 1 (28 tasks total) delivers core "Magna Carta" feature
- **Commit strategy**: Commit after each task or logical group (e.g., all [P] ChatWidget components together)
- **Checkpoints**: Stop after each user story phase to validate independently before moving forward
- **Dependencies file**: Qdrant indexing (T030) requires existing chapters in my-website/docs/physical-ai/
- **Environment setup**: .env file required before backend tasks (T030, T059)
- **Format validation**: All tasks follow strict checklist format ✅
  - Checkbox prefix: `- [ ]`
  - Task ID: T001-T062 sequential
  - [P] marker: Only for parallelizable tasks
  - [Story] label: US1, US2, US3, US4 for user story tasks
  - File paths: Included in all implementation tasks
