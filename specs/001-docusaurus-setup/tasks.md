# Tasks: Docusaurus Documentation Site for Physical AI & Humanoid Robotics Book

**Input**: Design documents from `/specs/001-docusaurus-setup/`
**Prerequisites**: plan.md ✅, spec.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Environment Validation)

**Purpose**: Verify system meets requirements before initialization

**Checkpoint**: Environment ready for Docusaurus installation

- [X] T001 Verify Node.js version >= 18.0 with `node --version`
- [X] T002 [P] Verify npm is available with `npm --version`
- [X] T003 [P] Verify source textbook exists at `F:\my-ai-book\my-ai-spec-book\Hackathon I_ Physical AI & Humanoid Robotics Textbook.md`
- [X] T004 [P] Confirm current working directory is `F:\my-ai-book\my-ai-spec-book`

**Acceptance**: All verification checks pass; no blocking errors detected

---

## Phase 2: Foundational (Docusaurus Initialization & Configuration)

**Purpose**: Create functional Docusaurus project with TypeScript support and configure site metadata

**⚠️ CRITICAL**: All content work depends on this phase completion

Status,Task ID,Description
- [X] T005 [US1] Execute npx create-docusaurus@latest my-website classic --typescript to initialize Docusaurus
- [X] T006 [US1] Wait for npm package installation to complete
- [X] T007 [US1] "Verify initialization created my-website/docusaurus.config.ts, my-website/package.json, my-website/sidebars.ts,
                   my-website/docs/, my-website/src/, and my-website/static/"
- [X] T008 [US1] Navigate into the my-website/ directory and run npm start to verify the site loads at localhost:3000
- [X] T009 [US1] Stop the development server (Ctrl+C)
- [X] T010 [US2] Open my-website/docusaurus.config.ts and update the title field to 'Physical AI & Humanoid Robotics'

**Checkpoint**: Foundation ready - Docusaurus site functional with correct configuration

**Acceptance Criteria**:
- Development server starts within 30 seconds (SC-007)
- Site title displays "Physical AI & Humanoid Robotics" in browser tab (SC-002)
- Production build completes in <2 minutes without errors (SC-005)
- Root URL will redirect to first doc when content is added (FR-017)

---

## Phase 3: User Story 4 - Create Physical AI Documentation Section Structure (Priority: P4)

**Goal**: Create dedicated documentation section for course textbook with structured sidebar category

**Independent Test**: Start dev server and verify "Course Textbook" sidebar category appears with proper structure

- [X] T017 [US4] Navigate to `my-website/docs/` directory
- [X] T018 [US4] Remove default Docusaurus tutorial content: delete `my-website/docs/intro.md`, `my-website/docs/tutorial-basics/`, `my-website/docs/tutorial-extras/`
- [X] T019 [US4] Create new directory at `my-website/docs/physical-ai/`
- [X] T020 [US4] Verify `my-website/docs/physical-ai/` directory exists and is empty

**Checkpoint**: Content directory structure ready

**Acceptance Criteria**:
- `my-website/docs/physical-ai/` directory exists (US4-AC1)
- Default tutorial content removed
- Directory ready to receive 10 markdown files

---

## Phase 4: User Story 5 - Split and Organize Textbook Content into Individual Pages (Priority: P5)

**Goal**: Extract content from source textbook and distribute into 10 separate, well-organized markdown files

**Independent Test**: Verify all 10 markdown files exist in `my-website/docs/physical-ai/`, each contains extracted content with proper frontmatter

### Content Mapping & File Creation

**⚠️ CRITICAL**: Content must be copied exactly as-is from source (FR-014, FR-015). No rewriting, paraphrasing, or summarizing allowed.

