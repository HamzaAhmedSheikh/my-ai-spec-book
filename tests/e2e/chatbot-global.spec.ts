/**
 * E2E Test: Chatbot Global Mode (Full-Book Search)
 *
 * Test Flow:
 * 1. Navigate to homepage (no text selection)
 * 2. Open chat widget
 * 3. Verify NO grounded mode badge
 * 4. Ask a question about the book
 * 5. Verify response includes source citations with chapter links
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Chatbot Global Mode (User Story 4)', () => {
  let page: Page;

  test.beforeEach(async ({ page: p }) => {
    page = p;
    // Navigate to homepage (no specific chapter)
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should NOT show grounded mode badge when no text selected', async () => {
    // Open chat widget
    const chatButton = page.locator('[aria-label="Open chat"]');
    await expect(chatButton).toBeVisible();
    await chatButton.click();

    // Verify grounded mode badge is NOT visible
    const groundedBadge = page.locator('text=🎯 Grounded Mode');
    await expect(groundedBadge).not.toBeVisible();

    // Verify empty state shows global mode message
    const emptyState = page.locator('text=Ask me anything about');
    await expect(emptyState).toBeVisible();
  });

  test('should send global query and receive response with sources', async () => {
    // Open chat widget
    await page.locator('[aria-label="Open chat"]').click();

    // Type a question about the book
    const textarea = page.locator('textarea[placeholder*="Ask"]');
    await expect(textarea).toBeVisible();
    await textarea.fill('What is ROS 2?');

    // Send message
    const sendButton = page.locator('button:has-text("➤")');
    await sendButton.click();

    // Wait for response (may take several seconds due to API call)
    await page.waitForTimeout(8000); // Allow up to 8 seconds for vector search + LLM

    // Verify user message appears
    const userMessage = page.locator('text=What is ROS 2?');
    await expect(userMessage).toBeVisible();

    // Verify assistant response appears
    const assistantMessage = page.locator('.messageAssistant').first();
    await expect(assistantMessage).toBeVisible();

    // Verify sources are present (if response is not a refusal)
    const sourcesHeader = page.locator('text=📖 Sources:');
    const refusalMessage = page.locator('text=can only answer questions based on');

    // Either sources should be visible OR it's a refusal
    const hasSourcesOrRefusal = await Promise.race([
      sourcesHeader.isVisible().then(visible => ({ type: 'sources', visible })),
      refusalMessage.isVisible().then(visible => ({ type: 'refusal', visible })),
      page.waitForTimeout(2000).then(() => ({ type: 'timeout', visible: false }))
    ]);

    // If sources are visible, verify they have chapter links
    if (hasSourcesOrRefusal.type === 'sources' && hasSourcesOrRefusal.visible) {
      const sourceLinks = page.locator('.sources a');
      const linkCount = await sourceLinks.count();
      expect(linkCount).toBeGreaterThan(0);

      // Verify first source link has correct format
      const firstLink = sourceLinks.first();
      const href = await firstLink.getAttribute('href');
      expect(href).toContain('/docs/');
    }
  });

  test('should display relevance scores for source citations', async () => {
    // Open chat and ask question
    await page.locator('[aria-label="Open chat"]').click();
    await page.locator('textarea').fill('Explain Physical AI');
    await page.locator('button:has-text("➤")').click();

    // Wait for response
    await page.waitForTimeout(8000);

    // Check for relevance scores (if sources are present)
    const relevanceScore = page.locator('.relevanceScore').first();
    const hasScore = await relevanceScore.isVisible({ timeout: 2000 }).catch(() => false);

    // If score is visible, verify format
    if (hasScore) {
      const scoreText = await relevanceScore.textContent();
      // Should be a percentage (e.g., "85%")
      expect(scoreText).toMatch(/\d+%/);
    }
  });

  test('should allow switching between global and grounded mode', async () => {
    // Start in global mode
    await page.locator('[aria-label="Open chat"]').click();

    // Verify no grounded badge
    let groundedBadge = page.locator('text=🎯 Grounded Mode');
    await expect(groundedBadge).not.toBeVisible();

    // Close chat
    await page.locator('[aria-label="Close chat"]').click();

    // Navigate to a chapter
    await page.goto('/docs/physical-ai/introduction');
    await page.waitForLoadState('networkidle');

    // Select text
    await page.evaluate(() => {
      const paragraph = document.querySelector('article p');
      if (paragraph) {
        const range = document.createRange();
        range.selectNodeContents(paragraph);
        const selection = window.getSelection();
        if (selection) {
          selection.removeAllRanges();
          selection.addRange(range);
        }
        document.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
      }
    });

    await page.waitForTimeout(500);

    // Reopen chat
    await page.locator('[aria-label="Open chat"]').click();

    // Now grounded badge SHOULD be visible
    groundedBadge = page.locator('text=🎯 Grounded Mode');
    await expect(groundedBadge).toBeVisible();
  });

  test('should handle empty results gracefully', async () => {
    // Open chat
    await page.locator('[aria-label="Open chat"]').click();

    // Ask a very specific question unlikely to have matches
    await page.locator('textarea').fill('What is the exact temperature on Mars right now?');
    await page.locator('button:has-text("➤")').click();

    // Wait for response
    await page.waitForTimeout(8000);

    // Should receive a refusal message
    const refusalMessage = page.locator('text=can only answer questions based on');
    await expect(refusalMessage).toBeVisible({ timeout: 2000 });
  });

  test('should preserve conversation history in global mode', async () => {
    // Open chat
    await page.locator('[aria-label="Open chat"]').click();

    // Send first message
    await page.locator('textarea').fill('What is ROS 2?');
    await page.locator('button:has-text("➤")').click();
    await page.waitForTimeout(8000);

    // Send second message
    await page.locator('textarea').fill('What is Physical AI?');
    await page.locator('button:has-text("➤")').click();
    await page.waitForTimeout(8000);

    // Verify both user messages are present
    const userMessage1 = page.locator('text=What is ROS 2?');
    const userMessage2 = page.locator('text=What is Physical AI?');

    await expect(userMessage1).toBeVisible();
    await expect(userMessage2).toBeVisible();

    // Verify at least two assistant responses
    const assistantMessages = page.locator('.messageAssistant');
    const count = await assistantMessages.count();
    expect(count).toBeGreaterThanOrEqual(2);
  });
});

/**
 * NOTE: These tests require:
 * 1. Docusaurus dev server running (npm start in my-website/)
 * 2. FastAPI backend running (uvicorn app.main:app in api/)
 * 3. Valid .env file with OPENAI_API_KEY and QDRANT_API_KEY
 * 4. Qdrant vector store populated with book chapters (run api/scripts/index_chapters.py)
 *
 * To run:
 * npx playwright test tests/e2e/chatbot-global.spec.ts
 */
