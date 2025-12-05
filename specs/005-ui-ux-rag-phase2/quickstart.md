# Quickstart: UI/UX Rework and Phase 2 RAG Chatbot Integration

**Feature**: 005-ui-ux-rag-phase2
**Date**: 2025-11-30
**Audience**: Developers implementing this feature

## Overview

This quickstart guide provides step-by-step integration scenarios for the three main user flows:
1. **Selected Text Grounding** ("Magna Carta" feature)
2. **Global Context Search** (full-book Q&A)
3. **Dark Mode Persistence** (theme toggle)

Each scenario includes frontend code, backend code, and end-to-end testing instructions.

---

## Scenario 1: Selected Text Grounding

**User Flow**: Reader highlights paragraph → Asks question → Receives grounded answer

### Frontend Implementation (React + TypeScript)

#### Step 1: Set up Selection Context

```typescript
// my-website/src/theme/Root.tsx
import React, {createContext, useContext, useState, useEffect} from 'react';

export interface SelectionContextType {
  selectedText: string;
  sourceChapter: string | null;
  setSelectedText: (text: string, chapter?: string) => void;
  clearSelection: () => void;
}

export const SelectionContext = createContext<SelectionContextType>({
  selectedText: '',
  sourceChapter: null,
  setSelectedText: () => {},
  clearSelection: () => {},
});

export default function Root({children}) {
  const [selectedText, setSelectedTextState] = useState('');
  const [sourceChapter, setSourceChapter] = useState<string | null>(null);

  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      if (selection && selection.toString().trim().length >= 10) {
        const text = selection.toString().trim();
        setSelectedTextState(text);

        // Extract chapter slug from current URL
        const path = window.location.pathname;
        const match = path.match(/\/docs\/(physical-ai\/.+)/);
        const chapter = match ? match[1] : null;
        setSourceChapter(chapter);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, []);

  const setSelectedText = (text: string, chapter?: string) => {
    setSelectedTextState(text);
    setSourceChapter(chapter || null);
  };

  const clearSelection = () => {
    setSelectedTextState('');
    setSourceChapter(null);
  };

  return (
    <SelectionContext.Provider value={{selectedText, sourceChapter, setSelectedText, clearSelection}}>
      {children}
    </SelectionContext.Provider>
  );
}
```

#### Step 2: Create API Client

```typescript
// my-website/src/utils/api.ts
import axios from 'axios';
import type {ChatRequest, GroundedChatRequest, ChatResponse, APIResult} from './types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function chatGrounded(
  query: string,
  selectedText: string,
  sourceChapter?: string
): Promise<APIResult<ChatResponse>> {
  try {
    const request: GroundedChatRequest = {
      query,
      selected_text: selectedText,
      source_chapter: sourceChapter,
    };

    const response = await apiClient.post<ChatResponse>('/chat/grounded', request);
    return {success: true, data: response.data};
  } catch (error) {
    const message = axios.isAxiosError(error)
      ? error.response?.data?.detail || error.message
      : 'Unknown error';
    return {success: false, error: message};
  }
}

export async function chatGlobal(query: string): Promise<APIResult<ChatResponse>> {
  try {
    const request: ChatRequest = {query};
    const response = await apiClient.post<ChatResponse>('/chat', request);
    return {success: true, data: response.data};
  } catch (error) {
    const message = axios.isAxiosError(error)
      ? error.response?.data?.detail || error.message
      : 'Unknown error';
    return {success: false, error: message};
  }
}
```

#### Step 3: Build Chat Widget Component