- [X] T021 [P] [US5] Open source file `Hackathon I_ Physical AI & Humanoid Robotics Textbook.md` and identify section boundaries
- [X] T022 [P] [US5] Create `my-website/docs/physical-ai/introduction.md` with frontmatter (title: "Introduction to Physical AI & Humanoid Robotics", sidebar_label: "Introduction", sidebar_position: 1) and extract lines 1-8 from source
- [X] T023 [P] [US5] Create `my-website/docs/physical-ai/quarter-overview.md` with frontmatter (title: "Quarter Overview", sidebar_label: "Quarter Overview", sidebar_position: 2) and extract lines 9-36 from source
- [X] T024 [P] [US5] Create `my-website/docs/physical-ai/why-physical-ai-matters.md` with frontmatter (title: "Why Physical AI Matters", sidebar_label: "Why It Matters", sidebar_position: 3) and extract lines 39-41 from source
- [X] T025 [P] [US5] Create `my-website/docs/physical-ai/learning-outcomes.md` with frontmatter (title: "Learning Outcomes", sidebar_label: "Learning Outcomes", sidebar_position: 4) and extract lines 43-50 from source
- [X] T026 [P] [US5] Create `my-website/docs/physical-ai/weekly-breakdown.md` with frontmatter (title: "Weekly Breakdown", sidebar_label: "Weekly Breakdown", sidebar_position: 5) and extract lines 52-95 from source
- [X] T027 [P] [US5] Create `my-website/docs/physical-ai/assessments.md` with frontmatter (title: "Assessments", sidebar_label: "Assessments", sidebar_position: 6) and extract lines 97-102 from source
- [X] T028 [P] [US5] Create `my-website/docs/physical-ai/hardware-requirements.md` with frontmatter (title: "Hardware Requirements", sidebar_label: "Hardware", sidebar_position: 7) and extract lines 104-122 from source
- [X] T029 [P] [US5] Create `my-website/docs/physical-ai/lab-setup.md` with frontmatter (title: "Lab Setup Guide", sidebar_label: "Lab Setup", sidebar_position: 8) and extract lines 127-136 from source
- [X] T030 [P] [US5] Create `my-website/docs/physical-ai/student-kits.md` with frontmatter (title: "Student Kit Options", sidebar_label: "Student Kits", sidebar_position: 9) and extract lines 138-150+ from source
- [X] T031 [P] [US5] Create `my-website/docs/physical-ai/cloud-lab-options.md` with frontmatter (title: "Cloud & Remote Lab Options", sidebar_label: "Cloud Labs", sidebar_position: 10) and extract remaining content from source

### Content Quality Validation

- [X] T032 [US5] Verify all 10 files exist in `my-website/docs/physical-ai/` directory
- [X] T033 [US5] Verify each file has valid YAML frontmatter with `title`, `sidebar_label`, and `sidebar_position` fields
- [X] T034 [US5] Verify each `sidebar_position` value is unique (1-10)
- [X] T035 [US5] Spot-check 3 files to confirm content matches source sections exactly (no rewriting)

**Checkpoint**: All content files created with proper structure

**Acceptance Criteria**:
- All 10 markdown files exist (FR-011, US5-AC1, SC-004)
- Each file contains correct frontmatter (FR-013, US5-AC3)
- Content matches source sections exactly (US5-AC2, SC-009)
- Zero rewritten content (SC-009, SC-010)

---

## Phase 5: User Story 6 - Preserve Original Content Formatting and Structure (Priority: P6)

**Goal**: Ensure all original textbook content is preserved exactly as provided, including all markdown elements

**Independent Test**: Compare rendered pages in browser against source textbook sections and verify identical rendering

- [X] T036 [US6] Verify all headings maintain original hierarchy levels (H1, H2, H3, etc.) across all 10 files
- [X] T037 [US6] Verify all lists (bulleted, numbered) and tables preserve original structure
- [X] T038 [US6] Verify all hyperlinks remain functional and point to correct destinations
- [X] T039 [US6] Verify all code blocks (if any) render correctly with syntax preservation
- [X] T040 [US6] Verify all bold/italic/emphasis formatting preserved across all files

