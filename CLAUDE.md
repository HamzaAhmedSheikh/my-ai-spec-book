# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Agent-Native Book Challenge** project following Spec-Driven Development (SDD) methodology. The goal is to create a technical book with Docusaurus (static core) and an embedded RAG agent with FastAPI (dynamic core), both delivered as a unified repository.

### Key Architecture
- **Static Core**: Docusaurus site deployed to GitHub Pages
- **Dynamic Core**: FastAPI RAG agent with Qdrant vector DB, supporting global context and text-selection grounding ("Magna Carta" feature)
- **Development Framework**: Spec-Kit Plus for traceability (specs → AI generation → implementation)

## Development Commands

### Spec-Driven Development Workflow

The project follows a strict spec-first workflow using slash commands:

1. **Create Feature Specification**
   ```bash
   /sp.specify <feature description>
   ```
   - Generates feature spec in `specs/<feature-number>-<short-name>/spec.md`
   - Creates new git branch `<number>-<short-name>`
   - Validates spec quality with automated checklist

2. **Clarify Specification** (optional)
   ```bash
   /sp.clarify
   ```
   - Identifies underspecified areas in the current spec
   - Asks up to 5 targeted clarification questions
   - Updates spec with answers

3. **Generate Implementation Plan**
   ```bash
   /sp.plan
   ```
   - Creates `plan.md` with technical architecture
   - Generates research.md, data-model.md, contracts/, quickstart.md
   - Validates against constitution requirements

4. **Generate Task List**
   ```bash
   /sp.tasks
   ```
   - Creates dependency-ordered `tasks.md`
   - Organizes tasks by user story for independent implementation
   - Includes parallelization markers [P] for concurrent execution

5. **Execute Implementation**
   ```bash
   /sp.implement
   ```
   - Executes all tasks from tasks.md in dependency order
   - Checks checklists before starting
   - Marks tasks complete as they finish

6. **Commit & Create PR**
   ```bash
   /sp.git.commit_pr
   ```
   - Autonomous git workflow agent
   - Analyzes changes and generates meaningful commit messages
   - Creates feature branch and PR with intelligent descriptions

7. **Document Architecture Decisions**
   ```bash
   /sp.adr <decision-title>
   ```
   - Creates Architecture Decision Record in `history/adr/`
   - Documents rationale and tradeoffs

8. **Generate Feature Checklist**
   ```bash
   /sp.checklist
   ```
   - Creates custom checklist for current feature

9. **Analyze Cross-Artifact Consistency**
   ```bash
   /sp.analyze
   ```
   - Validates consistency across spec.md, plan.md, tasks.md
   - Non-destructive quality analysis

### Constitution Management

**View/Edit Project Principles**
```bash
# Constitution is at:
.specify/memory/constitution.md
```

**Update Constitution**
```bash
/sp.constitution
```
- Creates or updates constitution from interactive inputs
- Keeps dependent templates in sync

## Repository Structure

```
├── docs/                          # Docusaurus content (if implemented)
│   ├── docs/                      # Book chapters (markdown/MDX)
│   ├── src/                       # React components
│   ├── static/                    # Static assets
│   └── docusaurus.config.js
├── api/                           # FastAPI backend (if implemented)
│   ├── app/
│   │   ├── main.py                # FastAPI entry point
│   │   ├── routers/               # API routes
│   │   ├── services/              # RAG, Qdrant integration
│   │   └── models/                # Pydantic models
│   ├── tests/
│   └── requirements.txt
├── specs/                         # Feature specifications
│   └── <feature-number>-<name>/
│       ├── spec.md                # Requirements (business-focused, no tech details)
│       ├── plan.md                # Technical architecture
│       ├── tasks.md               # Implementation tasks
│       ├── checklists/            # Quality validation checklists
│       ├── research.md            # Technical decisions
│       ├── data-model.md          # Entity definitions
│       ├── contracts/             # API contracts
│       └── quickstart.md          # Integration scenarios
├── history/
│   ├── prompts/                   # Prompt History Records (PHRs)
│   │   ├── constitution/
│   │   ├── <feature-name>/
│   │   └── general/
│   └── adr/                       # Architecture Decision Records
├── .specify/                      # Spec-Kit Plus framework
│   ├── memory/
│   │   └── constitution.md        # Project principles
│   ├── templates/                 # Spec, plan, task templates
│   └── scripts/bash/              # Automation scripts
└── .claude/
    └── commands/                  # Slash command definitions
```

