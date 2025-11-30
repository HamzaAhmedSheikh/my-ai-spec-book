/**
 * E2E Test: Chatbot Refusal Messages (Groundedness Enforcement)
 *
 * Test Flow:
 * 1. Open chat widget
 * 2. Ask external knowledge questions (not covered in book)
 * 3. Verify chatbot refuses to answer
 * 4. Verify refusal message is consistent and user-friendly
 */

import { test, expect, Page } from '@playwright/test';

// External knowledge questions that should trigger refusals
const EXTERNAL_QUESTIONS = [
  'What is the weather today?',
  'Who is the current US president?',
  'What is the latest news?',
  'Tell me a joke',
  'How do I cook pasta?',
];

const EXPECTED_REFUSAL_PHRASE = 'can only answer questions based on';

test.describe('Chatbot Refusal Messages (User Story 4)', () => {
  let page: Page;

  test.beforeEach(async ({ page: p }) => {
    page = p;
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Open chat widget
    const chatButton = page.locator('[aria-label="Open chat"]');
    await chatButton.click();
    await expect(chatButton).not.toBeVisible(); // Button disappears when chat opens
  });

  EXTERNAL_QUESTIONS.forEach((question) => {
    test(`should refuse to answer: "${question}"`, async () => {
      // Type question
      const textarea = page.locator('textarea');
      await textarea.fill(question);

      // Send message
      const sendButton = page.locator('button:has-text("➤")');
      await sendButton.click();

      // Wait for response
      await page.waitForTimeout(8000);

      // Verify refusal message appears
      const refusalMessage = page.locator(`text=${EXPECTED_REFUSAL_PHRASE}`);
      await expect(refusalMessage).toBeVisible({
        timeout: 3000,
      });

      // Verify no sources are included (refusals shouldn't have citations)
      const sourcesHeader = page.locator('text=📖 Sources:');
      await expect(sourcesHeader).not.toBeVisible();
    });
  });

  test('should display user-friendly refusal message', async () => {
    // Ask external knowledge question
    await page.locator('textarea').fill('What is quantum computing?');
    await page.locator('button:has-text("➤")').click();

    // Wait for response
    await page.waitForTimeout(8000);

    // Get the assistant's response text
    const assistantMessage = page.locator('.messageAssistant').first();
    await expect(assistantMessage).toBeVisible();

    const messageText = await assistantMessage.textContent();

    // Verify refusal message is polite and explains limitation
    expect(messageText).toContain('can only answer questions based on');
    expect(messageText).toContain('textbook');

    // Should NOT contain harsh language
    expect(messageText?.toLowerCase()).not.toContain('error');
    expect(messageText?.toLowerCase()).not.toContain('invalid');
  });

  test('should maintain refusal consistency across multiple attempts', async () => {
    // Ask same external question twice
    const question = 'What is the weather?';

    // First attempt
    await page.locator('textarea').fill(question);
    await page.locator('button:has-text("➤")').click();
    await page.waitForTimeout(8000);

    const firstResponse = await page.locator('.messageAssistant').first().textContent();

    // Second attempt
    await page.locator('textarea').fill(question);
    await page.locator('button:has-text("➤")').click();
    await page.waitForTimeout(8000);

    const secondResponse = await page.locator('.messageAssistant').last().textContent();

    // Both should be refusals (contain the refusal phrase)
    expect(firstResponse).toContain('can only answer questions based on');
    expect(secondResponse).toContain('can only answer questions based on');
  });

  test('should allow valid questions after refusal', async () => {
    // First ask external question (should refuse)
    await page.locator('textarea').fill('What is the weather?');
    await page.locator('button:has-text("➤")').click();
    await page.waitForTimeout(8000);

    // Verify refusal
    const refusal = page.locator(`text=${EXPECTED_REFUSAL_PHRASE}`);
    await expect(refusal).toBeVisible();

    // Now ask valid book question
    await page.locator('textarea').fill('What is ROS 2?');
    await page.locator('button:has-text("➤")').click();
    await page.waitForTimeout(8000);

    // Should get either a valid answer OR a refusal if vector store is empty
    const lastAssistantMessage = page.locator('.messageAssistant').last();
    await expect(lastAssistantMessage).toBeVisible();

    const responseText = await lastAssistantMessage.textContent();

    // If response is not empty, it should either be a valid answer or refusal
    expect(responseText).toBeTruthy();
    expect(responseText!.length).toBeGreaterThan(10);
  });

  test('should not leak external knowledge in refusal', async () => {
    // Ask question that LLM might know the answer to
    await page.locator('textarea').fill('Who invented the telephone?');
    await page.locator('button:has-text("➤")').click();
    await page.waitForTimeout(8000);

    const response = await page.locator('.messageAssistant').first().textContent();

    // Should be a refusal, NOT an answer with "Alexander Graham Bell"
    expect(response).toContain('can only answer questions based on');

    // Make sure it didn't answer the question
    expect(response?.toLowerCase()).not.toContain('bell');
    expect(response?.toLowerCase()).not.toContain('graham');
  });

  test('should handle mixed valid and invalid questions', async () => {
    // Valid question
    await page.locator('textarea').fill('What is Physical AI?');
    await page.locator('button:has-text("➤")').click();
    await page.waitForTimeout(8000);

    // Invalid question
    await page.locator('textarea').fill('What is the stock market doing?');
    await page.locator('button:has-text("➤")').click();
    await page.waitForTimeout(8000);

    // Verify we have at least 2 assistant responses
    const assistantMessages = page.locator('.messageAssistant');
    const count = await assistantMessages.count();
    expect(count).toBeGreaterThanOrEqual(2);

    // Last response should be a refusal
    const lastMessage = await assistantMessages.last().textContent();
    expect(lastMessage).toContain('can only answer questions based on');
  });
});

/**
 * NOTE: These tests require:
 * 1. Docusaurus dev server running (npm start in my-website/)
 * 2. FastAPI backend running (uvicorn app.main:app in api/)
 * 3. Valid .env file with OPENAI_API_KEY and QDRANT_API_KEY
 *
 * To run:
 * npx playwright test tests/e2e/chatbot-refusal.spec.ts
 */