**Checkpoint**: Content formatting validation complete

**Acceptance Criteria**:
- All markdown formatting preserved (US6-AC1, US6-AC2, SC-008)
- 100% formatting match with source (SC-010)
- All hyperlinks functional (SC-011)

---

## Phase 6: Sidebar Configuration (Priority: P4 continued)

**Goal**: Configure sidebar to display "Course Textbook" category with all 10 pages in correct order

**Independent Test**: View site and verify sidebar shows all 10 pages in specified order (1-10)

- [X] T041 [US4] Open `my-website/sidebars.ts`
- [X] T042 [US4] Replace default configuration with TypeScript autogenerated sidebar using `type: 'category'` and `type: 'autogenerated'` for `dirName: 'physical-ai'`
- [X] T043 [US4] Set category label to `'Course Textbook'`
- [X] T044 [US4] Save `my-website/sidebars.ts` file
- [X] T045 [US4] Verify sidebar configuration references correct directory (`physical-ai`)

**Checkpoint**: Sidebar configured to automatically generate from content files

**Acceptance Criteria**:
- Sidebar displays "Course Textbook" category (FR-012, US4-AC2, SC-003)
- All 10 pages listed in sidebar (FR-012, SC-003)
- Pages appear in correct order (1-10) based on `sidebar_position` frontmatter (US4-AC2)

---

## Phase 7: User Story 3 - Verify Complete Documentation Site Functionality (Priority: P3)

**Goal**: Verify complete Docusaurus site functions correctly with all content in place, ready for review

**Independent Test**: Build production site and serve locally, navigate through all pages to verify functionality

### Build Verification

- [ ] T046 [US3] Clean previous build artifacts: run `npm run clear` from my-website/ or manually delete `my-website/build/` and `my-website/.docusaurus/`
- [ ] T047 [US3] Run production build: `npm run build` from my-website/
- [ ] T048 [US3] Monitor build output for errors or warnings
- [ ] T049 [US3] Verify build directory created at `my-website/build/` with static files

### Production Site Testing

- [ ] T050 [US3] Serve production build locally: `npm run serve` from my-website/
- [ ] T051 [US3] Access site in browser (verify correct localhost port)
- [ ] T052 [US3] Verify root URL (`/`) redirects to introduction page
- [ ] T053 [US3] Click through all 10 sidebar items and verify each page loads without 404 errors
- [ ] T054 [US3] Verify active page highlighted in sidebar during navigation
- [ ] T055 [US3] Verify page transitions work smoothly between pages

### Content Display Verification

- [ ] T056 [US3] Spot-check 3-5 pages for formatting preservation (headings, lists, tables)
- [ ] T057 [US3] Test at least 2 hyperlinks from source content to verify functionality
- [ ] T058 [US3] Verify tables render correctly (if present in content)
- [ ] T059 [US3] Verify code blocks render correctly (if present in content)
- [ ] T060 [US3] Verify browser console shows zero errors

### Performance Verification

- [ ] T061 [US3] Confirm production build completed in <2 minutes
- [ ] T062 [US3] Verify no build warnings or errors in terminal output
- [ ] T063 [US3] Stop serve process

**Checkpoint**: Complete site verified and ready for deployment planning

**Acceptance Criteria**:
- Production build completes successfully (FR-007, US3-AC1, SC-005)
- All 10 pages accessible and navigable (US3-AC2, SC-006)
- Page transitions work smoothly (US3-AC3)
- Root redirects to introduction (FR-017, SC-012)
- Content displays correctly (SC-008)
- Hyperlinks functional (SC-011)
- Zero 404 errors, zero console errors

---

## Phase 8: Development Server Final Test (Priority: P3 continued)

**Goal**: Validate development workflow for future content updates

**Independent Test**: Start dev server and verify hot-reload functionality

