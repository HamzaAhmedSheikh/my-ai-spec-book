---
id: 0002
title: Update project constitution
stage: constitution
date: 2025-11-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 001-docusaurus-setup
user: user
command: /sp.constitution
labels: ["constitution", "update"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests: null
---

## Prompt

```
/sp.constitution

# INSTRUCTION: Update the constitution file; do not overwrite previous instructions or rules.

# PROJECT: Integrated RAG Chatbot (Book Companion)

## 1. Core Principles

*   **Source Truth:** The chatbot is an expert on *this book only*. It must not use outside knowledge unless explicitly asked.

*   **Context Awareness:** Answers must dynamically adapt to user-selected text (highlighted context) vs. general queries.

*   **Resource Efficiency:** Architecture must fit within Qdrant Cloud Free Tier and optimize OpenAI token usage.



## 2. Global Tech Stack Standards

*   **Backend:** Python 3.10+ with **FastAPI**.

*   **AI Engine:** **OpenAI Agents/ChatKit SDKs**.

*   **Vector DB:** **Qdrant Cloud (Free Tier)**.

*   **Code Style:** PEP 8 compliance; Strict type hinting (required for FastAPI Pydantic models).



## 3. Implementation Rules (Immutable)

*   **RAG Boundary:** All answers must include a reference/citation to the book content used.

*   **Selection Feature:** The API must accept an optional `selected_text` parameter to prioritize specific context in generation.

*   **Error Handling:** Graceful fallbacks if Qdrant limits are hit or OpenAI API times out.

*   **Security:** API keys must be loaded via environment variables; never hardcoded.



## 4. Success Criteria

*   **Accuracy:** 100% of answers are grounded in provided book chunks (zero hallucination tolerance).

*   **Functionality:** Chatbot successfully processes queries based *only* on user-selected text.

*   **Performance:** Response latency under 3 seconds for standard queries.
```

## Response snapshot

```
The project constitution has been updated to version 2.0.0. The core principles, global tech stack standards, implementation rules, and success criteria have been revised based on your input. The file .specify/memory/constitution.md was modified.
```

## Outcome

- ✅ Impact: Constitution updated to v2.0.0.
- 🧪 Tests: N/A
- 📁 Files: Updated .specify/memory/constitution.md
- 🔁 Next prompts: Review updated templates
- 🧠 Reflection: Major version bump due to significant changes in core principles.

## Evaluation notes (flywheel)

- Failure modes observed: null
- Graders run and results (PASS/FAIL): null
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
