# Text Selection & Timeout Fix Summary

## Problems Fixed

### 1. ⏱️ Request Timeout Error
**Problem:** Chatbot was timing out with error: "Request timed out. The chatbot is taking too long to respond."

**Root Cause:** API timeout was set to 30 seconds, but RAG processing (vector search + LLM generation) can take longer, especially on first query or with large contexts.

**Fix Applied:** ✅
```typescript
// File: my-website/src/utils/config.ts
timeout: 120000, // Increased from 30s to 120s (2 minutes)
```

### 2. 🎯 Text Selection Not Visible
**Problem:** User could select text, but there was no visual indication in the chatbot that text was selected for grounded mode.

**Fix Applied:** ✅ Added visual preview box showing:
- Selected text snippet (first 150 characters)
- Character count
- Clear button to remove selection
- Highlighted border in primary color

**Files Modified:**
1. `my-website/src/components/ChatWidget/ChatWidget.tsx` - Added preview component
2. `my-website/src/components/ChatWidget/styles.module.css` - Added styles

## How Text Selection Works Now

### Step-by-Step User Flow:

1. **Select Text on Page**
   - Highlight any text on the website (minimum 10 characters)
   - The selection is automatically captured by `SelectionContext` in `Root.tsx`

2. **Visual Feedback**
   - Open chat widget (click 💬 button)
   - You'll see a blue box above the input showing:
     ```
     🎯 Selected Text:
     [Your selected text preview...]
     150 characters selected                    [×]
     ```

3. **Ask Question**
   - Type your question in the input box
   - The question will be answered using ONLY the selected text (grounded mode)
   - Backend receives both `question` and `selected_text`

