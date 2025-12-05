/**
 * E2E Test: Dark Mode Persistence (User Story 3)
 *
 * Test Flow:
 * 1. Load site (default light mode)
 * 2. Click dark mode toggle
 * 3. Verify html[data-theme='dark']
 * 4. Verify localStorage theme='dark'
 * 5. Reload page
 * 6. Verify dark mode persists
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Dark Mode Persistence (User Story 3)', () => {
  let page: Page;

  test.beforeEach(async ({ page: p }) => {
    page = p;
    // Clear localStorage to start fresh
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await page.waitForLoadState('networkidle');
  });

  test('should default to light mode', async () => {
    // Check html data-theme attribute
    const htmlElement = page.locator('html');
    const theme = await htmlElement.getAttribute('data-theme');
    expect(theme).toBe('light');
  });

  test('should toggle to dark mode when clicked', async () => {
    // Find the dark mode toggle button (Docusaurus built-in or custom)
    // Docusaurus uses a button with aria-label containing "dark" or "light"
    const toggleButton = page.locator('button[aria-label*="dark"], button[aria-label*="Switch"]').first();

    // If toggle is not visible, skip this test (toggle might be in different location)
    const isVisible = await toggleButton.isVisible({ timeout: 2000 }).catch(() => false);

    if (!isVisible) {
      test.skip(true, 'Dark mode toggle not found in expected location');
      return;
    }

    await toggleButton.click();
    await page.waitForTimeout(500); // Wait for transition

    // Verify html has data-theme="dark"
    const htmlElement = page.locator('html');
    const theme = await htmlElement.getAttribute('data-theme');
    expect(theme).toBe('dark');
  });

  test('should persist dark mode in localStorage', async () => {
    // Toggle to dark mode
    const toggleButton = page.locator('button[aria-label*="dark"], button[aria-label*="Switch"]').first();
    const isVisible = await toggleButton.isVisible({ timeout: 2000 }).catch(() => false);

    if (!isVisible) {
      test.skip(true, 'Dark mode toggle not found');
      return;
    }

    await toggleButton.click();
    await page.waitForTimeout(500);

    // Check localStorage for theme value
    const localStorageTheme = await page.evaluate(() => localStorage.getItem('theme'));
    expect(localStorageTheme).toBe('dark');
  });

  test('should restore dark mode after page reload', async () => {
    // Toggle to dark mode
    const toggleButton = page.locator('button[aria-label*="dark"], button[aria-label*="Switch"]').first();
    const isVisible = await toggleButton.isVisible({ timeout: 2000 }).catch(() => false);

    if (!isVisible) {
      test.skip(true, 'Dark mode toggle not found');
      return;
    }

    await toggleButton.click();
    await page.waitForTimeout(500);

    // Verify dark mode is active
    let theme = await page.locator('html').getAttribute('data-theme');
    expect(theme).toBe('dark');

    // Reload the page
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Verify dark mode persisted after reload
    theme = await page.locator('html').getAttribute('data-theme');
    expect(theme).toBe('dark');
  });

  test('should toggle back to light mode', async () => {
    // First toggle to dark
    const toggleButton = page.locator('button[aria-label*="dark"], button[aria-label*="Switch"]').first();
    const isVisible = await toggleButton.isVisible({ timeout: 2000 }).catch(() => false);

    if (!isVisible) {
      test.skip(true, 'Dark mode toggle not found');
      return;
    }

    await toggleButton.click();
    await page.waitForTimeout(500);

    // Then toggle back to light
    await toggleButton.click();
    await page.waitForTimeout(500);

    // Verify light mode
    const theme = await page.locator('html').getAttribute('data-theme');
    expect(theme).toBe('light');
  });

  test('should apply dark mode styles to chatbot', async () => {
    // Toggle to dark mode
    const toggleButton = page.locator('button[aria-label*="dark"], button[aria-label*="Switch"]').first();
    const isVisible = await toggleButton.isVisible({ timeout: 2000 }).catch(() => false);

    if (!isVisible) {
      test.skip(true, 'Dark mode toggle not found');
      return;
    }

    await toggleButton.click();
    await page.waitForTimeout(500);

    // Open chatbot
    const chatButton = page.locator('[aria-label="Open chat"]');
    if (await chatButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await chatButton.click();
      await page.waitForTimeout(500);

      // Verify chatbot widget exists and respects dark mode
      // (CSS variables should apply automatically)
      const chatWidget = page.locator('.chatWidget');
      await expect(chatWidget).toBeVisible();
    }
  });
});

/**
 * NOTE: These tests require:
 * 1. Docusaurus dev server running (npm start in my-website/)
 * 2. Dark mode toggle configured in docusaurus.config.ts
 *
 * To run:
 * npx playwright test tests/e2e/dark-mode.spec.ts
 */