```typescript
// my-website/src/components/ChatWidget/ChatWidget.tsx
import React, {useState, useContext} from 'react';
import {SelectionContext} from '@theme/Root';
import {chatGrounded, chatGlobal} from '@site/src/utils/api';
import type {ChatMessage} from '@site/src/utils/types';
import styles from './styles.module.css';

export default function ChatWidget() {
  const {selectedText, sourceChapter, clearSelection} = useContext(SelectionContext);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [query, setQuery] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      content: query,
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    // Call API (grounded if text is selected, otherwise global)
    const result = selectedText
      ? await chatGrounded(query, selectedText, sourceChapter || undefined)
      : await chatGlobal(query);

    setIsLoading(false);

    if (result.success) {
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        content: result.data.answer,
        sender: 'assistant',
        timestamp: new Date(),
        sources: result.data.sources,
        grounded: result.data.grounded,
      };
      setMessages(prev => [...prev, assistantMessage]);

      if (result.data.grounded) {
        clearSelection(); // Clear selection after grounded query
      }
    } else {
      // Error handling
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        content: `Error: ${result.error}`,
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  return (
    <div className={styles.chatWidget}>
      {!isOpen ? (
        <button className={styles.chatButton} onClick={() => setIsOpen(true)}>
          💬 Ask a Question
        </button>
      ) : (
        <div className={styles.chatContainer}>
          <div className={styles.chatHeader}>
            <h3>Book Q&A</h3>
            {selectedText && (
              <span className={styles.groundedBadge}>📌 Grounded Mode</span>
            )}
            <button onClick={() => setIsOpen(false)}>✕</button>
          </div>

          <div className={styles.chatMessages}>
            {messages.map(msg => (
              <div key={msg.id} className={styles[msg.sender]}>
                <p>{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className={styles.sources}>
                    <strong>Sources:</strong>
                    <ul>
                      {msg.sources.map((src, idx) => (
                        <li key={idx}>
                          <a href={`/docs/${src.chapter}`}>{src.title}</a>
                          {src.relevance_score && (
                            <span> ({(src.relevance_score * 100).toFixed(0)}% match)</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
            {isLoading && <div className={styles.loading}>Thinking...</div>}
          </div>

          <form className={styles.chatInput} onSubmit={handleSubmit}>
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder={selectedText ? 'Ask about selected text...' : 'Ask a question...'}
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !query.trim()}>
              Send
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
```

### Backend Implementation (FastAPI + Python)

#### Step 1: Pydantic Models

```python
# api/app/models/chat.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class GroundedChatRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    selected_text: str = Field(..., min_length=10, max_length=10000)
    source_chapter: Optional[str] = None
    conversation_id: Optional[str] = None

    @field_validator('query', 'selected_text')
    def strip_whitespace(cls, v):
        return v.strip()

class ChatResponse(BaseModel):
    answer: str
    sources: list['SourceCitation'] = Field(default_factory=list)
    grounded_in: Optional[str] = None
    conversation_id: str
    grounded: bool

class SourceCitation(BaseModel):
    chapter: str
    title: str
    relevance_score: Optional[float] = None
```

#### Step 2: Grounding Service

```python
# api/app/services/llm.py
from openai import OpenAI
from app.models.chat import ChatResponse, GroundedChatRequest
import uuid

client = OpenAI()

GROUNDED_SYSTEM_PROMPT = """You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.

**STRICT RULES:**
1. ONLY answer questions using the provided text excerpt below.
2. If the excerpt does not contain enough information, respond with:
   "I can only answer based on the selected text. Please select more text or ask a broader question."
3. Do NOT use external knowledge.
4. Keep your answer concise and directly related to the excerpt.

**Selected Text:**
{selected_text}

**Question:** {query}
"""

async def generate_grounded_response(request: GroundedChatRequest) -> ChatResponse:
    """Generate answer grounded in selected text"""

    system_prompt = GROUNDED_SYSTEM_PROMPT.format(
        selected_text=request.selected_text,
        query=request.query
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.query}
        ],
        temperature=0.3,
        max_tokens=1000
    )

    answer = response.choices[0].message.content

    return ChatResponse(
        answer=answer,
        grounded_in=request.selected_text[:100] + "...",  # Truncated preview
        conversation_id=request.conversation_id or str(uuid.uuid4()),
        grounded=True
    )
```

#### Step 3: FastAPI Endpoint

```python
# api/app/routers/chat.py
from fastapi import APIRouter, HTTPException
from app.models.chat import GroundedChatRequest, ChatResponse
from app.services.llm import generate_grounded_response

router = APIRouter()

@router.post("/chat/grounded", response_model=ChatResponse)
async def chat_grounded(request: GroundedChatRequest):
    """
    Grounded context chatbot (selected text priority)
    """
    try:
        response = await generate_grounded_response(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Testing Scenario 1

#### Manual Testing

1. **Start Backend**:
   ```bash
   cd api
   uvicorn app.main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd my-website
   npm start
   ```

3. **Test Flow**:
   - Navigate to any chapter (e.g., `/docs/physical-ai/module-1/ros2-architecture`)
   - Highlight a paragraph about ROS 2 nodes
   - Click chat button (should show "📌 Grounded Mode" badge)
   - Ask: "Explain this concept"
   - Verify response only uses highlighted text

#### E2E Test (Playwright)

```typescript
// tests/e2e/chatbot-grounding.spec.ts
import {test, expect} from '@playwright/test';

