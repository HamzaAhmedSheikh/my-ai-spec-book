---
id: 0001
title: UI/UX Rework and RAG Phase 2 Specification
stage: spec
date: 2025-11-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-ui-ux-rag-phase2
branch: 005-ui-ux-rag-phase2
user: IC Traders
command: /sp.specify
labels: ["ui-ux", "rag-chatbot", "phase2", "dark-mode", "navigation", "specification"]
links:
  spec: ../../../specs/005-ui-ux-rag-phase2/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-ui-ux-rag-phase2/spec.md
  - specs/005-ui-ux-rag-phase2/checklists/requirements.md
tests:
  - Specification quality validation (all checklist items passed)
---

## Prompt

```
/sp.specify ## INSTRUCTION: Do not overwrite the spec file. Update only the content below.

# UI/UX Rework and Phase 2 RAG Chatbot Integration

## Intent
Execute the first stage of Phase 2 by implementing major UI/UX improvements (Home Page & Dark Mode) and integrating the RAG Chatbot (Phase 2 MVP) to enable context-grounded Q&A on the book's content.

## Constraints
* **Frontend Host:** Must remain Docusaurus 3.x (Static Core).
* **Structural Rework:** The existing 42 chapters must be preserved, but the `sidebars.ts` configuration must be updated to reorganize them into 4 to 5 high-level "Parts" or "Modules" for improved navigation.
* **RAG Backend:** Must use FastAPI, Qdrant Cloud, and comply with all "Integrated RAG Chatbot" Constitution rules. The API must specifically support and process an optional `selected_text` parameter to prioritize highlighted context.

## Success Evals (SMART)
* **UI/Home Page:** The book's home page is visually updated (new components, improved layout) and the build passes without errors.
* **Dark Mode:** A functional dark mode toggle is implemented on the header, and the theme choice persists across page loads.
* **Structure Rework:** The Docusaurus sidebar configuration (`sidebars.ts`) is updated to display 4-5 high-level organizational parts, with the 42 chapters nested logically inside.
* **RAG Functionality:** The RAG Chatbot component is successfully embedded within the Docusaurus frontend, and a test query confirms it returns answers *only* from the book content (Grounding Test).
* **Selected Context Test:** A test query using the `selected_text` parameter successfully yields an answer grounded exclusively in the selected context.
* **Groundedness:** The chatbot explicitly refuses to answer a question requiring external (non-book) information, proving adherence to the Source Truth principle.

## Non-Goals (Prevents Scope Creep)
* **Bonus Features:** No implementation of Better-Auth, Personalization, or Urdu Translation (these are separate Phase 2 bonus items).
* **PDF Parsing:** Assumes content is already indexed/in the DOM.
```

## Response snapshot

Created comprehensive feature specification for UI/UX rework and Phase 2 RAG chatbot integration:

**Branch Created**: `005-ui-ux-rag-phase2`

**Key Deliverables**:
1. **Specification Document** (`specs/005-ui-ux-rag-phase2/spec.md`):
   - 4 prioritized user stories (P1-P3) with independent testability
   - 27 functional requirements organized across 6 categories:
     - Homepage and Navigation (FR-001 to FR-004)
     - Dark Mode (FR-005 to FR-009)
     - RAG Chatbot Integration (FR-010 to FR-013)
     - Context Grounding / Selected Text (FR-014 to FR-018)
     - Global Context Mode (FR-019 to FR-021)
     - Groundedness and Source Truth (FR-022 to FR-024)
     - Error Handling (FR-025 to FR-027)
   - 13 measurable success criteria (technology-agnostic)
   - 6 edge cases with expected behaviors
   - Complete Assumptions, Dependencies, Out of Scope, Constraints, and Risks sections

2. **Quality Validation** (`specs/005-ui-ux-rag-phase2/checklists/requirements.md`):
   - All 14 checklist items passed ✅
   - No [NEEDS CLARIFICATION] markers required
   - Specification ready for `/sp.plan` phase

**User Stories Priority**:
- **P1**: Context-Grounded Book Q&A (core "Magna Carta" feature)
- **P2**: Enhanced Book Navigation, Global Knowledge Access
- **P3**: Dark Mode (UX enhancement)

**Success Criteria Highlights**:
- Chatbot passes grounding test (refuses external knowledge questions)
- Selected text context yields grounded responses
- Dark mode toggle functional with persistent preference
- Sidebar reorganized into 4-5 parts with 42 chapters nested
- Response time under 5 seconds for typical queries
- WCAG AA contrast compliance (4.5:1 ratio)

## Outcome

- ✅ Impact: Feature 005 specification created with comprehensive requirements, user scenarios, and validation. Ready for planning phase.
- 🧪 Tests: Specification quality checklist validation (14/14 items passed). No clarifications needed.
- 📁 Files: Created `spec.md` (230 lines) and `requirements.md` checklist. Branch `005-ui-ux-rag-phase2` initialized.
- 🔁 Next prompts: `/sp.plan` to generate technical architecture, or `/sp.clarify` if additional refinement needed (not required based on validation).
- 🧠 Reflection: Strong specification with clear separation of user value (what/why) from implementation (how). Technology constraints (Docusaurus, FastAPI, Qdrant) appropriately scoped as business requirements per user input. Independent testability ensures incremental delivery.

## Evaluation notes (flywheel)

- Failure modes observed: None. Script correctly identified feature number 005 and created branch. All placeholders filled successfully.
- Graders run and results (PASS/FAIL): Specification Quality Checklist - PASS (14/14 items). Content Quality: PASS. Requirement Completeness: PASS. Feature Readiness: PASS.
- Prompt variant (if applicable): Standard `/sp.specify` workflow with user-provided constraints embedded in feature description.
- Next experiment (smallest change to try): During `/sp.plan`, consider creating a dedicated ADR for the 4-5 navigation parts organization decision to document the rationale for chosen themes.
