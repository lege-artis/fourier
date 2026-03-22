// Playwright configuration — local Chrome (primary) + Firefox (crosscheck)
// ThinkPad: Chrome = dev test target | Firefox = crosscheck
// MacBook:  Safari via separate config (safari-playwright.config.js)

const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './src',
  testMatch: ['**/*.e2e.{js,jsx,ts,tsx}', '**/*.browser.{js,jsx,ts,tsx}'],
  timeout: 30_000,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['list'],
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    // ── Primary: Chrome on Windows (ThinkPad dev target) ─────────────────────
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',       // use installed local Chrome if available
        launchOptions: {
          executablePath: process.env.CHROME_PATH || undefined,  // override with local install path
        },
      },
    },

    // ── Crosscheck: Firefox ───────────────────────────────────────────────────
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        launchOptions: {
          executablePath: process.env.FIREFOX_PATH || undefined, // override with local install path
        },
      },
    },

    // ── Mobile crosscheck (Chrome Android emulation) ──────────────────────────
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  // Local dev server — start React before running browser tests
  webServer: {
    command: 'npm start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
});
