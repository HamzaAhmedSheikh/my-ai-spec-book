# Agent-Native Book Challenge

This project is an **Agent-Native Book Challenge** following Spec-Driven Development (SDD) methodology. The primary goal is to create a technical book with Docusaurus (static core) and an embedded RAG agent with FastAPI (dynamic core), both delivered as a unified repository.

## Key Architecture
- **Static Core**: Docusaurus site deployed to GitHub Pages
- **Dynamic Core**: FastAPI RAG agent with Qdrant vector DB, supporting global context and text-selection grounding ("Magna Carta" feature)
- **Development Framework**: Spec-Kit Plus for traceability (specs → AI generation → implementation)

## Development Commands

### Spec-Driven Development Workflow

The project follows a strict spec-first workflow using slash commands:

1.  **Create Feature Specification**
    ```bash
    /sp.specify <feature description>
    ```
    -   Generates feature spec in `specs/<feature-number>-<short-name>/spec.md`
    -   Creates new git branch `<number>-<short-name>`
    -   Validates spec quality with automated checklist

2.  **Clarify Specification** (optional)
    ```bash
    /sp.clarify
    ```
    -   Identifies underspecified areas in the current spec
    -   Asks up to 5 targeted clarification questions
    -   Updates spec with answers

3.  **Generate Implementation Plan**
    ```bash
    /sp.plan
    ```
    -   Creates `plan.md` with technical architecture
    -   Generates research.md, data-model.md, contracts/, quickstart.md
    -   Validates against constitution requirements

4.  **Generate Task List**
    ```bash
    /sp.tasks
    ```
    -   Creates dependency-ordered `tasks.md`
    -   Organizes tasks by user story for independent implementation
    -   Includes parallelization markers [P] for concurrent execution

5.  **Execute Implementation**
    ```bash
    /sp.implement
    ```
    -   Executes all tasks from tasks.md in dependency order
    -   Checks checklists before starting
    -   Marks tasks complete as they finish

6.  **Commit & Create PR**
    ```bash
    /sp.git.commit_pr
    ```
    -   Autonomous git workflow agent
    -   Analyzes changes and generates meaningful commit messages
    -   Creates feature branch and PR with intelligent descriptions

7.  **Document Architecture Decisions**
    ```bash
    /sp.adr <decision-title>
    ```
    -   Creates Architecture Decision Record in `history/adr/`
    -   Documents rationale and tradeoffs

8.  **Generate Feature Checklist**
    ```bash
    /sp.checklist
    ```
    -   Creates custom checklist for current feature

9.  **Analyze Cross-Artifact Consistency**
    ```bash
    /sp.analyze
    ```
    -   Validates consistency across spec.md, plan.md, tasks.md
    -   Non-destructive quality analysis

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
-   Creates or updates constitution from interactive inputs
-   Keeps dependent templates in sync

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

## Mandatory Deliverables (from Constitution)

The project MUST deliver:

1.  **Live GitHub Pages URL**: Docusaurus site with 10+ substantive pages
2.  **Live API Endpoint**: FastAPI backend with health check and chat endpoints
3.  **Text Selection Grounding**: "Magna Carta" feature for context-aware responses
4.  **Spec-Kit Artifacts**: Complete specs, PHRs, and ADRs demonstrating AI-assisted development
5.  **Required API Endpoints**:
    -   `GET /health` - Health check
    -   `POST /chat` - Global context mode
    -   `POST /chat/grounded` - Selection grounding mode

## Technology Stack (Non-Negotiable)

-   **Book**: Docusaurus 3.x → GitHub Pages
-   **API**: FastAPI (Python 3.9+) → Render/Railway
-   **Agent**: OpenAI Agents SDK (preferred) or ChatKit
-   **Vector DB**: Qdrant Cloud (Free Tier)
-   **Development**: Claude Code + Spec-Kit Plus

See `.specify/memory/constitution.md` for complete requirements.

## Core Agent Behavior

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

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
    "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.
