# Feature Specification: UI/UX Rework and Phase 2 RAG Chatbot Integration

**Feature Branch**: `005-ui-ux-rag-phase2`
**Created**: 2025-11-30
**Status**: Draft
**Input**: User description: "Execute the first stage of Phase 2 by implementing major UI/UX improvements (Home Page & Dark Mode) and integrating the RAG Chatbot (Phase 2 MVP) to enable context-grounded Q&A on the book's content."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Context-Grounded Book Q&A (Priority: P1)

A reader is studying a specific chapter and wants to ask questions about concepts within that content. They highlight text on the page, click the chatbot interface, ask a question, and receive an answer that specifically references and is grounded in their selected text.

**Why this priority**: This is the core value proposition of Phase 2 - enabling readers to engage with the book content through AI-assisted Q&A that respects the source material boundaries. This delivers immediate learning value and demonstrates the "Magna Carta" grounding feature.

**Independent Test**: Can be fully tested by loading any chapter, selecting a paragraph, opening the chat interface, asking a question about the selected text, and verifying the response references only the highlighted content. Delivers standalone value as a study assistant.

**Acceptance Scenarios**:

1. **Given** a reader is viewing Chapter 5 on "RAG Fundamentals", **When** they highlight the paragraph about vector embeddings and ask "How do embeddings work?", **Then** the chatbot provides an answer using only the highlighted text as context
2. **Given** a reader highlights a code example, **When** they ask "Explain this code", **Then** the chatbot explains the specific code snippet without referencing external documentation
3. **Given** a reader asks a question without selecting any text, **When** the chatbot processes the query, **Then** it uses the full book content as context and clearly indicates the source chapter/section in the response

---

### User Story 2 - Enhanced Book Navigation and Discovery (Priority: P2)

A new visitor arrives at the book's homepage and needs to quickly understand what the book covers and find relevant chapters. They see a well-designed homepage with clear section organization, visual hierarchy, and intuitive navigation that helps them discover content aligned with their learning goals.

**Why this priority**: First impressions matter. An improved homepage and restructured navigation (4-5 parts) reduces friction for new readers and improves content discoverability, directly supporting user retention and engagement.

**Independent Test**: Can be fully tested by loading the homepage and verifying visual improvements are present, checking that the sidebar shows 4-5 high-level parts with nested chapters, and confirming a new user can locate a specific topic within 30 seconds. Delivers standalone value as improved UX.

**Acceptance Scenarios**:

1. **Given** a visitor lands on the homepage, **When** they view the page, **Then** they see a visually appealing layout with clear headings, descriptive summaries, and call-to-action elements that guide them to start reading
2. **Given** a reader opens the sidebar navigation, **When** they scan the structure, **Then** they see 4-5 major parts (e.g., "Foundations", "RAG Architecture", "Advanced Topics", "Case Studies") with all 42 chapters organized underneath
3. **Given** a reader wants to find content about vector databases, **When** they use the restructured navigation, **Then** they can identify the relevant part and chapter within 3 clicks

---

### User Story 3 - Personalized Reading Environment (Priority: P3)

A reader prefers to read technical content in dark mode to reduce eye strain during extended study sessions. They toggle dark mode from the header, and the entire site (including the embedded chatbot) switches to a dark theme. Their preference is remembered across sessions.

**Why this priority**: Dark mode is a standard expectation for modern technical documentation and significantly improves user comfort for extended reading sessions. While not core to the RAG functionality, it enhances overall UX and demonstrates polish.

**Independent Test**: Can be fully tested by clicking the dark mode toggle in the header, verifying all page elements (text, backgrounds, code blocks, chatbot UI) switch to dark theme, closing the browser, reopening the site, and confirming the dark mode preference persists. Delivers standalone value as a usability feature.

**Acceptance Scenarios**:

1. **Given** a reader is viewing the site in light mode, **When** they click the dark mode toggle in the header, **Then** the entire page (including navigation, content, and chatbot) transitions smoothly to dark theme
2. **Given** a reader has enabled dark mode, **When** they close the browser and return to the site, **Then** dark mode is still active (preference persisted in local storage)
3. **Given** a reader switches between pages, **When** navigating through chapters, **Then** the dark mode setting remains consistent across all pages

---