- [ ] T064 [US3] Start development server: `npm start` from my-website/
- [ ] T065 [US3] Verify server starts within 30 seconds
- [ ] T066 [US3] Verify site loads at `localhost:3000`
- [ ] T067 [US3] Test hot-reload: make small edit to any .md file, save, and verify browser updates automatically
- [ ] T068 [US3] Verify no build warnings in console during development
- [ ] T069 [US3] Stop development server

**Checkpoint**: Development workflow validated

**Acceptance Criteria**:
- Dev server starts within 30 seconds (SC-007)
- Site serves without errors (FR-008)
- Hot-reload functional
- No build warnings

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all content work
- **User Story 4 (Phase 3)**: Depends on Foundational (Phase 2) - Creates directory structure
- **User Story 5 (Phase 4)**: Depends on Phase 3 - Content files need directory to exist
- **User Story 6 (Phase 5)**: Depends on Phase 4 - Validates content from Phase 4
- **Sidebar Config (Phase 6)**: Depends on Phase 4 - Reads frontmatter from content files
- **User Story 3 (Phase 7-8)**: Depends on Phases 4, 5, 6 - Final verification of complete site

### Critical Path

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ──→ Creates Docusaurus structure
    ↓
Phase 3 (US4 - Directory) ──→ Creates my-website/docs/physical-ai/
    ↓
Phase 4 (US5 - Content) ──→ Creates 10 .md files with frontmatter
    ↓                        (Content must exist before sidebar)
Phase 5 (US6 - Validation) ──→ Validates content quality
    ↓
Phase 6 (Sidebar) ──→ Reads frontmatter from Phase 4 files
    ↓                  (Sidebar must be configured before build)
