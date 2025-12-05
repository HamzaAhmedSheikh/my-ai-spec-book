# ChatBot Integration Testing Guide

## Prerequisites

1. **Backend Running:**
   ```bash
   cd backend
   uv run uvicorn app.main:app --reload
   ```
   Backend should be accessible at `http://localhost:8000`

2. **Book Content Indexed:**
   ```bash
   curl -X POST http://localhost:8000/index
   ```
   Wait for indexing to complete (~2-5 minutes for full book)

3. **Frontend Running:**
   ```bash
   cd my-website
   npm run start
   ```
   Frontend should be accessible at `http://localhost:3000`

## Test Suite

### Test 1: Health Check
**Purpose:** Verify backend connectivity

**Steps:**
1. Open browser console (F12)
2. Navigate to `http://localhost:3000`
3. Open the chat widget (click 💬 button in bottom-right)
4. Widget should open without errors

**Expected Result:**
- No console errors
- Chat widget displays with greeting message

**API Call to Verify:**
```bash
curl http://localhost:8000/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "qdrant_connected": true
}
```

---

### Test 2: Global Chat - Simple Question
**Purpose:** Test basic question answering across the entire book

**Steps:**
1. Open chat widget
2. Type: "What is Physical AI?"
3. Press Enter or click send button (➤)

**Expected Result:**
- Loading indicator appears (three dots)
- Response appears within 3 seconds
- Answer provides a definition/explanation
- Sources section shows chapter references like:
  ```
  📖 Sources:
  • Chapter 1: Introduction (95% relevant)
  • Chapter 2: Core Concepts (87% relevant)
  ```

**Backend Logs to Check:**
```
INFO: Processing chat request: What is Physical AI?...
INFO: Chat response generated successfully (latency: 1.23s)
```

---

### Test 3: Global Chat - Technical Question
**Purpose:** Test retrieval of specific technical information

**Steps:**
1. Clear previous conversation (click 🗑️ button)
2. Type: "How do ROS2 nodes communicate?"
3. Send message

**Expected Result:**
- Answer mentions topics, services, and/or actions
- Sources reference ROS2 chapters
- Response is coherent and relevant

---

### Test 4: Grounded Chat - Text Selection
**Purpose:** Test "Magna Carta" feature with user-selected text

**Steps:**
1. Navigate to any book chapter page (if available) or use the chat widget
2. Highlight a paragraph of text (at least 50 words) - **Note:** Text selection feature may not work on home page
3. Open chat widget
4. Verify "🎯 Grounded Mode" badge appears in header
5. Type: "Summarize the key points"
6. Send message

**Expected Result:**
- Widget shows "🎯 Grounded Mode" badge
- Answer is constrained to the selected text only
- No sources displayed (empty sources list)
- Response has "🎯 Response grounded in your selected text" badge
- Selected text is cleared after response

**Manual API Test (without UI):**
```bash
curl -X POST http://localhost:8000/chat/grounded \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main components?",
    "selected_text": "ROS2 provides a framework with nodes, topics, services, and actions. Nodes are the basic building blocks that communicate via topics using a publish-subscribe pattern."
  }'
```

---

### Test 5: Error Handling - Backend Down
**Purpose:** Verify graceful error handling when backend is unavailable

**Steps:**
1. Stop the backend server (Ctrl+C)
2. Open chat widget
3. Type any question
4. Send message

**Expected Result:**
- Error message displays: "Cannot connect to chatbot API. Please check your internet connection."
- User can retry after backend restarts
- No console errors that crash the app

---

### Test 6: Error Handling - Empty Question
**Purpose:** Verify input validation

**Steps:**
1. Open chat widget
2. Try to send an empty message (just spaces)
3. Try to send a 1-2 character message

**Expected Result:**
- Send button is disabled when input is < 3 characters
- Character counter shows 0/1000

---

### Test 7: Error Handling - Long Input
**Purpose:** Verify max length validation

**Steps:**
1. Open chat widget
2. Paste a very long question (>1000 characters)