test('selected text grounding works', async ({page}) => {
  // Navigate to chapter
  await page.goto('http://localhost:3000/docs/physical-ai/module-1/ros2-architecture');

  // Highlight text
  const paragraph = page.locator('p:has-text("ROS 2 nodes communicate")');
  await paragraph.selectText();

  // Open chat widget
  await page.click('[aria-label="Ask a Question"]');

  // Verify grounded mode badge
  await expect(page.locator('text=📌 Grounded Mode')).toBeVisible();

  // Ask question
  await page.fill('input[placeholder="Ask about selected text..."]', 'How do nodes talk?');
  await page.click('button:has-text("Send")');

  // Wait for response
  await page.waitForSelector('.assistant .message', {timeout: 10000});

  // Verify response mentions selected text concepts
  const response = await page.locator('.assistant .message').textContent();
  expect(response).toContain('nodes');
  expect(response).toContain('communicate');
});
```

---

## Scenario 2: Global Context Search

**User Flow**: Reader asks broad question → Receives answer with chapter citations

### Frontend (Reuse API Client from Scenario 1)

```typescript
// Already implemented in chatGlobal() function
// Usage in ChatWidget component automatically switches mode based on selectedText state
```

### Backend Implementation

```python
# api/app/services/retriever.py
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.services.embedder import generate_embedding
from app.models.chat import SourceCitation

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

async def retrieve_top_k_chunks(query: str, k: int = 5) -> list[dict]:
    """Vector search for relevant chunks"""

    # Generate query embedding
    query_embedding = await generate_embedding(query)

    # Search Qdrant
    results = client.search(
        collection_name="book_chapters",
        query_vector=query_embedding,
        limit=k,
        score_threshold=0.7
    )

    if len(results) == 0:
        return []

    return [
        {
            "text": hit.payload["text"],
            "chapter": hit.payload["chapter_id"],
            "title": hit.payload["chapter_title"],
            "score": hit.score
        }
        for hit in results
    ]
```

```python
# api/app/routers/chat.py (continued)
from app.services.retriever import retrieve_top_k_chunks

@router.post("/chat", response_model=ChatResponse)
async def chat_global(request: ChatRequest):
    """Global context chatbot (full-book search)"""

    # Retrieve relevant chunks
    chunks = await retrieve_top_k_chunks(request.query)

    if not chunks:
        return ChatResponse(
            answer="I can only answer questions based on the content in this textbook. Your question requires information not covered in these chapters.",
            sources=[],
            conversation_id=request.conversation_id or str(uuid.uuid4()),
            grounded=False
        )

    # Build context from chunks
    context = "\n\n".join([f"[{chunk['title']}]\n{chunk['text']}" for chunk in chunks])

    # Generate answer
    system_prompt = f"""You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.

**STRICT RULES:**
1. ONLY answer using the book excerpts below.
2. Cite chapters explicitly (e.g., "According to Chapter 7...").
3. If excerpts don't contain enough info, refuse to answer.

**Book Excerpts:**
{context}

**Question:** {request.query}
"""

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.query}
        ],
        temperature=0.3
    )

    answer = response.choices[0].message.content

    # Extract sources
    sources = [
        SourceCitation(
            chapter=chunk["chapter"],
            title=chunk["title"],
            relevance_score=chunk["score"]
        )
        for chunk in chunks
    ]

    return ChatResponse(
        answer=answer,
        sources=sources,
        conversation_id=request.conversation_id or str(uuid.uuid4()),
        grounded=False
    )