## Helper Scripts

The `.specify/scripts/bash/` directory contains automation scripts:

- **`create-new-feature.sh`**: Creates feature branch and initializes spec
- **`create-phr.sh`**: Creates Prompt History Record
- **`create-adr.sh`**: Creates Architecture Decision Record
- **`setup-plan.sh`**: Initializes planning artifacts
- **`check-prerequisites.sh`**: Validates feature readiness
- **`update-agent-context.sh`**: Updates agent context files
- **`common.sh`**: Shared utilities

These are typically called by slash commands, not directly.

## Mandatory Deliverables (from Constitution)

The project MUST deliver:

1. **Live GitHub Pages URL**: Docusaurus site with 10+ substantive pages
2. **Live API Endpoint**: FastAPI backend with health check and chat endpoints
3. **Text Selection Grounding**: "Magna Carta" feature for context-aware responses
4. **Spec-Kit Artifacts**: Complete specs, PHRs, and ADRs demonstrating AI-assisted development
5. **Required API Endpoints**:
   - `GET /health` - Health check
   - `POST /chat` - Global context mode
   - `POST /chat/grounded` - Selection grounding mode

## Technology Stack (Non-Negotiable)

- **Book**: Docusaurus 3.x → GitHub Pages
- **API**: FastAPI (Python 3.9+) → Render/Railway
- **Agent**: OpenAI Agents SDK (preferred) or ChatKit
- **Vector DB**: Qdrant Cloud (Free Tier)
- **Development**: Claude Code + Spec-Kit Plus

See `.specify/memory/constitution.md` for complete requirements.

## Key Principles

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architect to build products.

## Quick Reference

### Current Branch Strategy
- `main`/`master`: Production-ready code
- Feature branches: `<number>-<short-name>` (e.g., `001-docusaurus-setup`)
- All specs in: `specs/<number>-<short-name>/`
- All PHRs in: `history/prompts/<constitution|feature-name|general>/`

### Commit Message Format
Follow Conventional Commits:
```
<type>(<scope>): <description> (refs <task-id>)

Types: feat, fix, docs, refactor, test, chore
Examples:
  feat(book): add RAG fundamentals chapter (refs T015)
  feat(api): implement selection grounding (refs T023)
  docs(adr): document embedding model choice (refs ADR-001)
```

### PHR (Prompt History Record) Creation

PHRs are **MANDATORY** after completing any user request. They document AI-assisted development sessions.

**When to create**: Implementation work, planning, debugging, spec/task creation, multi-step workflows

**Stages**: `constitution` | `spec` | `plan` | `tasks` | `red` | `green` | `refactor` | `explainer` | `misc` | `general`

**Routing** (automatic):
- Constitution stage → `history/prompts/constitution/`
- Feature stages (spec, plan, tasks, etc.) → `history/prompts/<feature-name>/`
- General stage → `history/prompts/general/`

**Process**: Most slash commands auto-create PHRs. For manual creation, use agent-native tools or fallback to `.specify/scripts/bash/create-phr.sh`.

### ADR (Architecture Decision Record) Suggestions

When you identify architecturally significant decisions during `/sp.plan` or `/sp.tasks`, suggest:

```
📋 Architectural decision detected: <brief description>
   Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`
```

**Criteria for significance** (ALL must be true):
- **Impact**: Long-term consequences (framework, data model, API, security, platform)
- **Alternatives**: Multiple viable options considered
- **Scope**: Cross-cutting, influences system design

Wait for user consent; **never auto-create ADRs**.

---

## Core Agent Behavior

### Task Context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.

## Active Technologies
- TypeScript 5.6+ (frontend), Python 3.11+ (backend) (005-ui-ux-rag-phase2)
- Python 3.11+ + FastAPI 0.104+, uvicorn 0.24+, fastembed 0.2+, qdrant-client 1.7+, openai 1.3+, python-frontmatter 1.0+, tiktoken 0.5+, pydantic 2.5+ (006-uv-rag-backend)
- Qdrant Cloud Free Tier (vector database, 1GB limit), Environment variables (.env file for configuration) (006-uv-rag-backend)

## Recent Changes
- 005-ui-ux-rag-phase2: Added TypeScript 5.6+ (frontend), Python 3.11+ (backend)
