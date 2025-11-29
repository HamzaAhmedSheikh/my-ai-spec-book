<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0
- Modified principles:
  * Principle II: Clarified Agent Framework choice (OpenAI Agents SDK preferred, ChatKit allowed)
  * Principle IV: Added concrete AI-assistance evidence requirements
  * Principle V: Added minimum book content and API contract requirements
  * Principle VII: Expanded with branch strategy and commit format
- Added sections:
  * API Contract Specification (new subsection under Technology Stack)
  * Security & Secrets Management (new subsection)
  * Testing Requirements (new subsection)
  * Book Content Requirements (new subsection)
  * Deployment SLA Standards (new subsection)
  * Agentic Excellence Scoring Rubric (expanded VI)
- Removed sections: N/A
- Templates requiring updates:
  ✅ plan-template.md (Constitution Check updated with new requirements)
  ✅ spec-template.md (Aligned with API contract and testing requirements)
  ✅ tasks-template.md (Aligned with testing phases)
- Follow-up TODOs: None
-->

# Agent-Native Book Challenge Constitution

## Core Principles

### I. Unified Deliverable Mandate

**NON-NEGOTIABLE**: Every submission MUST contain both cores in a single unified repository:

- **Static Core**: A technical book generated via AI/Specifications, built with Docusaurus and deployed to GitHub Pages
- **Dynamic Core**: An embedded RAG agent powered by FastAPI, deployed live, capable of answering questions about the book content

**Rationale**: The hackathon tests the ability to build agent-augmented documentation systems. A static book alone is insufficient; the intelligence layer is mandatory. Both cores must be demonstrated working together.

### II. Technology Stack Compliance

**NON-NEGOTIABLE**: The following technology stack is ratified and MUST be used without substitution:

| Component | Ratified Technology | Constraint |
|-----------|---------------------|------------|
| Book Framework | Docusaurus | Must be static site generated (SSG) |
| Book Hosting | GitHub Pages | Must be publicly accessible via standard URL |
| Chatbot Backend | FastAPI | Must be deployed live (e.g., Render/Railway) to serve requests |
| Agent Logic | OpenAI Agents SDK (preferred) or ChatKit SDK | Orchestration of the RAG flow |
| Vector DB | Qdrant Cloud (Free Tier) | Indexing and retrieval of book content |
| Development | Claude Code (or allowed LLM) | Used for code generation & content writing |
| Planning | Spec-Kit Plus | Source of truth for book structure |

**Rationale**: Standardized tooling ensures fair evaluation, reproducibility, and validates participants' ability to work within real-world constraints where technology choices are often predetermined by architecture or compliance requirements.

### III. Intelligence Fidelity (RAG Standard)

**NON-NEGOTIABLE**: The RAG agent MUST demonstrate two distinct operational modes:

1. **Global Context Mode**: Answer questions using the entire book as knowledge base
2. **Selection Grounding Mode ("Magna Carta" Feature)**: When user highlights/selects specific text in the book UI, the agent MUST answer subsequent questions using strictly that selected text as context

**Disqualification Trigger**: Failure to implement text-selection grounding results in immediate disqualification.

**Rationale**: This tests advanced RAG capabilities—context windowing, precision grounding, and UI-agent integration. Global-only RAG is trivial; selection grounding demonstrates production-grade contextual intelligence.

### IV. Spec-First Workflow (Traceability Principle)

**NON-NEGOTIABLE**: All code and content MUST be traceable to artifacts created with Spec-Kit Plus. The workflow MUST demonstrate:

**Spec → LLM Generation → Docusaurus Output**

**AI-Assistance Evidence Requirements**:
- **Specifications**: At least one feature spec in `specs/<feature>/spec.md` documenting book structure and RAG agent requirements
- **Prompt History Records (PHRs)**: Minimum required PHRs:
  - 1 PHR for constitution creation (stage: `constitution`)
  - 1 PHR for book content specification (stage: `spec`)
  - 1 PHR for RAG agent implementation planning (stage: `plan`)
  - Additional PHRs documenting major content generation sessions
- **Architecture Decision Records (ADRs)**: Minimum required ADRs:
  - ADR documenting embedding model choice and rationale
  - ADR documenting deployment strategy (hosting providers, CI/CD)
  - ADR documenting text-selection grounding implementation approach
- **Git History**: Commits must reference specs/tasks (e.g., `feat: implement global context mode (refs T012)`)

**What Constitutes Manual Authorship (VIOLATION)**:
- Book chapters written directly in Docusaurus without spec → LLM workflow
- Code committed without corresponding tasks or PHRs
- Content edits not traceable to AI-assisted sessions
- Missing specs for major features

**Rationale**: The hackathon validates spec-driven development methodology. Manual authorship bypasses the core challenge: building AI-native development workflows that maintain traceability and architectural discipline.

### V. Mandatory Deliverables (Pass/Fail Gates)

All submissions MUST pass these gates to be considered valid:

