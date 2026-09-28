import { expect, test } from "@playwright/test";

test("section text enters, resets offscreen and respects preference changes", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/how-it-works");
  const heading = page.getByRole("heading", { level: 1 });
  await expect(heading).toHaveClass(/recovery-enter/);
  await expect(heading).toHaveCSS("animation-name", "recovery-text-enter");
  await heading.evaluate(async (element) => {
    await Promise.all(element.getAnimations().map((animation) => animation.finished));
    const bounds = element.closest("section")!.getBoundingClientRect();
    window.scrollTo({ top: window.scrollY + bounds.top + bounds.height * 0.92, behavior: "instant" });
  });
  await expect(heading).toHaveClass(/recovery-exit/);
  await heading.evaluate(async (element) => {
    await Promise.all(element.getAnimations().map((animation) => animation.finished));
  });
  await expect(heading).toHaveClass(/recovery-exit/);
  await page.locator("footer").scrollIntoViewIfNeeded();
  await expect(heading).not.toHaveClass(/recovery-enter/);
  await heading.scrollIntoViewIfNeeded();
  await expect(heading).toHaveClass(/recovery-enter/);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect(heading).not.toHaveClass(/recovery-enter/);
  await expect(heading).toHaveCSS("opacity", "1");
});

test("keyboard skip link keeps the static hero available", async ({ page, browserName }) => {
  await page.goto("/");
  if (browserName === "webkit") {
    // macOS WebKit's default Tab preference skips links; test activation explicitly.
    await page.getByRole("link", { name: "Skip to content" }).focus();
  } else {
    await page.keyboard.press("Tab");
  }
  await expect(page.getByRole("link", { name: "Skip to content" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();
  await expect(page.locator(".hero-copy")).toBeVisible();
  await expect(page.locator(".port-story")).toHaveCount(0);
  await expect(page.locator(".hero-caption")).toHaveCount(0);
});

test("FAQ rows enter and exit with the importer section", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/");
  const row = page.locator(".recovery-faq details").first();
  await row.scrollIntoViewIfNeeded();
  await expect(row).toHaveClass(/recovery-enter/);
  await expect(row).toHaveCSS("animation-name", "recovery-faq-enter");
  await row.evaluate((element) => {
    const section = element.closest("section");
    if (!section) throw new Error("FAQ section not found");
    window.scrollTo({
      top: window.scrollY + section.getBoundingClientRect().top + section.getBoundingClientRect().height * 0.92,
      behavior: "instant",
    });
  });
  await expect(row).toHaveClass(/recovery-exit/);
});

test("reduced motion is static", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.locator(".hero-copy")).toBeVisible();
  await expect(page.locator(".port-story")).toHaveCount(0);
  await expect(page.locator(".hero-caption")).toHaveCount(0);
  await page.getByRole("button", { name: "Open navigation" }).click();
  const navigation = page.locator("#mobile-navigation");
  await expect(navigation).toBeVisible();
  await expect.poll(() => navigation.evaluate((element) =>
    element.getAnimations().filter((animation) => animation.playState === "running").length,
  )).toBe(0);
});

test("content and enquiry remain available without JavaScript", async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto("/");
  await expect(page.locator("#cfo-title")).toBeVisible();
  await expect(page.locator(".recovery-process li")).toHaveCount(4);
  await page.locator("summary").filter({ hasText: "What does it cost?" }).click();
  await expect(page.locator("details[open]")).toContainText("no upfront cost");
  await page.locator(".hero-actions").getByRole("link", { name: "Find Recoverable Value" }).click();
  await expect(page.getByRole("status")).toBeVisible();
  await context.close();
});

test("image failure does not hide the offer or CTA", async ({ page }) => {
  await page.route("**/media/recovery-port*", (route) => route.abort());
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await page.locator(".hero-actions").getByRole("link", { name: "Find Recoverable Value" }).click();
  await expect(page).toHaveURL(/\/contact$/);
});

test("primary recovery CTA animates in, on hover, and back on release", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/");
  const cta = page.locator(".hero-actions .recovery-action");
  await expect(cta).toHaveClass(/recovery-enter/);
  await cta.evaluate((element) => {
    element.addEventListener("click", (event) => event.preventDefault(), { once: true });
  });
  await cta.evaluate(async (element) => {
    await Promise.all(element.getAnimations().map((animation) => animation.finished));
  });
  await cta.hover();
  await cta.evaluate(async (element) => {
    await Promise.all(element.getAnimations().map((animation) => animation.finished));
  });
  const hoverTransform = await cta.evaluate((element) => getComputedStyle(element).transform);
  expect(hoverTransform).not.toBe("none");
  await page.mouse.down();
  await expect.poll(() => cta.evaluate((element) => element.matches(":active"))).toBe(true);
  await expect.poll(() => cta.evaluate((element) => getComputedStyle(element).transform)).not.toBe(hoverTransform);
  await page.mouse.up();
  await expect.poll(() => cta.evaluate((element) => element.matches(":active"))).toBe(false);
  await expect.poll(() => cta.evaluate((element) => getComputedStyle(element).transform)).toBe(hoverTransform);
  await expect(cta).toBeVisible();
});

test("forced colors preserves the CTA", async ({ page }) => {
  await page.emulateMedia({ forcedColors: "active" });
  await page.goto("/");
  await expect(page.locator(".hero-actions").getByRole("link", { name: "Find Recoverable Value" })).toBeVisible();
});

for (const width of [320, 375, 768, 1024, 1440, 1920]) {
  test(`no overflow or missing art at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    await page.goto("/");
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
    const image = page.locator(".recovery-hero img");
    await expect(image).toBeVisible();
    expect(await image.evaluate((element) => (element as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
    await expect(page.locator(".invoice-history-visual")).toBeVisible();
    await expect(page.locator(".invoice-history-timeline li")).toHaveCount(3);
  });
}

test("reflows at 200 percent zoom", async ({ page }) => {
  await page.setViewportSize({ width: 640, height: 900 });
  await page.goto("/");
  await page.locator("body").evaluate((body) => { body.style.zoom = "2"; });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
});
