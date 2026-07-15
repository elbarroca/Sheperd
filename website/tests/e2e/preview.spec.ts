import { expect, test } from "@playwright/test";

test("renders the Preview contract and working navigation", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Start with the record.");
  await expect(page.locator("h1")).toHaveCount(1);
  await expect(page.locator("form, input[type=file], iframe")).toHaveCount(0);
  await expect(page.locator('a[href^="mailto:"], a[href*="typeform"]')).toHaveCount(0);

  const cta = page.getByRole("link", { name: "Review requirements" }).first();
  await expect(cta).toHaveAttribute("href", "#review-requirements");
  await cta.click();
  await expect(page).toHaveURL(/#review-requirements$/);
  await expect(page.getByRole("heading", { name: "Build the review checklist." })).toBeVisible();
});

test("exposes Preview metadata and no indexing controls", async ({ page, request }) => {
  const response = await request.get("/");
  expect(response.headers()["x-robots-tag"]).toBe("noindex, nofollow, noarchive");
  expect(response.headers()["x-content-type-options"]).toBe("nosniff");
  expect(response.headers()["x-frame-options"]).toBe("DENY");
  expect(response.headers()["content-security-policy"]).toContain("form-action 'none'");
  expect(response.headers()["content-security-policy"]).not.toContain("'unsafe-eval'");

  await page.goto("/");
  await expect(page.locator('meta[name="robots"]')).toHaveAttribute("content", /noindex/);
  await expect(page.locator('link[rel="canonical"]')).toHaveCount(0);
  await expect(page.locator('script[type="application/ld\+json"]')).toHaveCount(0);

  const robots = await request.get("/robots.txt");
  expect(await robots.text()).toContain("Disallow: /");
  const sitemap = await request.get("/sitemap.xml");
  expect(await sitemap.text()).not.toContain("<url>");
});

test("supports disclosure interactions and keyboard focus", async ({ page }) => {
  await page.goto("/");
  const payment = page.getByRole("button", { name: /Payment record/ });
  await payment.focus();
  await expect(payment).toBeFocused();
  await payment.press("Enter");
  await expect(payment).toHaveAttribute("aria-expanded", "true");
  await expect(page.locator(".evidence-disclosure-panel")).toContainText(
    "Was the charge paid",
  );
});

test("exposes hero evidence detail by focus and touch-safe activation", async ({ page }) => {
  await page.goto("/");
  const billing = page.getByRole("button", { name: "Billing facts" });
  const detail = page.locator("#hero-evidence-detail-0");

  await expect(billing).toHaveAttribute("aria-pressed", "false");
  await billing.focus();
  await expect(detail).toHaveCSS("opacity", "1");
  await billing.click();
  await expect(billing).toHaveAttribute("aria-pressed", "true");
  await expect(detail).toHaveCSS("opacity", "1");
});

test("renders legal Preview notices and a noindex 404", async ({ page }) => {
  await page.goto("/privacy");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Preview Data Notice");
  await page.goto("/terms");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Preview Use Notice");
  const response = await page.goto("/missing-preview-route");
  expect(response?.status()).toBe(404);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Record not found.");
  await expect(page.locator('meta[name="robots"]').first()).toHaveAttribute(
    "content",
    /noindex/,
  );
});

test("does not issue third-party requests or write browser storage", async ({ page }) => {
  const thirdPartyRequests: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (!['127.0.0.1', 'localhost'].includes(url.hostname)) {
      thirdPartyRequests.push(request.url());
    }
  });

  await page.goto("/");
  await page.waitForLoadState("networkidle");
  expect(thirdPartyRequests).toEqual([]);
  expect(await page.evaluate(() => ({
    cookies: document.cookie,
    local: localStorage.length,
    session: sessionStorage.length,
  }))).toEqual({ cookies: "", local: 0, session: 0 });
});

test("keeps the core content available without JavaScript", async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(page.locator(".no-script-list li")).toHaveCount(5);
  await expect(
    page.locator(".evidence-disclosure-trigger:visible"),
  ).toHaveCount(0);
  await expect(page.getByRole("link", { name: "Review requirements" }).first()).toHaveAttribute(
    "href",
    "#review-requirements",
  );
  await context.close();
});