Phase 7-8 (US3 - Verification) ──→ Builds and tests complete site
```

### Parallel Opportunities

**Phase 1 (Setup)**: All 4 verification tasks (T001-T004) can run in parallel

**Phase 4 (Content Creation)**: All 10 file creation tasks (T022-T031) can run in parallel - each creates a different file with no dependencies

**Phase 5 (Formatting Validation)**: Most validation tasks (T036-T040) can run in parallel - different aspects being checked

**Estimated Execution Time per Phase**:
- Phase 1: 5 minutes (environment checks)
- Phase 2: 15-20 minutes (npm install + initial tests)
- Phase 3: 5 minutes (directory cleanup)
- Phase 4: 30-45 minutes (content extraction - 10 files, 15-30 min each if done atomically)
- Phase 5: 10-15 minutes (validation checks)
- Phase 6: 10 minutes (sidebar configuration)
- Phase 7: 15-20 minutes (build + thorough testing)
- Phase 8: 5 minutes (dev server test)

**Total Estimated Time**: 95-120 minutes (1.5-2 hours)

---

## Parallel Example: Phase 4 Content Creation

```bash
# Launch all content file creation tasks together (T022-T031):
Task: "Create introduction.md with frontmatter and content"
Task: "Create quarter-overview.md with frontmatter and content"
Task: "Create why-physical-ai-matters.md with frontmatter and content"
Task: "Create learning-outcomes.md with frontmatter and content"
Task: "Create weekly-breakdown.md with frontmatter and content"
Task: "Create assessments.md with frontmatter and content"
Task: "Create hardware-requirements.md with frontmatter and content"
Task: "Create lab-setup.md with frontmatter and content"
Task: "Create student-kits.md with frontmatter and content"
Task: "Create cloud-lab-options.md with frontmatter and content"
```

These can all run simultaneously because:
- Each task creates a different file
- No dependencies between tasks
- No shared resources being modified

---

## Implementation Strategy

### Recommended Approach (Sequential by Phase)

1. **Complete Phase 1**: Setup → Verify environment ready
2. **Complete Phase 2**: Foundational → Get Docusaurus running
3. **Complete Phase 3**: Directory Structure → Prepare content location
4. **Complete Phase 4**: Content Creation → All 10 files (can parallelize individual file tasks)
5. **Complete Phase 5**: Content Validation → Verify quality
6. **Complete Phase 6**: Sidebar Configuration → Enable navigation
7. **Complete Phase 7**: Build & Test → Verify production readiness
8. **Complete Phase 8**: Dev Server Test → Validate workflow

**Checkpoint Strategy**: Stop after each phase to validate before proceeding. Most critical checkpoints:
- After Phase 2: Verify Docusaurus runs
- After Phase 4: Verify all content files created
- After Phase 7: Verify complete site functional

### Alternative: Parallel Content Creation (Phase 4)

If multiple people or processes available, Phase 4 tasks (T022-T031) can all execute simultaneously, reducing Phase 4 time from 30-45 minutes to ~5 minutes per file (with 10 parallel workers).

---

## Notes

- **[P] marker**: Task can run in parallel with other [P] tasks in same phase
- **[Story] label**: Maps task to specific user story from spec.md (US1, US2, US3, US4, US5, US6)
- **File paths**: All paths are absolute from repository root (`F:\my-ai-book\my-ai-spec-book\`)
- **Content preservation**: Tasks T022-T031 MUST copy content exactly as-is (FR-014, FR-015)
- **Frontmatter format**: All frontmatter must use YAML syntax with triple-dash delimiters (`---`)
- **Commit strategy**: Commit after each phase completion (not individual tasks)
- **Testing**: No automated tests in this feature; all validation is manual verification

---

## Acceptance Checklist

### Functional Requirements Coverage

- [ ] FR-001: Docusaurus initialized with exact command (T005)
- [ ] FR-002: Directory renamed/merged correctly (T007)
- [ ] FR-003: Site title set to "Physical AI & Humanoid Robotics" (T011)
- [ ] FR-004: Deployment placeholders added (T012)
- [ ] FR-005: Content extracted from source file (T022-T031)
- [ ] FR-006: Markdown formatting preserved (T036-T040)
- [ ] FR-007: Build completes successfully (T047)
- [ ] FR-008: Dev server works (T008-T009, T064)
- [ ] FR-009: TypeScript configuration used (T005)
- [ ] FR-010: my-website/docs/physical-ai/ directory created (T019)
- [ ] FR-011: Exactly 10 markdown files created (T022-T031)
- [ ] FR-012: Sidebar configured correctly (T042-T043)
- [ ] FR-013: Frontmatter added to all files (T022-T031)
- [ ] FR-014: No content rewritten (T035, T056)
- [ ] FR-015: All formatting preserved (T036-T040)
- [ ] FR-016: Links remain functional (T038, T057)
- [ ] FR-017: Root redirects to introduction (T013, T052)

### Success Criteria Coverage

- [ ] SC-001: Init within 5 min (T005-T006)
- [ ] SC-002: Title displays correctly (T011, T051)
- [ ] SC-003: Sidebar shows 10 pages (T053)
- [ ] SC-004: Zero 404 errors (T053)
- [ ] SC-005: Build completes <2 min (T061)
- [ ] SC-006: All pages navigable (T053-T055)
- [ ] SC-007: Dev server starts <30s (T065)
- [ ] SC-008: Formatting preserved (T056)
- [ ] SC-009: Zero rewritten content (T035)
- [ ] SC-010: 100% formatting match (T056-T059)
- [ ] SC-011: Links functional (T057)
- [ ] SC-012: Root redirects to intro (T052)

### User Story Coverage

- [ ] US1: Initialize Docusaurus Project (Phase 2, T005-T010)
- [ ] US2: Configure Site Metadata (Phase 2, T011-T016)
- [ ] US3: Verify Complete Site Functionality (Phases 7-8, T046-T069)
- [ ] US4: Create Documentation Section Structure (Phases 3 & 6, T017-T020, T041-T045)
- [ ] US5: Split and Organize Content (Phase 4, T021-T035)
- [ ] US6: Preserve Content Formatting (Phase 5, T036-T040)
