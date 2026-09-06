import { expect, test } from "@playwright/test";

test("eases wheel input over multiple frames and preserves anchor navigation", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/", { waitUntil: "networkidle" });
  await expect(page.locator("html")).toHaveClass(/\blenis\b/);
  await page.mouse.move(350, 420);
  await page.mouse.wheel(0, 640);
  const positions = await page.evaluate(async () => {
    const samples: number[] = [];
    for (let frame = 0; frame < 30; frame += 1) {
      await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
      samples.push(Math.round(window.scrollY));
    }
    return samples;
  });
  expect(new Set(positions).size).toBeGreaterThan(4);
  expect(positions.some((position) => position > 0 && position < 600)).toBe(true);
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(600);

  await page.locator('.header-links a[href="#process"]').click();
  await expect(page).toHaveURL(/#process$/);
  await expect.poll(() => page.locator("#process").evaluate((section) =>
    Math.abs(section.getBoundingClientRect().top - Number.parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop)),
  )).toBeLessThan(3);

  await page.getByRole("link", { name: "Skip to content" }).focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();
});

test("uses native scrolling for reduced motion and pauses while hidden", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" });
  await expect(page.locator("html")).toHaveClass(/\blenis\b/);
  await page.evaluate(() => {
    Object.defineProperty(document, "visibilityState", { configurable: true, value: "hidden" });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await expect(page.locator("html")).toHaveClass(/lenis-stopped/);
  await page.evaluate(() => {
    delete (document as unknown as Record<string, unknown>).visibilityState;
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await expect(page.locator("html")).not.toHaveClass(/lenis-stopped/);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect(page.locator("html")).not.toHaveClass(/\blenis\b/);
  await page.mouse.move(350, 420);
  await page.mouse.wheel(0, 400);
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(300);
});

test("yields anchor easing to keyboard scrolling", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" });
  await expect(page.locator("html")).toHaveClass(/\blenis\b/);
  await page.locator('.header-links a[href="#process"]').click();
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(80);
  await page.keyboard.press("Home");
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeLessThan(3);
  await expect(page.locator("html")).not.toHaveClass(/lenis-scrolling/);
  expect(new URL(page.url()).hash).toBe("");
});

test("does not reclaim focus moved during anchor easing", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" });
  await expect(page.locator("html")).toHaveClass(/\blenis\b/);
  await page.locator('.header-links a[href="#process"]').click();
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(80);
  const nextLink = page.locator('.header-links a[href="#evidence"]');
  await nextLink.focus();
  await expect(page.locator("html")).not.toHaveClass(/lenis-scrolling/);
  await expect(nextLink).toBeFocused();
});

test("lets the pilot dialog scroll natively and resumes page scrolling after close", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/", { waitUntil: "networkidle" });
  await expect(page.locator("html")).toHaveClass(/\blenis\b/);
  await page.locator(".header-pilot").click();
  const dialog = page.getByRole("dialog", { name: "Request a pilot" });
  await expect(dialog).toBeVisible();
  await expect(page.locator("html")).not.toHaveClass(/\blenis\b/);
  const pageY = await page.evaluate(() => window.scrollY);
  await dialog.hover();
  await page.mouse.wheel(0, 500);
  await expect.poll(() => dialog.evaluate((element) => element.scrollTop)).toBeGreaterThan(0);
  expect(await page.evaluate(() => window.scrollY)).toBe(pageY);
  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
  await expect(page.locator("html")).toHaveClass(/\blenis\b/);
  await page.keyboard.press("PageDown");
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(pageY);
});
