import { expect, test, type Locator } from "@playwright/test";

const HERO_TITLE = "Recover the D&D money hiding in your invoices.";
const VIDEO_PLAYBACK_TIMEOUT_MS = 15_000;
const VIDEO_FRAME_TIMEOUT_MS = 5_000;
const REVEAL_ACTIVE_TIMEOUT_MS = 2_000;
const REVEAL_SETTLED_TIMEOUT_MS = 3_000;
const supportedViewports = [
  { width: 320, height: 900 },
  { width: 390, height: 900 },
  { width: 768, height: 1024 },
  { width: 1440, height: 1000 },
  { width: 1920, height: 1080 },
] as const;

async function waitForVideoPlayback(video: Locator): Promise<void> {
  await expect
    .poll(
      async () =>
        video.evaluate((element) => {
          const media = element as HTMLVideoElement;
          return { currentTime: media.currentTime, paused: media.paused };
        }),
      { timeout: VIDEO_PLAYBACK_TIMEOUT_MS },
    )
    .toMatchObject({ paused: false });

  const initialTime = await video.evaluate(
    (element) => (element as HTMLVideoElement).currentTime,
  );
  await expect
    .poll(
      async () =>
        video.evaluate((element) => (element as HTMLVideoElement).currentTime),
      { timeout: VIDEO_FRAME_TIMEOUT_MS },
    )
    .toBeGreaterThan(initialTime);
}

test("renders a full width borderless video hero without motion controls", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });

  const scene = page.getByTestId("hero-scene");
  const video = scene.getByTestId("hero-video");
  await expect(scene).toHaveAttribute("data-motion", "running");
  await expect(video).toBeVisible();
  await expect(video).toHaveJSProperty("autoplay", true);

  const metrics = await scene.evaluate((element) => {
    const heroScene = element as HTMLElement;
    const video = heroScene.querySelector<HTMLVideoElement>(
      '[data-testid="hero-video"]',
    );
    if (!video) {
      throw new Error("The hero video is missing");
    }

    const rect = heroScene.getBoundingClientRect();
    const styles = getComputedStyle(heroScene);
    const sources = Array.from(video.querySelectorAll("source"), (source) =>
      new URL(source.src, document.baseURI).pathname,
    );

    return {
      borderBottom: styles.borderBottomWidth,
      borderLeft: styles.borderLeftWidth,
      borderRight: styles.borderRightWidth,
      borderTop: styles.borderTopWidth,
      buttons: heroScene.querySelectorAll("button").length,
      left: rect.left,
      right: rect.right,
      viewportWidth: document.documentElement.clientWidth,
      width: rect.width,
      video: {
        ariaHidden: video.getAttribute("aria-hidden"),
        autoplay: video.autoplay,
        controls: video.controls,
        loop: video.loop,
        muted: video.muted,
        playsInline: video.hasAttribute("playsinline"),
        sources,
      },
    };
  });

  expect(metrics.left).toBeLessThanOrEqual(1);
  expect(metrics.right).toBeGreaterThanOrEqual(metrics.viewportWidth - 1);
  expect(metrics.width).toBeGreaterThanOrEqual(metrics.viewportWidth - 1);
  expect(metrics.borderBottom).toBe("0px");
  expect(metrics.borderLeft).toBe("0px");
  expect(metrics.borderRight).toBe("0px");
  expect(metrics.borderTop).toBe("0px");
  expect(metrics.buttons).toBe(0);
  expect(metrics.video).toMatchObject({
    ariaHidden: "true",
    autoplay: true,
    controls: false,
    loop: true,
    muted: true,
    playsInline: true,
  });
  expect(metrics.video.sources).toEqual(
    expect.arrayContaining([
      "/media/recovery-terminal-loop.webm",
      "/media/recovery-terminal-loop.mp4",
    ]),
  );
  await expect(
    page.getByRole("button", { name: /pause animation|resume animation|motion off/i }),
  ).toHaveCount(0);

  await waitForVideoPlayback(video);
});

test("uses the static image and pauses the video for reduced motion", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/", { waitUntil: "networkidle" });

  const scene = page.getByTestId("hero-scene");
  const video = scene.getByTestId("hero-video");
  await expect(scene).toHaveAttribute("data-motion", "paused");
  await expect(video).toHaveJSProperty("paused", true);
  await expect(video).toHaveCSS("display", "none");
  await expect(
    scene.locator('img[src*="recovery-terminal"]'),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /pause animation|resume animation|motion off/i }),
  ).toHaveCount(0);
});

test("pauses the native hero video while the document is hidden", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });
  const scene = page.getByTestId("hero-scene");
  const video = scene.getByTestId("hero-video");
  await expect(scene).toHaveAttribute("data-motion", "running");
  await waitForVideoPlayback(video);

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
  await expect.poll(async () => video.evaluate((element) => (element as HTMLVideoElement).paused)).toBe(true);
  await expect(video).toHaveCSS("opacity", "0");

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
  await expect.poll(async () => video.evaluate((element) => (element as HTMLVideoElement).paused)).toBe(false);
});

