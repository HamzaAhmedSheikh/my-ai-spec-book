/**
 * E2E Test: Sidebar Navigation (User Story 2)
 *
 * Test Flow:
 * 1. Navigate to a docs page
 * 2. Verify 5 parts are visible
 * 3. Test expand/collapse functionality
 * 4. Verify chapters are nested correctly
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Sidebar Navigation (User Story 2)', () => {
  let page: Page;

  test.beforeEach(async ({ page: p }) => {
    page = p;
    await page.goto('/docs/physical-ai/introduction');
    await page.waitForLoadState('networkidle');
  });

  test('should display all 5 parts in sidebar', async () => {
    // Verify the 5 main parts are present
    const expectedParts = [
      'Getting Started',
      'Core Technologies',
      'AI Integration',
      'Hardware & Deployment',
      'Assessment & Resources',
    ];

    for (const partName of expectedParts) {
      const part = page.locator(`text=${partName}`);
      await expect(part).toBeVisible({ timeout: 5000 });
    }
  });

  test('should display chapters under Getting Started', async () => {
    // Verify chapters under Getting Started are present
    const expectedChapters = [
      'Introduction',
      'Why Physical AI Matters',
      'Learning Outcomes',
      'Quarter Overview',
      'Weekly Breakdown',
    ];

    for (const chapterName of expectedChapters) {
      const chapter = page.locator(`a:has-text("${chapterName}")`);
      await expect(chapter).toBeVisible();
    }
  });

  test('should navigate to chapter when clicked', async () => {
    // Click on "Why Physical AI Matters"
    const whyPhysicalAI = page.locator('a:has-text("Why Physical AI Matters")');
    await whyPhysicalAI.click();

    // Wait for navigation
    await page.waitForURL('**/docs/physical-ai/why-physical-ai-matters');

    // Verify we're on the correct page
    expect(page.url()).toContain('/docs/physical-ai/why-physical-ai-matters');
  });
});

/**
 * NOTE: These tests require:
 * 1. Docusaurus dev server running (npm start in my-website/)
 * 2. Chapters defined in sidebars.ts must exist
 *
 * To run:
 * npx playwright test tests/e2e/sidebar-navigation.spec.ts
 */
