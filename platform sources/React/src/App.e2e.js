/**
 * App.e2e.js — Playwright browser smoke test (CI heartbeat)
 *
 * Validates that the React app boots and renders its core UI in a real browser.
 * Runs against chromium (ThinkPad primary) and firefox (crosscheck).
 * WebServer starts automatically via playwright.config.js.
 */

const { test, expect } = require('@playwright/test');

test.describe('React app smoke test', () => {
  test('page title is set correctly', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/React Hello World Test/i);
  });

  test('main heading renders', async ({ page }) => {
    await page.goto('/');
    await expect(
      page.getByRole('heading', { name: /React Hello World Test/i })
    ).toBeVisible();
  });

  test('increment button is interactive', async ({ page }) => {
    await page.goto('/');
    const btn = page.getByRole('button', { name: /increment/i });
    await expect(btn).toBeVisible();
    await btn.click();
    await expect(page.getByText(/counter: 1/i).first()).toBeVisible();
  });
});
