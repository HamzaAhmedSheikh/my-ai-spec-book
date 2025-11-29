---
id: 0001
title: Initial hackathon constitution
stage: constitution
date: 2025-11-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution", "hackathon", "setup", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

Hackathon Constitution: The Agent-Native Book Challenge



Article I. The Unified Mandate

One Project, Two Cores. Participants must submit a single, unified repository containing both:

- The Static Core: A technical book generated via AI/Specs.

- The Dynamic Core: An embedded RAG agent capable of answering questions about the book.



Article II. Technology Ratification

Submissions are only valid if they utilize the following ratified technology stack. No substitutions allowed for core components.



Component              | Ratified Tech                     | Constraint

---------------------- | ----------------------------------|----------------------------------------------

Book Framework         | Docusaurus                        | Must be static site generated (SSG).

Book Hosting           | GitHub Pages                      | Must be publicly accessible via standard URL.

Chatbot Backend        | FastAPI                           | Must be deployed live (e.g., Render/Railway) to serve requests.

Agent Logic            | OpenAI Agents / ChatKit SDK       | Orchestration of the RAG flow.

Vector DB              | Qdrant Cloud (Free Tier)          | Indexing and retrieval of book content.

Development            | Claude Code (or allowed LLM)      | Used for code generation & content writing.

Planning               | Spec-Kit Plus                     | Source of truth for book structure.



Article III. The RAG Standard (Retrieval-Augmented Generation)

The integrated chatbot must demonstrate "Intelligence Fidelity" through two distinct modes:

- Global Context Mode: The agent must answer questions using the entire book as its knowledge base.

- Selection Grounding Mode (The "Magna Carta" Feature): If a user highlights/selects specific text in the book UI, the agent must answer the subsequent question using strictly that selected text as the context.

Failure to implement text-selection grounding results in disqualification.



Article IV. The Spec-First Workflow

Traceability Principle: The final code and content must be traceable to artifacts created with Spec-Kit Plus. The workflow must demonstrate:

Spec → LLM Generation → Docusaurus Output.

Projects where the book is written manually without AI/Spec assistance violate the spirit of the constitution.



Article V. Success Criteria & Scoring

Section A: Mandatory Requirements (Pass/Fail)

[ ] Live GitHub Pages URL (Book).

[ ] Live API Endpoint (Chatbot).

[ ] Text Selection Grounding feature is functional.

[ ] Repository contains Spec-Kit artifacts.



Section B: The "Agentic" Bonus (Merit)

Participants earn distinction/bonus marks for:

- Reusable Intelligence: Creating Claude Code Subagents to automate parts of the build process.

- Skill Definition: Defining custom Agent Skills within the ChatKit ecosystem that allow the bot to perform specific actions beyond simple text retrieval (e.g., running code snippets found in the book).



Article VI. Submission Protocol

- Repository: One public GitHub repo containing docs/ (content), api/ (FastAPI), and specs/ (Spec-Kit).

- Readme: Must include the "Live Links" section at the very top.

## Response snapshot

Created the initial constitution for the Agent-Native Book Challenge hackathon. The constitution defines 7 core principles:

I. Unified Deliverable Mandate - Both static book (Docusaurus) and dynamic RAG agent (FastAPI) required
II. Technology Stack Compliance - Fixed technology stack (no substitutions allowed)
III. Intelligence Fidelity (RAG Standard) - Global context mode + Selection grounding mode (Magna Carta feature)
IV. Spec-First Workflow - Full traceability from Spec → LLM → Output required
V. Mandatory Deliverables - 4 pass/fail gates defined
VI. Agentic Excellence - Bonus merit for custom subagents and skills
VII. Repository Standards - Prescribed directory structure and README format

The constitution also includes detailed sections for:
- Technology Stack Requirements (Static Core, Dynamic Core, Development Tooling)
- Quality Gates (Constitution Check, Pre-Submission Validation, Agentic Excellence Validation)
- Governance (Authority, Amendments policy, Compliance Review, Complexity Justification, Version Management)

Version 1.0.0 ratified on 2025-11-29. No placeholders remaining - all fields have been filled with concrete values. Sync Impact Report included in HTML comment at top of file documenting this is the initial version.

## Outcome

- ✅ Impact: Created comprehensive hackathon constitution defining all mandatory requirements, technology stack, quality gates, and governance rules for the Agent-Native Book Challenge
- 🧪 Tests: N/A (constitution document)
- 📁 Files: Created/updated `.specify/memory/constitution.md` with complete constitution (no placeholders remaining)
- 🔁 Next prompts: User may want to proceed with `/sp.specify` to create feature specifications, or `/sp.plan` to begin planning the implementation of the book + RAG agent system
- 🧠 Reflection: Constitution successfully captures all hackathon requirements in structured, testable format. The 7 principles provide clear non-negotiable rules (I-V) and merit opportunities (VI-VII). Quality gates provide concrete checklists for validation at different phases.

## Evaluation notes (flywheel)

- Failure modes observed: None - all template placeholders successfully replaced with concrete values
- Graders run and results (PASS/FAIL): Manual validation PASS - no bracketed placeholders remain, all sections populated, version/date formatting correct
- Prompt variant (if applicable): N/A (initial constitution)
- Next experiment (smallest change to try): N/A - constitution is fixed for hackathon duration per governance rules
