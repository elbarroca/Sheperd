import { expect, test } from "@playwright/test";

const supportedViewports = [
  { width: 320, height: 900 },
  { width: 390, height: 900 },
  { width: 768, height: 1024 },
  { width: 1440, height: 1000 },
  { width: 1920, height: 1080 },
] as const;

test("pauses and resumes the hero scene through its accessible control", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });

  const scene = page.getByTestId("hero-scene");
  const pauseButton = page.getByRole("button", { name: "Pause animation" });
  await expect(scene).toHaveAttribute("data-motion", "running");
  await expect(pauseButton).toBeVisible();

  await pauseButton.click();
  await expect(scene).toHaveAttribute("data-motion", "paused");
  await expect(
    page.getByRole("button", { name: "Resume animation" }),
  ).toBeVisible();

  await page.getByRole("button", { name: "Resume animation" }).click();
  await expect(scene).toHaveAttribute("data-motion", "running");
  await expect(
    page.getByRole("button", { name: "Pause animation" }),
  ).toBeVisible();
});

test("keeps ambient motion paused when reduced motion is requested", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/", { waitUntil: "networkidle" });

  await expect(page.getByTestId("hero-scene")).toHaveAttribute(
    "data-motion",
    "paused",
  );
  await expect(
    page.getByRole("button", { name: "Motion off" }),
  ).toBeDisabled();
  await expect(page.locator(".hero-fog")).toHaveCSS("animation-name", "none");
  await expect(page.locator(".hero-light")).toHaveCSS("animation-name", "none");
});

test("pauses ambient motion while the document is hidden", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" });
  const scene = page.getByTestId("hero-scene");
  await expect(scene).toHaveAttribute("data-motion", "running");

  await page.evaluate(() => {
    Object.defineProperty(document, "hidden", {
      configurable: true,
      get: () => true,
    });
    Object.defineProperty(document, "visibilityState", {
      configurable: true,
      get: () => "hidden",
    });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await expect(scene).toHaveAttribute("data-motion", "paused");

  await page.evaluate(() => {
    Object.defineProperty(document, "hidden", {
      configurable: true,
      get: () => false,
    });
    Object.defineProperty(document, "visibilityState", {
      configurable: true,
      get: () => "visible",
    });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await expect(scene).toHaveAttribute("data-motion", "running");
});

test("pauses and resumes ambient motion as the hero leaves and re-enters view", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });
  const scene = page.getByTestId("hero-scene");
  await expect(scene).toHaveAttribute("data-motion", "running");

  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await expect
    .poll(async () => scene.getAttribute("data-motion"))
    .toBe("paused");

  await page.evaluate(() => window.scrollTo(0, 0));
  await expect
    .poll(async () => scene.getAttribute("data-motion"))
    .toBe("running");
});

test("uses a native details menu on mobile", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 900 });
  await page.goto("/", { waitUntil: "networkidle" });

  const navigation = page.locator('details:has(summary[aria-label="Navigation menu"])');
  const summary = navigation.locator('summary[aria-label="Navigation menu"]');
  await expect(summary).toBeVisible();
  await expect(summary).toHaveAttribute("aria-label", "Navigation menu");
  await summary.click();
  await expect(navigation).toHaveAttribute("open", "");
  await expect(navigation.locator('a[href="#process"]')).toBeVisible();
  await expect(navigation.locator('a[href="#evidence"]')).toBeVisible();
  await expect(navigation.locator('a[href="#pilot-scope"]')).toBeVisible();
  await expect(navigation.locator('a[href="#trust"]')).toBeVisible();
});

test("keeps the page readable in forced colors", async ({ page }) => {
  await page.emulateMedia({ forcedColors: "active" });
  await page.goto("/", { waitUntil: "networkidle" });

  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(
    page.locator('a[href="/pilot"]:visible').filter({ hasText: "Request a pilot" }).first(),
  ).toBeVisible();
  await expect(page.getByTestId("hero-scene")).toBeVisible();
});

test("reflows without horizontal overflow at 200 percent zoom", async ({ page }) => {
  await page.setViewportSize({ width: 640, height: 900 });
  await page.goto("/", { waitUntil: "networkidle" });
  await page.evaluate(() => {
    document.body.style.zoom = "2";
  });

  const dimensions = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.clientWidth + 1);
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
});

test("has no horizontal overflow across the supported width range", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });

  for (const viewport of supportedViewports) {
    await page.setViewportSize(viewport);
    const dimensions = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
    }));
    expect(
      dimensions.scrollWidth,
      `horizontal overflow at ${viewport.width}px`,
    ).toBeLessThanOrEqual(dimensions.clientWidth + 1);
  }
});