4. **Response**
   - Answer appears with "🎯 Response grounded in your selected text" badge
   - No sources displayed (because it's using your selection, not searching)
   - Selected text is automatically cleared after response

5. **Clear Selection** (Optional)
   - Click the [×] button in the selected text preview
   - Or the selection auto-clears after you get an answer

## Technical Implementation

### Text Selection Detection
**File:** `my-website/src/theme/Root.tsx` (lines 54-81)

```typescript
useEffect(() => {
  const handleSelection = () => {
    const selection = window.getSelection();

    if (selection && selection.toString().trim().length >= 10) {
      const text = selection.toString().trim();
      setSelectedTextState(text);
      setSourceChapter(chapter);
      setSelectionTime(new Date());
    }
  };

  document.addEventListener('mouseup', handleSelection);
  return () => document.removeEventListener('mouseup', handleSelection);
}, []);
```

**How it works:**
- Listens to `mouseup` events globally
- Checks if `window.getSelection()` has ≥10 characters
- Stores text in React Context (`SelectionContext`)
- ChatWidget reads from this context

### Visual Preview Component
**File:** `my-website/src/components/ChatWidget/ChatWidget.tsx` (lines 212-234)

```tsx
{selectedText.length >= 10 && (
  <div className={styles.selectedTextPreview}>
    <div className={styles.selectedTextHeader}>
      <span>🎯 Selected Text:</span>
      <button onClick={clearSelection}>✕</button>
    </div>
    <div className={styles.selectedTextContent}>
      {selectedText.length > 150
        ? `${selectedText.substring(0, 150)}...`
        : selectedText}
    </div>
    <div className={styles.selectedTextFooter}>
      {selectedText.length} characters selected
    </div>
  </div>
)}
```

### API Integration
**File:** `my-website/src/utils/api.ts` (lines 95-111)

```typescript
export async function chatGrounded(
  question: string,
  selectedText: string
): Promise<APIResult<ChatResponse>> {
  const request: GroundedChatRequest = {
    question,
    selected_text: selectedText,
  };

  const response = await apiClient.post<ChatResponse>(
    API_ENDPOINTS.CHAT_GROUNDED, // POST /chat/grounded
    request
  );

  return { success: true, data: response.data };
}
```

## Testing the Fixes

### Test 1: Verify Timeout Increase
```bash
# Terminal 1: Start backend
cd backend
uv run uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd my-website
npm run start

# Browser: Ask a complex question
# Should NOT timeout before 120 seconds
```

### Test 2: Text Selection Feature
1. Navigate to any page on http://localhost:3000
2. Highlight a paragraph (at least 10 characters)
3. Open chat widget (💬 button)
4. **Expected:** Blue box appears showing selected text
5. Type question: "Summarize this"
6. **Expected:** Answer based only on selection
7. **Expected:** Selection preview disappears after response

### Test 3: Clear Selection
1. Select text
2. Open chat widget
3. Click [×] button in the blue preview box
4. **Expected:** Preview disappears immediately
5. **Expected:** Next question uses global mode (not grounded)

## Troubleshooting

### Issue: Selected text not showing in chat widget

**Possible Causes:**
1. Selected text is <10 characters (minimum threshold)
2. Selection was cleared before opening widget
3. Console errors preventing SelectionContext from working

**Debug Steps:**
```javascript
// Open browser console (F12)
// After selecting text, check:
window.getSelection().toString()
// Should show your selected text

// Check if context is working:
// Look for console log:
// "[SelectionContext] Text selected: ..."
```

### Issue: Still getting timeout after 120 seconds

**Possible Causes:**
1. Backend is actually taking >2 minutes (check backend logs)
2. Backend indexing not completed yet
3. Qdrant or OpenAI API slow/unavailable

**Solutions:**
1. **Check backend logs:**
   ```
   INFO: Processing chat request: ...
   INFO: Chat response generated successfully (latency: X.XXs)
   ```

2. **Verify indexing is complete:**
   ```bash
   curl -X POST http://localhost:8000/index
   # Wait for status: "completed"
   ```

3. **Check backend health:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy","qdrant_connected":true}
   ```

4. **If still slow, increase timeout further:**
   ```typescript
   // my-website/src/utils/config.ts
   timeout: 180000, // 3 minutes
   ```

### Issue: Timeout on first query only

**Explanation:** This is normal! The first query might be slower because:
- Embedding model needs to load (fastembed)
- Qdrant collection needs to be loaded into memory
- OpenAI API cold start

**Solution:** This is expected behavior. Subsequent queries should be faster (<3 seconds).

## Performance Optimization Tips

### Backend Optimizations

1. **Use smaller embedding model** (if accuracy is acceptable):
   ```python
   # backend/app/embeddings.py
   # Change to faster model
   model_name = "BAAI/bge-small-en-v1.5"  # Current (fast)
   # vs
   model_name = "BAAI/bge-base-en-v1.5"   # More accurate but slower
   ```

2. **Reduce retrieval chunks** (if response quality is acceptable):
   ```python
   # backend/app/rag.py
   # Reduce from 5 to 3 chunks
   limit=3  # Faster retrieval
   ```

3. **Use faster LLM** (for development):
   ```python
   # backend/app/llm.py
   model = "gpt-3.5-turbo"  # Faster, cheaper
   # vs
   model = "gpt-4"          # Slower, more accurate
   ```

### Frontend Optimizations

1. **Show loading progress:**
   - Current: Just shows "..." animation
   - Enhancement: Show elapsed time or progress bar

2. **Cache responses:**
   - Store recent Q&A pairs in localStorage
   - Return cached answer if same question asked again

## Files Modified

| File | Change | Purpose |
|------|--------|---------|
| `my-website/src/utils/config.ts` | Timeout: 30s → 120s | Fix timeout errors |
| `my-website/src/components/ChatWidget/ChatWidget.tsx` | Added selected text preview | Show selection visually |
| `my-website/src/components/ChatWidget/styles.module.css` | Added preview styles | Style the preview box |

## Related Documentation

- **Text Selection Implementation:** `my-website/src/theme/Root.tsx`
- **API Integration:** `my-website/src/utils/api.ts`
- **Backend Grounded Endpoint:** `backend/app/routes.py` (line 123)
- **CORS Fix:** `CORS_FIX_SUMMARY.md`
- **Integration Guide:** `my-website/INTEGRATION_SUMMARY.md`
- **Testing Guide:** `TESTING_GUIDE.md`

## Visual Preview

### Before Fix:
```
[Chat Widget]
┌────────────────────────┐
│ 📚 Physical AI Assistant│
├────────────────────────┤
│ Messages...            │
│                        │
├────────────────────────┤
│ [Type message...]   ➤  │
└────────────────────────┘
```
*No indication that text was selected!*

### After Fix:
```
[Chat Widget]
┌────────────────────────┐
│ 📚 Physical AI Assistant│
├────────────────────────┤
│ Messages...            │
│                        │
├────────────────────────┤
│ ╔════════════════════╗ │
│ ║ 🎯 Selected Text: ✕║ │
│ ║ ROS2 provides...   ║ │
│ ║ 150 characters     ║ │
│ ╚════════════════════╝ │
├────────────────────────┤
│ [Type message...]   ➤  │
└────────────────────────┘
```
*Clear visual feedback!*

---

## Summary

✅ **Timeout Fixed:** Increased from 30s to 120s
✅ **Text Selection Visible:** Blue preview box with selected text
✅ **Clear Selection:** [×] button to remove selection
✅ **Auto-clear:** Selection clears after getting answer
✅ **Character Count:** Shows how much text selected
✅ **Truncation:** Shows first 150 chars if longer

**Status:** Ready for testing! 🚀

**Next Steps:**
1. Rebuild frontend (in progress)
2. Restart both backend and frontend
3. Test text selection feature
4. Verify no more timeouts