test("honors reduced-motion preference", async ({ browser }) => {
  const context = await browser.newContext({ reducedMotion: "reduce" });
  const page = await context.newPage();
  await page.goto("/");
  const finalStateSelectors = [
    ".container-module",
    ".relation-line",
    ".section-reveal",
  ];

  for (const selector of finalStateSelectors) {
    await expect(page.locator(selector).first()).toBeVisible();
    await expect(page.locator(selector).first()).toHaveCSS("transform", "none");
  }

  const cta = page.getByRole("link", { name: "Review requirements" }).first();
  await cta.dispatchEvent("pointerdown");
  await expect(cta).toHaveCSS("transform", "none");

  const payment = page.getByRole("button", { name: /Payment record/ });
  await payment.focus();
  await payment.press("Enter");
  await expect(page.locator(".evidence-disclosure-panel")).toHaveCSS(
    "transform",
    "none",
  );
  await context.close();
});

test("keeps reflow readable at 200 percent text zoom", async ({ browser }) => {
  const context = await browser.newContext({ viewport: { width: 640, height: 900 } });
  const page = await context.newPage();
  await page.goto("/");
  await page.evaluate(() => {
    document.documentElement.style.fontSize = "200%";
  });

  const dimensions = await page.evaluate(() => ({
    documentWidth: document.documentElement.scrollWidth,
    viewportWidth: document.documentElement.clientWidth,
  }));
  expect(dimensions.documentWidth).toBeLessThanOrEqual(dimensions.viewportWidth);
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(page.getByRole("link", { name: "Review requirements" }).first()).toBeVisible();
  await context.close();
});

test("preserves content and focus in forced-colors mode", async ({ browser }) => {
  const context = await browser.newContext({ forcedColors: "active" });
  const page = await context.newPage();
  await page.goto("/");
  const cta = page.getByRole("link", { name: "Review requirements" }).first();
  await cta.focus();
  await expect(cta).toBeFocused();
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await context.close();
});

test("reports no CSP violations or console errors", async ({ page }) => {
  const errors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") {
      errors.push(message.text());
    }
  });
  await page.addInitScript(() => {
    const state = window as Window & { __cspViolations?: string[] };
    state.__cspViolations = [];
    document.addEventListener("securitypolicyviolation", (event) => {
      state.__cspViolations?.push(`${event.violatedDirective}: ${event.blockedURI}`);
    });
  });
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  const violations = await page.evaluate(
    () => (window as Window & { __cspViolations?: string[] }).__cspViolations ?? [],
  );
  expect(violations).toEqual([]);
  expect(errors).toEqual([]);
});

test("serves valid social artwork dimensions", async ({ page }) => {
  await page.goto("/opengraph-image");
  const dimensions = await page.evaluate(async () => {
    const image = new Image();
    image.src = "/opengraph-image";
    await image.decode();
    return { width: image.naturalWidth, height: image.naturalHeight };
  });
  expect(dimensions).toEqual({ width: 1200, height: 630 });
});

test("keeps every external source link safe and every image valid", async ({ page }) => {
  await page.goto("/");
  const externalLinks = page.locator('a[target="_blank"]');
  expect(await externalLinks.count()).toBeGreaterThan(0);
  for (let index = 0; index < (await externalLinks.count()); index += 1) {
    await expect(externalLinks.nth(index)).toHaveAttribute(
      "rel",
      "noopener noreferrer",
    );
  }
  const invalidImages = await page.locator("img").evaluateAll(async (images) => {
    const htmlImages = images.filter(
      (image): image is HTMLImageElement => image instanceof HTMLImageElement,
    );
    for (const image of htmlImages) {
      image.loading = "eager";
    }
    await Promise.allSettled(htmlImages.map((image) => image.decode()));
    return (
      images.length - htmlImages.length +
      htmlImages.filter((image) => !image.complete || image.naturalWidth === 0).length
    );
  });
  expect(invalidImages).toBe(0);
});

test("keeps the reading path when decorative media fails", async ({ page }) => {
  await page.route("**/_next/image?**", (route) => route.abort());
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(page.getByRole("link", { name: "Review requirements" }).first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "One charge. Three questions." })).toBeVisible();
});

test("handles long content without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 900 });
  await page.goto("/");
  await page.locator(".source-register h3").first().evaluate((heading) => {
    heading.textContent =
      "An intentionally long translated official-source heading that must wrap safely";
  });
  const dimensions = await page.evaluate(() => ({
    documentWidth: document.documentElement.scrollWidth,
    viewportWidth: document.documentElement.clientWidth,
  }));
  expect(dimensions.documentWidth).toBeLessThanOrEqual(dimensions.viewportWidth);
});

test("supports the primary path with touch input", async ({ browser }) => {
  const context = await browser.newContext({
    hasTouch: true,
    viewport: { width: 375, height: 812 },
  });
  const page = await context.newPage();
  await page.goto("/");
  const cta = page.getByRole("link", { name: "Review requirements" }).first();
  await cta.tap();
  await expect(page).toHaveURL(/#review-requirements$/);
  await context.close();
});