test("pauses and resumes the native hero video as the hero leaves and re-enters view", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });
  const scene = page.getByTestId("hero-scene");
  const video = scene.getByTestId("hero-video");
  await expect(scene).toHaveAttribute("data-motion", "running");
  await waitForVideoPlayback(video);

  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await expect
    .poll(async () => scene.getAttribute("data-motion"))
    .toBe("paused");
  await expect
    .poll(async () => video.evaluate((element) => (element as HTMLVideoElement).paused))
    .toBe(true);
  await expect(video).toHaveCSS("opacity", "0");

  await page.evaluate(() => window.scrollTo(0, 0));
  await expect
    .poll(async () => scene.getAttribute("data-motion"))
    .toBe("running");
  await expect
    .poll(async () => video.evaluate((element) => (element as HTMLVideoElement).paused))
    .toBe(false);
});

test("reveals below-fold headings with WAAPI while preserving accessible names", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/", { waitUntil: "networkidle" });

  const processSection = page.locator("#process");
  const heading = page.getByRole("heading", {
    level: 2,
    name: /Your invoices\. Our next move\./i,
  });
  const headingWords = heading.locator(".scroll-heading-word");
  await expect(headingWords.first()).toHaveAttribute(
    "data-scroll-reveal-target-state",
    "pending",
  );

  await processSection.scrollIntoViewIfNeeded();
  await expect
    .poll(
      async () =>
        headingWords.evaluateAll((elements) =>
          elements.filter((element) =>
            element
              .getAnimations()
              .some((animation) => animation.playState === "running"),
          ).length,
        ),
      { timeout: REVEAL_ACTIVE_TIMEOUT_MS },
    )
    .toBeGreaterThan(0);

  await expect
    .poll(
      async () =>
        headingWords.evaluateAll((elements) =>
          elements.every(
            (element) =>
              element.getAttribute("data-scroll-reveal-target-state") ===
                "revealed" &&
              element
                .getAnimations()
                .every((animation) => animation.playState !== "running"),
          ),
        ),
      { timeout: REVEAL_SETTLED_TIMEOUT_MS },
    )
    .toBe(true);
  await expect(heading).toHaveAccessibleName("Your invoices. Our next move.");
});

test("stops active scroll reveals and shows content when reduced motion changes", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/", { waitUntil: "networkidle" });

  const processSection = page.locator("#process");
  const firstProcessItem = processSection.locator(".process-list > li").first();
  await expect(firstProcessItem).toHaveAttribute(
    "data-scroll-reveal-state",
    "pending",
  );

  await processSection.scrollIntoViewIfNeeded();
  await expect
    .poll(
      async () =>
        firstProcessItem.evaluate((element) =>
          Array.from(element.getAnimations()).filter(
            (animation) => animation.playState === "running",
          ).length,
        ),
      { timeout: REVEAL_ACTIVE_TIMEOUT_MS },
    )
    .toBeGreaterThan(0);

  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect
    .poll(
      async () =>
        firstProcessItem.evaluate((element) => {
          const styles = getComputedStyle(element);
          return {
            opacity: styles.opacity,
            running: Array.from(element.getAnimations()).some(
              (animation) => animation.playState === "running",
            ),
            state: element.getAttribute("data-scroll-reveal-state"),
            transform: styles.transform,
            visible: element.getClientRects().length > 0,
          };
        }),
      { timeout: REVEAL_SETTLED_TIMEOUT_MS },
    )
    .toMatchObject({
      opacity: "1",
      running: false,
      state: "revealed",
      transform: "none",
      visible: true,
    });
  expect((await firstProcessItem.innerText()).trim()).not.toBe("");
});

test("keeps the recovery hero readable with JavaScript disabled", async ({
  browser,
}) => {
  const context = await browser.newContext({
    javaScriptEnabled: false,
    viewport: { width: 390, height: 844 },
  });
  const page = await context.newPage();

  await page.goto("/", { waitUntil: "domcontentloaded" });
  const scene = page.getByTestId("hero-scene");
  await expect(
    page.getByRole("heading", { level: 1, name: HERO_TITLE }),
  ).toBeVisible();
  await expect(scene.locator('img[src*="recovery-terminal"]')).toBeVisible();
  await expect(scene.locator("button")).toHaveCount(0);
  await expect(
    page.locator('a[href="/pilot"]:visible').filter({ hasText: "Request a pilot" }).first(),
  ).toBeVisible();

  const processSection = page.locator("#process");
  await processSection.scrollIntoViewIfNeeded();
  await expect(
    page.getByRole("heading", {
      level: 2,
      name: /Your invoices\. Our next move\./i,
    }),
  ).toBeVisible();
  const processList = processSection.locator(".process-list");
  await expect(processList).toBeVisible();
  expect((await processList.innerText()).trim()).not.toBe("");

  await context.close();
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