### User Story 4 - Global Book Knowledge Access (Priority: P2)

A reader has a general question about a concept that might be covered across multiple chapters (e.g., "What are the main challenges with RAG systems?"). They open the chatbot without selecting any text, ask their question, and receive a comprehensive answer that synthesizes information from relevant chapters while clearly citing sources.

**Why this priority**: Complements the selected-text grounding feature by enabling broader knowledge exploration. This supports readers who want to understand cross-cutting themes or compare approaches across different sections of the book.

**Independent Test**: Can be fully tested by opening the chatbot with no text selection, asking a broad question (e.g., "Compare different embedding models"), and verifying the response draws from multiple chapters while maintaining grounding in book content only. Delivers standalone value as a global search/synthesis tool.

**Acceptance Scenarios**:

1. **Given** no text is selected, **When** a reader asks "What are the best practices for chunking strategies?", **Then** the chatbot provides an answer synthesizing information from relevant chapters and cites specific sections
2. **Given** a reader asks a question requiring external knowledge (e.g., "What is the latest OpenAI model?"), **When** the chatbot processes the query, **Then** it politely refuses and explains it can only answer questions based on the book content
3. **Given** a broad question is asked, **When** the chatbot responds, **Then** the answer includes references to specific chapter numbers or section titles where the information was found

---

### Edge Cases

- **What happens when a reader selects text that doesn't contain enough context to answer their question?** The chatbot should gracefully indicate that the selected text doesn't provide sufficient information to answer the query and suggest either selecting more text or asking without selection for global context.

- **How does the system handle very long text selections (e.g., entire chapters)?** The system should process the selection but may need to truncate or summarize context if it exceeds token limits, informing the user that the context was large.

- **What if a reader asks a question in a different language than the book content?** The chatbot should respond in the query language but clarify that answers are limited to the English book content (Urdu translation is a future bonus feature).

- **How does dark mode affect embedded images, diagrams, or code syntax highlighting?** All visual elements should have dark mode variants with appropriate contrast ratios to maintain readability.

- **What happens if the RAG backend is unavailable or returns an error?** The chatbot UI should display a user-friendly error message (e.g., "The Q&A service is temporarily unavailable. Please try again later.") and degrade gracefully without breaking the static site.

- **What if JavaScript is disabled in the reader's browser?** The static book content remains fully accessible; only the chatbot feature becomes unavailable (progressive enhancement principle).

## Requirements *(mandatory)*

### Functional Requirements

#### Homepage and Navigation

- **FR-001**: The homepage MUST display a redesigned layout with improved visual hierarchy, including a hero section, feature highlights, and clear calls-to-action for starting to read
- **FR-002**: The sidebar navigation MUST reorganize the existing 42 chapters into 4-5 high-level parts/modules with descriptive names that reflect content themes
- **FR-003**: Each part in the sidebar MUST be collapsible/expandable to reduce visual clutter and improve navigation efficiency
- **FR-004**: The homepage MUST include a brief overview of each major part to help readers understand the book's structure at a glance

#### Dark Mode

- **FR-005**: The site header MUST include a visible dark mode toggle button accessible from all pages
- **FR-006**: Activating dark mode MUST apply a consistent dark theme across all page elements including text, backgrounds, navigation, code blocks, and the chatbot interface
- **FR-007**: The dark mode preference MUST persist across browser sessions using local storage
- **FR-008**: All text in dark mode MUST maintain sufficient contrast ratios (WCAG AA minimum 4.5:1) for readability
- **FR-009**: The dark mode toggle MUST provide visual feedback (icon change or animation) when activated

#### RAG Chatbot Integration

- **FR-010**: A chatbot interface MUST be embedded within the Docusaurus frontend, accessible from all book pages
- **FR-011**: The chatbot interface MUST provide a clear visual affordance (e.g., button, widget) for users to initiate Q&A
- **FR-012**: The chatbot MUST accept user queries as text input with a submit mechanism (button or Enter key)
- **FR-013**: The chatbot MUST display responses in a readable format with clear distinction between user queries and assistant responses

#### Context Grounding (Selected Text)

