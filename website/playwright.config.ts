import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:4173";

export default defineConfig({
  testDir: "./tests",
  testMatch: [
    "e2e/**/*.spec.ts",
    "accessibility/**/*.spec.ts",
    "visual/**/*.spec.ts",
  ],
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "off",
  },
  webServer: process.env.PLAYWRIGHT_BASE_URL
    ? undefined
    : {
        command:
          "pnpm build && pnpm start --hostname 127.0.0.1 --port 4173",
        url: baseURL,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    {
      name: "firefox",
      testIgnore: "visual/**/*.spec.ts",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      testIgnore: "visual/**/*.spec.ts",
      use: { ...devices["Desktop Safari"] },
    },
  ],
});
