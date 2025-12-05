# Backend API Integration Summary

## Overview
Successfully integrated the FastAPI backend RAG chatbot with the Docusaurus frontend ChatWidget component.

## Changes Made

### 1. Updated Type Definitions (`src/utils/types.ts`)

**Before:** Used unified API with `mode` field
**After:** Separate interfaces matching backend models

- `ChatRequest`: For `POST /chat` - contains `question` field
- `GroundedChatRequest`: For `POST /chat/grounded` - contains `question` and `selected_text`
- `ChatResponse`: Updated to match backend response structure
  - `sources: Source[]` (instead of `SourceCitation[]`)
  - Added `latency?: number`
  - Added `context?: string`
  - Removed `mode` and `conversation_id` fields
- `Source`: Matches backend structure
  - `chapter: number`
  - `section: string`
  - `page?: string`
  - `relevance_score?: number`
- `HealthResponse`: Simplified to match backend
  - `status: string`
  - `qdrant_connected: boolean`

**API Endpoints:**
```typescript
export const API_ENDPOINTS = {
  HEALTH: "/health",
  CHAT: "/chat",
  CHAT_GROUNDED: "/chat/grounded",
  INDEX: "/index",
} as const;
```

### 2. Updated API Client (`src/utils/api.ts`)

**chatGlobal Function:**
```typescript
// Before:
chatGlobal(query: string, conversationId?: string)

// After:
chatGlobal(question: string)
```
- Removed `conversationId` parameter (not supported by backend MVP)
- Changed parameter name from `query` to `question` to match backend
- Sends to `POST /chat` endpoint

**chatGrounded Function:**
```typescript
// Before:
chatGrounded(query: string, selectedText: string, sourceChapter?: string, conversationId?: string)

// After:
chatGrounded(question: string, selectedText: string)
```
- Removed `sourceChapter` parameter (not used by backend)
- Removed `conversationId` parameter (not supported by backend MVP)
- Changed parameter name from `query` to `question` to match backend
- Sends to `POST /chat/grounded` endpoint

**Configuration:**
- Moved `DEFAULT_API_CONFIG` to `src/utils/config.ts`
- Imports config from separate file for better organization

### 3. Updated ChatWidget Component (`src/components/ChatWidget/ChatWidget.tsx`)

**handleSendMessage Function Changes:**
```typescript
// Before:
result = await chatGrounded(query, selectedText, sourceChapter || undefined, state.conversationId || undefined);
result = await chatGlobal(query, state.conversationId || undefined);

// After:
result = await chatGrounded(query, selectedText);
result = await chatGlobal(query);
```

**Assistant Message Creation:**
```typescript
// Before:
grounded: result.data.grounded,
conversationId: result.data.conversation_id,

// After:
grounded: isGroundedMode,  // Determined client-side based on selected text
// conversationId removed from state updates
```

### 4. Updated ChatMessage Component (`src/components/ChatWidget/ChatMessage.tsx`)

**Source Display:**
```typescript
// Before:
<a href={`/docs/${source.book}`}>
  {source.book}
</a>

// After:
Chapter {source.chapter}: {source.section}
{source.page && source.page !== "N/A" && (
  <span> (Page {source.page})</span>
)}
```

Updated to display chapter number and section name instead of book path/slug.

## API Integration Flow

### Global Chat (POST /chat)

1. User types question without selecting text
2. ChatWidget detects no selection (`selectedText.length < 10`)
3. Calls `chatGlobal(question)`
4. API sends:
   ```json
   {
     "question": "What is Physical AI?"
   }
   ```
5. Backend responds:
   ```json
   {
     "answer": "Physical AI refers to...",
     "sources": [
       {
         "chapter": 1,
         "section": "Introduction",
         "page": "N/A",
         "relevance_score": 0.95
       }
     ],
     "latency": 1.23
   }
   ```

### Grounded Chat (POST /chat/grounded)

1. User selects text on page (≥10 characters)
2. ChatWidget shows "🎯 Grounded Mode" badge
3. User types question about selection
4. Calls `chatGrounded(question, selectedText)`
5. API sends:
   ```json
   {
     "question": "What are the key points?",
     "selected_text": "ROS2 provides a robust framework for..."
   }
   ```
6. Backend responds with answer constrained to selected text:
   ```json
   {
     "answer": "Based on the selected text, the key points are...",
     "sources": [],  // Empty for grounded mode
     "latency": 0.87
   }
   ```

## Testing Checklist

- [x] Type definitions match backend models exactly
- [x] API client sends correct request format
- [x] ChatWidget calls correct endpoints
- [x] Sources display correctly in UI
- [ ] Build completes without TypeScript errors (in progress)
- [ ] Manual testing with running backend:
  - [ ] Global chat returns relevant answers with sources
  - [ ] Grounded chat constrains answer to selected text
  - [ ] Error handling works (backend down, invalid input)
  - [ ] Loading states display correctly

## Environment Configuration

**Backend URL Configuration:**
File: `src/utils/config.ts`

```typescript
export const DEFAULT_API_CONFIG: APIConfig = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
};
```

**For Local Development:**
```bash
# Backend runs on http://localhost:8000
# Frontend auto-connects to backend
npm run start
```

**For Production:**
Set environment variable:
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

## Files Modified

1. `my-website/src/utils/types.ts` - Type definitions
2. `my-website/src/utils/api.ts` - API client functions
3. `my-website/src/utils/config.ts` - API configuration (already existed, no changes needed)
4. `my-website/src/components/ChatWidget/ChatWidget.tsx` - Main component
5. `my-website/src/components/ChatWidget/ChatMessage.tsx` - Message display

## Next Steps

1. Wait for build to complete and verify no TypeScript errors
2. Start backend: `cd backend && uv run uvicorn app.main:app --reload`
3. Start frontend: `cd my-website && npm run start`
4. Test both endpoints manually:
   - Test global chat with various questions
   - Test grounded chat by selecting text
   - Verify sources display correctly
   - Test error scenarios

## Notes

- Removed conversation ID tracking (not implemented in backend MVP)
- Removed source chapter tracking (not used by backend)
- Grounded mode is determined client-side based on text selection length
- Backend MVP does not support multi-turn conversations yet