- [ ] **Live GitHub Pages URL**: Book must be publicly accessible and functional
  - Minimum 10 pages of substantive technical content (excluding index, navigation)
  - Content must be cohesive (not random disconnected articles)
  - Must include working table of contents and navigation
- [ ] **Live API Endpoint**: Chatbot backend must be deployed and responsive
  - Health check endpoint must return 200 OK
  - Must respond to chat queries within 30 seconds
  - Uptime requirement: 95% during final 48 hours before deadline
- [ ] **Text Selection Grounding**: Magna Carta feature must be functional and demonstrable
  - UI must support text selection (highlight with mouse/touch)
  - API must accept selected text as context parameter
  - Response must reference only the selected text (verifiable by evaluators)
- [ ] **Spec-Kit Artifacts**: Repository must contain valid spec files in `specs/` directory
  - At least 1 complete feature spec with user stories
  - Required PHRs as specified in Principle IV
  - Required ADRs as specified in Principle IV
- [ ] **Required API Endpoints** (see API Contract Specification section):
  - `GET /health` - Health check
  - `POST /chat` - Global context mode
  - `POST /chat/grounded` - Selection grounding mode

**Rationale**: These are non-negotiable table stakes. Missing any gate means the submission is incomplete and cannot be evaluated fairly against compliant entries. Specific minimums prevent gaming the system with trivial implementations.

### VI. Agentic Excellence (Merit Bonus)

Participants earn distinction and bonus consideration for:

**1. Reusable Intelligence (Max 30 points)**

Creating Claude Code Subagents to automate parts of the build process:
- **Tier 1 (10 pts)**: Basic automation agent (e.g., runs build commands, simple deployment scripts)
- **Tier 2 (20 pts)**: Intermediate agent with decision-making (e.g., generates Docusaurus content from specs, indexes content to Qdrant)
- **Tier 3 (30 pts)**: Advanced multi-step agent (e.g., full pipeline automation from spec → content generation → indexing → deployment)

**Evaluation Criteria**:
- Clear documentation in `.specify/agents/` with reuse instructions
- Demonstrable automation (recorded demo or reproducible steps)
- Code quality and error handling

**2. Agent Skills Definition (Max 30 points)**

Defining custom Agent Skills within ChatKit/OpenAI Agents ecosystem:
- **Tier 1 (10 pts)**: Basic skill (e.g., chapter navigation, bookmark management)
- **Tier 2 (20 pts)**: Interactive skill (e.g., code snippet execution, inline tutorials, quiz generation from content)
- **Tier 3 (30 pts)**: Advanced multi-skill orchestration (e.g., adaptive learning paths, context-aware recommendations, multi-turn dialogues)

**Evaluation Criteria**:
- Demonstrates clear value beyond baseline RAG
- Skills are well-documented with examples
- Integration is seamless and enhances user experience

**3. Innovation Bonus (Max 10 points)**

Awarded at evaluator discretion for:
- Novel RAG techniques (hybrid search, re-ranking, query expansion)
- Exceptional UX innovations in text selection or chat interface
- Creative agentic workflows not covered above
- Community contributions (open-source tooling, templates, guides)

**Total Possible Bonus**: 70 points (added to base evaluation score)

**Rationale**: This separates good submissions from excellent ones. Agentic tooling demonstrates mastery of the AI-native development paradigm and creates reusable artifacts for the broader community. The tiered rubric ensures fair, consistent evaluation.

### VII. Repository Standards

**MUST include**:

- **Repository Structure**:
  ```
  ├── docs/                      # Docusaurus content
  │   ├── docs/                  # Book chapters (markdown/MDX)
  │   ├── src/                   # React components for custom features
  │   ├── static/                # Static assets (images, files)
  │   └── docusaurus.config.js   # Docusaurus configuration
  ├── api/                       # FastAPI backend
  │   ├── app/                   # Application code
  │   │   ├── main.py            # FastAPI entry point
  │   │   ├── routers/           # API route handlers
  │   │   ├── services/          # Business logic (RAG, Qdrant)
  │   │   └── models/            # Pydantic models
  │   ├── tests/                 # Backend tests
  │   ├── requirements.txt       # Python dependencies
  │   └── README.md              # Deployment instructions
  ├── specs/                     # Spec-Kit Plus artifacts
  │   └── <feature-name>/
  │       ├── spec.md            # Feature specification
  │       ├── plan.md            # Implementation plan
  │       └── tasks.md           # Task breakdown
  ├── history/
  │   ├── prompts/               # PHRs (organized by stage)
  │   │   ├── constitution/
  │   │   ├── <feature-name>/
  │   │   └── general/
  │   └── adr/                   # ADRs (numbered)
  ├── .specify/                  # SpecKit Plus configuration
  │   ├── memory/
  │   │   └── constitution.md
  │   └── templates/
  ├── README.md                  # Must include "Live Links" section at top
  └── .github/workflows/         # (Optional) CI/CD automation
  ```

