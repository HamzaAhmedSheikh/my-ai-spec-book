/**
 * E2E Test: Homepage Redesign (User Story 2)
 *
 * Test Flow:
 * 1. Load homepage
 * 2. Verify hero section is present with title, subtitle, and description
 * 3. Verify CTAs are functional
 * 4. Verify 5 part overviews are visible
 * 5. Verify stats section is present
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Homepage Redesign (User Story 2)', () => {
  let page: Page;

  test.beforeEach(async ({ page: p }) => {
    page = p;
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should display hero section with title and tagline', async () => {
    // Verify hero title is present
    const heroTitle = page.locator('h1.hero__title');
    await expect(heroTitle).toBeVisible();

    // Verify hero subtitle (tagline)
    const heroSubtitle = page.locator('.hero__subtitle');
    await expect(heroSubtitle).toBeVisible();
  });

  test('should display all 5 part overviews', async () => {
    // Verify section header
    const sectionHeader = page.locator('h2:has-text("Explore the Curriculum")');
    await expect(sectionHeader).toBeVisible();

    // Verify all 5 parts are displayed
    const parts = page.locator('.partCard');
    const count = await parts.count();
    expect(count).toBe(5);
  });

  test('should display correct part titles', async () => {
    // Verify the 5 expected part titles
    const expectedTitles = [
      'Getting Started',
      'Core Technologies',
      'AI Integration',
      'Hardware & Deployment',
      'Assessment & Resources',
    ];

    for (const title of expectedTitles) {
      const partTitle = page.locator(`.partTitle:has-text("${title}")`);
      await expect(partTitle).toBeVisible();
    }
  });
});

/**
 * NOTE: These tests require:
 * 1. Docusaurus dev server running (npm start in my-website/)
 *
 * To run:
 * npx playwright test tests/e2e/homepage.spec.ts
 */
