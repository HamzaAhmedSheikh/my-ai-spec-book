<!--
Sync Impact Report
==================
Version Change: 1.0 → 1.0.1
Bump Type: PATCH (metadata updates, clarity improvements, no principle changes)
Date: 2025-11-30

Modified Principles: None (all principles remain unchanged)
Added Sections: Sync Impact Report (this comment)
Removed Sections: None

Templates Status:
✅ .specify/templates/spec-template.md - Reviewed, aligned with Phase-Driven Architecture
✅ .specify/templates/plan-template.md - Reviewed, Constitution Check section aligns with all principles
✅ .specify/templates/tasks-template.md - Reviewed, task organization aligns with Quality-First and Simplicity principles
✅ .claude/commands/*.md - Reviewed, no Claude-specific naming issues found

Follow-up TODOs: None
-->

# Physical AI & Humanoid Robotics Textbook — Hackathon Constitution

**Project**: Create a complete AI-native textbook for teaching Physical AI & Humanoid Robotics using Claude Code + Spec-Kit Plus
**Deadline**: November 30, 2025, 6:00 PM (UTC)
**Evaluation**: 100 base points + 200 bonus points (Auth, Personalization, Translation, Subagents)
**Submission**: https://forms.gle/CQsSEGM3GeCrL43c8

---

## 🎯 Core Principles

### I. Phase-Driven Architecture
The project is split into **two distinct phases** to prevent scope creep and enable iterative delivery:

- **PHASE 1 (Book Only)**: Docusaurus site with 42 chapters, MDX pages, diagrams, quizzes, exercises. Deploy to GitHub Pages.
- **PHASE 2 (RAG + Features)**: FastAPI backend, Qdrant vectors, Neon DB, Better-Auth, personalization, Urdu translation, subagents.

**Rule**: Complete Phase 1 first (100 points). Phase 2 features are optional bonus (up to 200 bonus points).

### II. Spec-Driven Development (SDD)
Every deliverable (chapter, feature, API) MUST start with a **spec**.

- **Chapter Spec Format**: `specs/chapters/<module>/<chapter-id>.spec.md`
- **Feature Spec Format**: `specs/features/<feature-name>/spec.md`
- **Process**: Spec → Plan → Tasks → Code → Tests → Verify

All specs MUST include:
- **id**: Unique identifier (e.g., `ch-1-01-intro`)
- **title**: Human-readable chapter/feature name
- **description**: 2-3 sentence summary
- **acceptance_criteria**: Checklist of deliverables
- **resources**: Links to referenced materials

**Rationale**: Spec-first approach ensures clarity before code, prevents scope drift, and maintains traceability from requirements to implementation.

### III. Docusaurus-First (Phase 1)
The book is the **primary deliverable**. All content MUST live as MDX files in `/book/docs/`.

- **Folder Structure**:
  ```
  book/
  ├── docs/
  │   ├── intro/           (5 chapters)
  │   ├── module-1-ros2/   (8 chapters)
  │   ├── module-2-gazebo/ (7 chapters)
  │   ├── module-3-isaac/  (7 chapters)
  │   ├── module-4-vla/    (5 chapters)
  │   ├── hardware/        (4 chapters)
  │   ├── capstone/        (5 chapters)
  │   └── glossary/        (2 chapters)
  ├── docusaurus.config.js
  ├── sidebars.js
  └── static/
  ```

- **MDX Standards**:
  - All chapters MUST include: Intro + Summary, Practical Exercise, Quiz, Downloadable Resources
  - Diagrams MUST use **Mermaid** (`mermaid` code blocks)
  - Code examples MUST be **real** (ROS2, Gazebo, Isaac, Python)
  - Beginner-friendly language (no jargon without explanation)
  - Frontmatter with metadata: `title`, `sidebar_position`, `description`

- **Build & Deploy**:
  - Build: `npm run build` → generates `/build/` static files
  - Deploy: Push to GitHub → GitHub Actions → GitHub Pages
  - Verification: Site live at `https://<username>.github.io/<repo>/`

**Rationale**: Focusing on book delivery first ensures the core deliverable (100 points) is complete before pursuing bonus features.

### IV. Quality-First (Testing)
Every code example MUST be **runnable and tested**.

- **Code Quality Gates**:
  - Python code: `pylint`, `black`, type hints required
  - JavaScript/React: `eslint`, `prettier`
  - MDX: No broken links, proper frontmatter
  - Build MUST pass: `npm run build` succeeds without errors

- **Testing Strategy**:
  - Chapter code blocks: Run via `npm run test:code` (extracts + runs examples)
  - RAG backend (Phase 2): FastAPI tests with `pytest`
  - Integration: E2E tests for chatbot queries

**Rationale**: Quality gates prevent technical debt accumulation and ensure all examples are accurate and functional.

### V. Security (Non-Negotiable)
Secrets, API keys, and credentials **MUST NEVER** appear in code.

- **`.env` Files**: All secrets in `.env.local` (gitignored)
- **Secrets Managed**:
  - OpenAI API key
  - Neon Database URL
  - Qdrant API key
  - Better-Auth secrets
- **Documentation**: `.env.example` shows required keys without values
- **Deployment**: GitHub Secrets for CI/CD

**Rationale**: Security breaches can disqualify submissions and expose sensitive credentials. Zero tolerance for secrets in code.

### VI. Simplicity Over Perfection
Start with **minimum viable product** (MVP) for each phase.

- **PHASE 1 MVP**: 42 chapters in Docusaurus, deployed to GitHub Pages
- **PHASE 2 MVP**: Basic RAG chatbot (ask questions about book content)
- **Bonus MVP**: Auth → Personalization → Translation → Subagents (in priority order)

No premature optimization. Refactor only after Phase 1 is live.

**Rationale**: MVP-first approach ensures deliverables meet requirements without over-engineering. Ship first, optimize later.

---

## 📚 Chapter Inventory (42 Total)

### INTRO (5 chapters)
1. What is Physical AI?
2. Embodied Intelligence: From Digital to Physical
3. Why Humanoid Robotics?
4. The Four Pillars of the Course
5. How to Use This Book

### MODULE 1: ROS 2 (8 chapters)
6. ROS 2 Architecture Overview
7. Nodes, Topics, and Services
8. ROS 2 Actions
9. Building ROS 2 Packages
10. Launch Files & Parameters
11. URDF Basics (Robot Description)
12. Building a Humanoid URDF
13. Connecting Python Agents to ROS 2 (rclpy)

### MODULE 2: GAZEBO & DIGITAL TWIN (7 chapters)
14. Introduction to Gazebo
15. URDF vs SDF
16. Working with Sensors (LiDAR, Depth, IMU)
17. Physics Simulation & Environments
18. Unity for Robotics Visualization
19. Building a Digital Twin of a Humanoid
20. Gazebo + ROS 2 Integration

### MODULE 3: NVIDIA ISAAC (7 chapters)
21. What is NVIDIA Isaac?
22. Isaac Sim Setup & Basics
23. Synthetic Data & Photorealism
24. Isaac ROS: VSLAM & Perception
25. Nav2 and Path Planning
26. Bipedal Locomotion in Isaac
27. Sim-to-Real Transfer

### MODULE 4: VISION-LANGUAGE-ACTION (5 chapters)
28. Voice-to-Action: Using Whisper
29. LLMs for Robotics
30. Gesture & Vision Interaction
31. Natural Language → ROS 2 Action Plans
32. Full VLA Pipeline

### HARDWARE (4 chapters)
33. Workstation Requirements
34. Jetson Edge AI Kits
35. Sensors (RealSense, LiDAR, IMU)
36. Humanoid Options (Go2, G1, OP3)

### CAPSTONE PROJECT (5 chapters)
37. Project Overview
38. Designing the Pipeline
39. Implementing the Robot
40. Testing & Evaluation
41. Final Submission Guidelines

### GLOSSARY (2 chapters)
42. Glossary of Terms
43. Robotics Acronyms Index

---

## 🛠️ Technology Stack (Fixed)

### Phase 1: Book (100 points)
- **Node.js**: v18+ (LTS)
- **Docusaurus**: v3.x (React-based static site generator)
- **MDX**: Latest (React in Markdown)
- **Mermaid**: v10+ (diagrams)
- **GitHub**: Repository + GitHub Pages
- **Deployment**: GitHub Actions (build → deploy)

### Phase 2: RAG + Features (0-200 bonus points)
- **Backend**: FastAPI (Python 3.11+)
- **Database**: Neon Serverless Postgres (free tier)
- **Vector Store**: Qdrant Cloud (free tier)
- **LLM Integration**: OpenAI API (GPT-4o or GPT-4 Turbo)
- **Auth**: Better-Auth (signup/signin)
- **Frontend**: React components embedded in Docusaurus
- **Language Translation**: Google Translate API or Hugging Face

### Dependency Versions (Locked)
```json
{
  "dependencies": {
    "docusaurus-core": "^3.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0"
  }
}
```

---

## 📋 Submission Requirements (Acceptance Criteria)

### PHASE 1 DELIVERABLES (100 points - required)
- [ ] **GitHub Repository**: Public repo with all code (book + backend structure)
- [ ] **Docusaurus Site**: 42 chapters across 8 folders, live on GitHub Pages
- [ ] **Chapter Quality**: Each chapter has:
  - Intro + summary
  - At least 1 diagram (Mermaid)
  - At least 2 code examples (real, runnable)
  - Practical exercise
  - Quiz (3-5 questions)
  - Downloadable resources (if applicable)
- [ ] **Build Success**: `npm run build` completes without errors
- [ ] **Deployment**: Site accessible at public GitHub Pages URL
- [ ] **Responsive Design**: Works on desktop + mobile
- [ ] **Navigation**: Sidebar works, internal links correct

### PHASE 2 OPTIONAL FEATURES (0-200 bonus points)

#### Feature: RAG Chatbot Backend (50 bonus points)
- [ ] FastAPI server running (`/chat` endpoint)
- [ ] Vector embeddings stored in Qdrant
- [ ] Queries retrieve relevant chapters (context window ~4K tokens)
- [ ] Chatbot answers questions about book content
- [ ] "Ask about selection" feature: User highlights text, chatbot answers only about that section

#### Feature: Better-Auth (50 bonus points)
- [ ] Signup form collects: name, email, software background, hardware background
- [ ] Signin/Signout functionality
- [ ] User profile page
- [ ] Authentication persists across sessions

#### Feature: Content Personalization (50 bonus points)
- [ ] "Personalize This Chapter" button at chapter start
- [ ] Backend generates personalized summary based on user background
- [ ] Uses LLM + user metadata (collected at signup)
- [ ] Result displayed in modal or sidebar

#### Feature: Urdu Translation (50 bonus points)
- [ ] "Translate to Urdu" button in chapter header
- [ ] Translates chapter title + section headings (not full content initially)
- [ ] Uses Google Translate API or Hugging Face
- [ ] Toggle between English/Urdu

#### Feature: Claude Code Subagents (50 bonus points)
- [ ] Define at least 2 reusable agent skills:
  - **Skill 1**: `code-extractor` (extracts code from chapters, validates syntax)
  - **Skill 2**: `diagram-generator` (generates Mermaid diagrams from descriptions)
- [ ] Subagents used in book generation (e.g., auto-generate chapter code from specs)

---

## 🔄 Development Workflow

### Claude Code Role
1. **Spec Reading**: Parse spec file → extract requirements
2. **Code Generation**: Create chapter MDX, backend endpoints, React components
3. **Testing**: Run build, validate links, test code examples
4. **Verification**: Confirm against acceptance criteria

### Human Role (You)
1. **Content Review**: Read generated chapters, verify accuracy
2. **Architecture Decisions**: Approve folder structure, design choices
3. **Bonus Feature Prioritization**: Decide which Phase 2 features to tackle
4. **Deployment**: Push to GitHub, verify GitHub Pages
5. **Demo Recording**: Create <90 sec video showcasing book + any Phase 2 features

### Escalation Rules
Claude Code MUST ask you if:
- Adding new dependencies (may cause conflicts)
- Changing folder structure (affects specs)
- Removing chapters (scope change)
- Using external services not pre-approved (API costs)

---

## 🚀 Deployment Pipeline

### Phase 1: Book Deployment
1. **Local Build**: `npm run build` → verify `/build/` generated
2. **Push to GitHub**: Commit + push to main branch
3. **GitHub Actions**: Auto-triggers (must be configured)
4. **GitHub Pages**: Deployed to `https://<org>.github.io/<repo>/`
5. **Verification**: All 42 chapters accessible, no 404s

### Phase 2: Backend Deployment (if attempting bonus)
- **FastAPI**: Deployed to Render.com or Railway (free tier)
- **Database**: Neon Serverless (free tier, auto-scales)
- **Vector Store**: Qdrant Cloud (free tier, 1GB limit)
- **Frontend Integration**: Embedded React components in Docusaurus

---

## 📊 Scoring Breakdown

| **Criteria** | **Points** | **Verification** |
|---|---|---|
| Phase 1: Book deployed + 42 chapters live | 100 | GitHub Pages URL accessible |
| RAG Chatbot (Phase 2) | 50 | API responds to queries |
| Better-Auth Integration | 50 | Signup/signin form works |
| Content Personalization | 50 | "Personalize" button returns customized content |
| Urdu Translation | 50 | "Translate" button switches language |
| Subagents/Agent Skills | 50 | Reusable skills documented in code |
| **TOTAL** | **400** | Must submit all links by Nov 30, 6 PM |

---

## 📝 Submission Checklist

Before submitting via https://forms.gle/CQsSEGM3GeCrL43c8, verify:

- [ ] **GitHub Repo**: Public, contains all code (book + backend if Phase 2)
- [ ] **Book URL**: GitHub Pages link, all 42 chapters live
- [ ] **Demo Video**: <90 seconds, shows book navigation + any Phase 2 features
- [ ] **Video Host**: YouTube, Loom, or NotebookLM (ensure accessible)
- [ ] **Code Quality**: `npm run build` succeeds, no linting errors
- [ ] **Responsive**: Tested on mobile + desktop
- [ ] **Glossary Complete**: All robotics terms defined
- [ ] **README.md**: Instructions to run locally + deploy
- [ ] **WhatsApp Number**: For live presentation invitation (top submissions only)

---

## 🛡️ Governance

### Constitution Compliance
- All pull requests MUST reference a spec: `Implements spec/chapters/module-1-ros2/ch-1-01.spec.md`
- All code MUST follow coding standards (linting, formatting, type hints)
- No secrets in code or commits
- All external dependencies vetted before merge

### Amendment Process
- Propose amendment with justification
- Update constitution version + date
- Notify team via commit message
- Re-verify all in-progress work against new rules

### Versioning Policy
- **MAJOR**: Backward incompatible governance/principle removals or redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

---

**Version**: 1.0.1
**Ratified**: 2025-11-29
**Last Amended**: 2025-11-30
**Status**: Active
**Deadline**: 2025-11-30 06:00 PM UTC