- **README Live Links Section** (must be at the very top):
  ```markdown
  # [Project Name]

  ## Live Links
  - **Book**: [GitHub Pages URL]
  - **API**: [FastAPI deployment URL]
  - **API Docs**: [FastAPI deployment URL]/docs
  - **Repository**: [GitHub repo URL]
  ```

- **Branch Strategy**:
  - `main` or `master`: Production-ready code, deployed to GitHub Pages
  - Feature branches: `<issue-number>-<feature-name>` (e.g., `001-book-content`, `002-rag-agent`)
  - All work merged to main via commits (PRs optional but not required for solo projects)

- **Commit Message Format**:
  - Follow Conventional Commits: `<type>(<scope>): <description> (refs <task-id>)`
  - Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
  - Examples:
    - `feat(book): add chapter on RAG fundamentals (refs T015)`
    - `feat(api): implement selection grounding endpoint (refs T023)`
    - `docs(adr): document embedding model choice (refs ADR-001)`
    - `chore(deploy): configure Railway deployment (refs T031)`

**Rationale**: Consistent structure enables rapid evaluation and ensures evaluators can immediately access both live deliverables without hunting through documentation. Clear commit messages provide traceability to specs and tasks.

## Technology Stack Requirements

### Static Core (Book)

- **Framework**: Docusaurus 3.x
- **Hosting**: GitHub Pages
- **Build**: Static Site Generation (SSG)
- **Content Format**: Markdown with MDX support
- **UI Requirements**: Must include text selection capability for Magna Carta feature

### Dynamic Core (RAG Agent)

- **Backend Framework**: FastAPI (Python 3.9+)
- **Agent Framework**: OpenAI Agents SDK or ChatKit SDK
- **Vector Database**: Qdrant Cloud (Free Tier)
- **Embeddings**: OpenAI embeddings (model choice documented in ADR)
- **Deployment**: Live hosting (Render, Railway, or equivalent)
- **API Documentation**: Auto-generated OpenAPI/Swagger docs at `/docs`

### Development Tooling

- **AI Assistant**: Claude Code or approved LLM
- **Planning Framework**: Spec-Kit Plus
- **Version Control**: Git with meaningful commit messages
- **Documentation**: PHRs for all AI interactions, ADRs for architectural decisions

## Quality Gates

### Constitution Check (Pre-Implementation)

Before Phase 0 research, verify:

- [ ] Technology stack matches ratified components (no substitutions)
- [ ] Repository structure follows prescribed layout
- [ ] Spec-Kit Plus is configured and operational
- [ ] `.specify/memory/constitution.md` exists and is accurate

Re-check after Phase 1 design:

- [ ] Both cores (Static + Dynamic) are in scope
- [ ] Magna Carta feature is designed and feasible
- [ ] Live deployment strategy is documented
- [ ] All mandatory deliverables are planned

### Pre-Submission Validation

Before submitting, verify:

- [ ] GitHub Pages site loads and is navigable
- [ ] FastAPI endpoint responds to health checks
- [ ] Text selection in UI triggers context-grounded responses
- [ ] README contains valid Live Links at the top
- [ ] `specs/` directory contains at least one complete spec
- [ ] At least 3 PHRs documenting AI-assisted development
- [ ] At least 1 ADR documenting a significant technical decision

### Agentic Excellence Validation (Optional)

For bonus consideration:

- [ ] Custom Claude Code Subagent is documented in `.specify/agents/`
- [ ] ChatKit Skills are defined and functional
- [ ] Reuse instructions are clear and testable
- [ ] Skills demonstrate clear value beyond baseline RAG

## Governance

### Authority

This constitution supersedes all other development practices for the duration of the hackathon. Participants may not:

- Substitute technology stack components
- Omit mandatory deliverables
- Skip spec-driven workflow
- Submit without live deployments

### Amendments

This constitution is fixed for the hackathon. No amendments are permitted after ratification to ensure fair and consistent evaluation criteria for all participants.

### Compliance Review

All submissions will be verified against:

1. **Technology Compliance**: Automated checks for required dependencies
2. **Deliverable Validation**: Manual verification of live links and functionality
3. **Spec Traceability**: Review of `specs/` and `history/` directories
4. **Quality Gates**: Checklist verification of mandatory requirements

### Complexity Justification

If a submission requires deviation from this constitution (e.g., additional technology not listed, alternative architecture), the participant MUST:

1. Document the deviation in an ADR
2. Provide clear rationale for why the constitution's approach is insufficient
3. Demonstrate that simpler alternatives were considered and rejected
4. Accept that deviations may result in disqualification at evaluator discretion

### Version Management

**Version**: 1.0.0
**Ratified**: 2025-11-29
**Last Amended**: 2025-11-29

**Version History**:
- **1.0.0** (2025-11-29): Initial constitution ratified for Agent-Native Book Challenge hackathon

**Versioning Policy**:
- **MAJOR**: Backward incompatible changes (e.g., technology stack changes, removal of mandatory requirements)
- **MINOR**: New requirements added or materially expanded guidance
- **PATCH**: Clarifications, wording fixes, non-semantic refinements
