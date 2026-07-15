import { expect, test } from "@playwright/test";

test("supports keyboard focus and the skip link", async ({
  browserName,
  page,
}) => {
  test.skip(
    browserName === "webkit",
    "Playwright WebKit follows the macOS links-only Tab preference; Chromium and Firefox own the deterministic keyboard assertion.",
  );
  await page.goto("/");
  await page.keyboard.press("Tab");
  const skipLink = page.getByRole("link", { name: "Skip to content" });
  await expect(skipLink).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();
});

test("uses the reduced-motion equivalent", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const hero = page.locator(".hero-copy");
  await expect(hero).toBeVisible();
  await expect(hero).toHaveCSS("opacity", "1");
  await expect(hero).toHaveCSS("transform", "none");
});

test("remains readable in forced colors", async ({ page }) => {
  await page.emulateMedia({ forcedColors: "active" });
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(
    page
      .locator(".hero-actions")
      .getByRole("link", { name: "Get a Free Invoice Audit" }),
  ).toBeVisible();
});

test("reflows at 200 percent zoom", async ({ page }) => {
  await page.setViewportSize({ width: 640, height: 900 });
  await page.goto("/");
  await page.locator("body").evaluate((body) => {
    body.style.zoom = "2";
  });
  const dimensions = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.clientWidth);
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
});

test("supports a touch CTA path", async ({ browser }) => {
  const context = await browser.newContext({
    hasTouch: true,
    isMobile: true,
    viewport: { width: 375, height: 900 },
  });
  const page = await context.newPage();
  await page.goto("/");
  await page
    .locator(".hero-actions")
    .getByRole("link", { name: "Get a Free Invoice Audit" })
    .tap();
  await expect(page.locator("#audit-form")).toBeInViewport();
  await context.close();
});

test("has no horizontal overflow at 320px", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 900 });
  await page.goto("/");
  const dimensions = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  expect(dimensions.scrollWidth).toBe(dimensions.clientWidth);
});