- **FR-014**: When a reader highlights text on any book page, the chatbot MUST detect and capture the selected text as context
- **FR-015**: The chatbot MUST send the selected text to the backend as an optional `selected_text` parameter
- **FR-016**: When `selected_text` is provided, the chatbot response MUST prioritize and ground answers exclusively in the highlighted content
- **FR-017**: The chatbot interface MUST provide visual feedback when selected text is detected (e.g., "Asking about selected text...")
- **FR-018**: Users MUST be able to clear the selected text context and ask questions against the global book content

#### Global Context Mode

- **FR-019**: When no text is selected, the chatbot MUST process queries using the full book content as context
- **FR-020**: Global context responses MUST cite specific chapter numbers or section titles where information was sourced
- **FR-021**: The chatbot MUST refuse to answer questions that require external knowledge not present in the book content

#### Groundedness and Source Truth

- **FR-022**: All chatbot responses MUST be grounded exclusively in the book's content (no external web searches or general knowledge)
- **FR-023**: If a query cannot be answered from the book content, the chatbot MUST explicitly state this and decline to answer
- **FR-024**: The chatbot MUST NOT hallucinate or fabricate information not present in the source material

#### Error Handling and Degradation

- **FR-025**: If the RAG backend is unavailable, the chatbot UI MUST display a clear error message without breaking the static site functionality
- **FR-026**: The static book content MUST remain fully accessible even if the chatbot feature fails
- **FR-027**: Network errors or timeouts MUST be handled gracefully with user-friendly messages

### Key Entities *(include if feature involves data)*

- **User Query**: Represents a question asked by the reader, containing the query text and optional selected context. Attributes include query string, timestamp, selected text (optional), and query mode (global vs grounded).

- **Selected Text Context**: Represents text highlighted by the user on a book page. Attributes include the text content, source page/chapter, character position range, and timestamp of selection.

- **Chat Message**: Represents a single message in the conversation thread. Attributes include message content, sender type (user/assistant), timestamp, and associated context (if grounded).

- **Book Chapter**: Represents a chapter or section of the book content indexed for RAG retrieval. Attributes include chapter number, title, content text, part/module assignment, and vector embeddings (implementation detail, but conceptually relevant).

- **Navigation Part**: Represents a high-level organizational grouping of chapters. Attributes include part name, description, chapter list, and display order.

- **Theme Preference**: Represents the user's theme choice (light/dark mode). Attributes include theme mode, timestamp of last change, and persistence key.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The book's homepage displays updated visual components and layout, and the Docusaurus build completes without errors
- **SC-002**: A functional dark mode toggle is present in the site header, and activating it successfully switches the theme for all page elements
- **SC-003**: Dark mode preference persists across browser sessions (verifiable by closing and reopening the browser)
- **SC-004**: The sidebar configuration displays 4-5 high-level parts with all 42 chapters nested logically underneath
- **SC-005**: The RAG chatbot interface is successfully embedded in the Docusaurus site and accessible from all pages
- **SC-006**: A test query with selected text (e.g., highlighting a paragraph and asking "Summarize this") returns a response grounded exclusively in the selected context (Selected Context Test passes)
- **SC-007**: A test query without selected text (e.g., "What is RAG?") returns a comprehensive answer from the book content with chapter citations (Global Context Test passes)
- **SC-008**: A test query requiring external knowledge (e.g., "What is the weather today?") is explicitly refused with a message explaining the chatbot only answers book-related questions (Groundedness Test passes)
- **SC-009**: All text in dark mode maintains a contrast ratio of at least 4.5:1 (WCAG AA compliance for readability)
- **SC-010**: Readers can navigate from the homepage to a specific chapter related to their interest within 30 seconds using the redesigned structure

### Quality Outcomes

- **SC-011**: The chatbot response time for typical queries is under 5 seconds (perceived as responsive by users)
- **SC-012**: The visual transition when toggling dark mode is smooth and does not cause layout shifts or flashing
- **SC-013**: New visitors to the homepage can understand the book's scope and structure within 10 seconds of landing

## Assumptions *(mandatory)*