**Expected Result:**
- Input is truncated at 1000 characters
- Character counter shows 1000/1000
- Warning styling may appear (if implemented)

---

### Test 8: Multi-Turn Conversation
**Purpose:** Test conversation continuity (if supported)

**Steps:**
1. Clear chat history
2. Ask: "What is ROS2?"
3. Wait for response
4. Ask follow-up: "What are its main features?"

**Expected Result:**
- Both questions and answers appear in history
- Second answer may or may not reference first question context (backend MVP doesn't support conversation ID yet)

---

### Test 9: Source Link Verification
**Purpose:** Ensure source citations are correct

**Steps:**
1. Ask a question that should have sources
2. Check the sources section
3. Verify format matches: "Chapter X: Section Name (Y% relevant)"

**Expected Result:**
- Chapter numbers are valid integers
- Section names are descriptive
- Relevance scores are between 0-100%
- Page field shows if available (or hidden if "N/A")

---

### Test 10: Widget UI States
**Purpose:** Verify all UI states work correctly

**Steps:**
1. **Collapsed State:** Widget shows as 💬 button in bottom-right
2. **Expanded State:** Widget opens with header, messages area, input
3. **Empty State:** Shows greeting message and instructions
4. **Loading State:** Shows three animated dots while waiting
5. **Error State:** Shows red error message with warning icon (⚠️)
6. **Grounded Mode:** Shows badge when text is selected

---

## Performance Benchmarks

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Global chat response time | <3s (p95) | Browser DevTools Network tab |
| Grounded chat response time | <2s (p95) | Browser DevTools Network tab |
| Widget open/close animation | Smooth (60fps) | Visual inspection |
| Build time (production) | <2 minutes | `npm run build` timing |

---

## Troubleshooting

### Issue: "Cannot connect to chatbot API"
**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in backend allow `http://localhost:3000`
3. Check browser console for CORS errors
4. Verify API base URL in `my-website/src/utils/config.ts`

### Issue: "Sources not displaying"
**Solution:**
1. Check backend logs for retrieval results
2. Verify indexing completed: `curl http://localhost:8000/index` (should return job status)
3. Check browser console for JavaScript errors
4. Verify `Source` interface matches backend response

### Issue: "Grounded mode not activating"
**Solution:**
1. Ensure selected text is ≥10 characters
2. Check text selection in browser dev tools: `window.getSelection().toString()`
3. Verify `SelectionContext` in `Root.tsx` is working
4. Check if selection is cleared after first message (expected behavior)

### Issue: "Build fails with TypeScript errors"
**Solution:**
1. Check types in `src/utils/types.ts` match backend models exactly
2. Run `npm run build` to see specific errors
3. Verify imports are correct (no circular dependencies)
4. Check `api.ts` function signatures match type definitions

---

## Manual API Testing (Bypass Frontend)

### Test Global Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Physical AI?"}'
```

**Expected Response:**
```json
{
  "answer": "Physical AI refers to...",
  "sources": [
    {
      "chapter": 1,
      "section": "Introduction to Physical AI",
      "page": "N/A",
      "relevance_score": 0.95
    }
  ],
  "latency": 1.234
}
```

### Test Grounded Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat/grounded \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Summarize this",
    "selected_text": "ROS2 is a framework for robot development that provides tools and libraries for building distributed systems."
  }'
```

**Expected Response:**
```json
{
  "answer": "ROS2 is a robot development framework providing tools and libraries for distributed systems.",
  "sources": [],
  "latency": 0.876
}
```

---

## Success Criteria

✅ All 10 tests pass without errors
✅ Backend logs show no exceptions
✅ Frontend builds without TypeScript errors
✅ Global chat returns relevant answers with sources
✅ Grounded chat constrains answers to selected text
✅ Error handling displays user-friendly messages
✅ Performance meets targets (<3s global, <2s grounded)

---

## Notes

- Conversation ID tracking is not implemented in backend MVP
- Sources may be empty for grounded mode (expected behavior)
- Text selection feature requires implementing `SelectionContext` in `Root.tsx` (may already exist)
- Backend must complete indexing before chat can return relevant results