```

### Testing Scenario 2

```typescript
// tests/e2e/chatbot-global.spec.ts
test('global context search with citations', async ({page}) => {
  await page.goto('http://localhost:3000');

  // Open chat (no text selection)
  await page.click('[aria-label="Ask a Question"]');

  // Verify NOT in grounded mode
  await expect(page.locator('text=📌 Grounded Mode')).not.toBeVisible();

  // Ask global question
  await page.fill('input[placeholder="Ask a question..."]', 'What is ROS 2?');
  await page.click('button:has-text("Send")');

  // Wait for response
  await page.waitForSelector('.assistant .message');

  // Verify sources are included
  await expect(page.locator('.sources')).toBeVisible();
  await expect(page.locator('.sources a')).toHaveCount.toBeGreaterThan(0);
});
```

---

## Scenario 3: Dark Mode Persistence

**User Flow**: Reader toggles dark mode → Preference persists across sessions

### Frontend Implementation

```typescript
// my-website/src/components/DarkModeToggle/DarkModeToggle.tsx
import React from 'react';
import {useColorMode} from '@docusaurus/theme-common';
import styles from './styles.module.css';

export default function DarkModeToggle() {
  const {colorMode, setColorMode} = useColorMode();

  const toggleTheme = () => {
    setColorMode(colorMode === 'dark' ? 'light' : 'dark');
  };

  return (
    <button
      className={styles.themeToggle}
      onClick={toggleTheme}
      aria-label="Toggle dark mode"
      title={`Switch to ${colorMode === 'dark' ? 'light' : 'dark'} mode`}
    >
      {colorMode === 'dark' ? '☀️' : '🌙'}
    </button>
  );
}
```

```typescript
// my-website/docusaurus.config.ts (updated)
themeConfig: {
  colorMode: {
    defaultMode: 'light',
    disableSwitch: false,
    respectPrefersColorScheme: true, // Honors OS preference
  },
  // ... rest of config
}
```

```css
/* my-website/src/css/custom.css (updated for dark mode) */
:root {
  --ifm-color-primary: #2e8555;
  --ifm-background-color: #ffffff;
  --ifm-font-color-base: #000000;
}

[data-theme='dark'] {
  --ifm-color-primary: #25c2a0;
  --ifm-background-color: #1b1b1d;
  --ifm-font-color-base: #ffffff;
  --ifm-heading-color: #ffffff;
}

/* Ensure chat widget respects dark mode */
[data-theme='dark'] .chatWidget {
  background-color: var(--ifm-background-color);
  color: var(--ifm-font-color-base);
  border: 1px solid #444;
}
```

### Testing Scenario 3

```typescript
// tests/e2e/dark-mode.spec.ts
test('dark mode persists across sessions', async ({page}) => {
  await page.goto('http://localhost:3000');

  // Toggle to dark mode
  await page.click('[aria-label="Toggle dark mode"]');

  // Verify dark mode applied
  const html = page.locator('html');
  await expect(html).toHaveAttribute('data-theme', 'dark');

  // Verify localStorage
  const theme = await page.evaluate(() => localStorage.getItem('theme'));
  expect(theme).toBe('dark');

  // Reload page
  await page.reload();

  // Verify dark mode persisted
  await expect(html).toHaveAttribute('data-theme', 'dark');
});
```

---

## Common Pitfalls & Troubleshooting

### Issue 1: CORS Errors

**Symptom**: Frontend can't call backend (Network error in browser console)

**Solution**: Verify CORS middleware in FastAPI

```python
# api/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.github.io"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Issue 2: Selected Text Not Detected

**Symptom**: Grounded mode badge doesn't appear after highlighting text

**Solution**: Check minimum length (10 chars) and event listener

```typescript
// Debugging: Log selection events
useEffect(() => {
  const handleSelection = () => {
    const selection = window.getSelection();
    console.log('Selection length:', selection?.toString().length);
    // ... rest of handler
  };
  // ...
}, []);
```

### Issue 3: Dark Mode Not Persisting

**Symptom**: Theme resets to light on page reload

**Solution**: Verify Docusaurus config and localStorage

```bash
# Check localStorage in browser console
localStorage.getItem('theme')  // Should return 'dark' or 'light'
```

---

## Next Steps

1. ✅ Integration scenarios documented
2. 🔄 Implement components following these patterns
3. 🔄 Run E2E tests to validate flows
4. 🔄 Update agent context with quickstart examples
5. 🔄 Generate tasks via `/sp.tasks` for implementation