- The existing 42 chapters are already authored and available in the Docusaurus site; this feature only reorganizes navigation and adds UI improvements
- The book content is in English; multi-language support (Urdu translation) is out of scope for this phase
- Readers will use modern browsers with JavaScript enabled for the chatbot feature (though static content remains accessible without JS)
- The RAG backend (FastAPI + Qdrant) will be developed in parallel or already exists as part of the Phase 2 roadmap
- Authentication and user accounts are not required for this phase; the chatbot is publicly accessible (Better-Auth is a separate bonus feature)
- The chatbot will use an embedding model and retrieval strategy appropriate for book content (implementation details to be defined in planning)
- The Docusaurus deployment target is GitHub Pages, consistent with the Static Core architecture
- The RAG backend will be deployed separately (e.g., Render, Railway) with a public API endpoint accessible from the frontend

## Dependencies *(mandatory)*

- **Docusaurus 3.x**: The static site framework must remain unchanged; all UI improvements must work within Docusaurus constraints
- **RAG Backend API**: The chatbot feature depends on a deployed FastAPI backend with `/chat` and `/chat/grounded` endpoints (or equivalent) that accept queries and optional `selected_text` parameters
- **Qdrant Cloud**: The backend must have access to a Qdrant vector database containing indexed book content
- **OpenAI API or Equivalent**: The RAG backend requires an LLM API for generating responses (e.g., OpenAI, Anthropic)
- **Embedding Model**: The backend must use an embedding model compatible with Qdrant for vector search (e.g., OpenAI text-embedding-3-small, sentence-transformers)

## Out of Scope *(mandatory)*

- **Better-Auth Integration**: User authentication, personalized chat history, and user accounts are explicitly out of scope (separate Phase 2 bonus feature)
- **Urdu Translation**: Multi-language support and translation features are not included in this phase
- **Personalization Features**: Customized reading recommendations, bookmarks, or progress tracking are not part of this feature
- **PDF Export/Parsing**: Generating or parsing PDFs of book content is not required (content is assumed to be in the DOM)
- **Advanced RAG Features**: Multi-modal RAG, document upload, or custom knowledge base ingestion are beyond MVP scope
- **Analytics and Telemetry**: Tracking user interactions, query logs, or usage analytics is not required for this phase (can be added later)
- **Offline Mode**: The chatbot requires an active internet connection; offline functionality is not supported

## Constraints *(mandatory)*

- **Frontend Host**: The static site MUST continue using Docusaurus 3.x; no migration to alternative frameworks
- **Structural Preservation**: All 42 existing chapters MUST be preserved; only the navigation organization changes
- **RAG Backend Stack**: MUST use FastAPI, Qdrant Cloud, and comply with Integrated RAG Chatbot Constitution rules
- **Selected Text Parameter**: The backend API MUST support and correctly process the `selected_text` parameter for grounding
- **Source Truth Principle**: The chatbot MUST NOT answer questions requiring external knowledge; all responses MUST be grounded in book content only
- **No Framework Changes**: No changes to the core Docusaurus configuration that would break existing functionality or deployment pipeline
- **GitHub Pages Deployment**: The static site must remain compatible with GitHub Pages hosting

## Risks *(optional)*

- **RAG Backend Latency**: If backend response times exceed 5-10 seconds, user experience will degrade; mitigation requires optimized vector search and caching strategies
- **Context Window Limits**: Very long selected text or entire chapters may exceed LLM context windows; the system must handle truncation gracefully
- **Hallucination Risk**: Despite grounding constraints, the LLM may occasionally generate plausible-sounding but incorrect information; rigorous testing and prompt engineering are required
- **Dark Mode Theme Conflicts**: Custom Docusaurus themes or plugins may conflict with dark mode implementation; thorough testing across all pages is necessary
- **Mobile Responsiveness**: The chatbot interface and dark mode toggle must work seamlessly on mobile devices; responsive design testing is critical
- **API Cost Overruns**: High query volume could result in unexpected LLM API costs; rate limiting or usage monitoring may be needed

## Notes *(optional)*

- This feature represents the first major integration of the Static Core (Docusaurus) and Dynamic Core (RAG API), establishing patterns for future enhancements
- The "Magna Carta" selected text grounding feature is a key differentiator and should be prominently showcased in user onboarding or help documentation
- Consider adding a brief tutorial or tooltip on first visit to explain how to use the selected text feature
- The 4-5 parts for sidebar organization should be determined based on the actual book content themes (e.g., "Foundations", "Core Concepts", "Advanced Techniques", "Case Studies", "Appendices")
- Dark mode implementation should follow Docusaurus best practices and use the built-in theming system where possible to ensure maintainability
