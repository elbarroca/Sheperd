import { expect, test, type Locator, type Page } from "@playwright/test";

interface SectionSpec {
  id: string;
  selector: string;
  variant: string;
  targetSelectors: readonly string[];
  primaryTargetSelector: string;
}

interface MotionState {
  activeAnimations: number;
  opacity: number;
  transform: string;
}

interface SectionMetrics {
  height: number;
  top: number;
  viewportHeight: number;
}

const SECTION_SPECS: readonly SectionSpec[] = [
  {
    id: "intro",
    selector: "main > section.intro-section",
    variant: "intro",
    targetSelectors: [".intro-layout > *"],
    primaryTargetSelector: ".intro-layout > *:first-child",
  },
  {
    id: "process",
    selector: "main > section#process",
    variant: "process",
    targetSelectors: [".section-heading", ".process-list"],
    primaryTargetSelector: ".section-heading",
  },
  {
    id: "evidence",
    selector: "main > section#evidence",
    variant: "evidence",
    targetSelectors: [".evidence-list"],
    primaryTargetSelector: ".evidence-list",
  },
  {
    id: "story",
    selector: "main > section.story-band",
    variant: "story",
    targetSelectors: [".story-band-copy", ".story-band-image"],
    primaryTargetSelector: ".story-band-copy",
  },
  {
    id: "pilot",
    selector: "main > section#pilot-scope",
    variant: "pilot",
    targetSelectors: [".pilot-scope-copy", ".pilot-scope-list"],
    primaryTargetSelector: ".pilot-scope-copy",
  },
  {
    id: "trust",
    selector: "main > section#trust",
    variant: "trust",
    targetSelectors: [".trust-layout"],
    primaryTargetSelector: ".trust-layout",
  },
  {
    id: "closing",
    selector: "main > section.closing-cta",
    variant: "closing",
    targetSelectors: [".closing-copy"],
    primaryTargetSelector: ".closing-copy",
  },
];

const EXPECTED_SECTION_COUNT = SECTION_SPECS.length;
const ENTRY_VIEWPORT_RATIO = 0.9;
const EXIT_VIEWPORT_RATIO = 0.1;
const SURFACE_STATE_TIMEOUT_MS = 3_000;
const TRANSFORM_EPSILON = 0.01;
const POINTER_POSE_SAMPLE_COUNT = 33;
const POINTER_POSITION_TOLERANCE_PX = 1;

function findSectionSpec(id: string): SectionSpec {
  const spec = SECTION_SPECS.find((candidate) => candidate.id === id);
  if (!spec) {
    throw new Error(`Missing section test configuration for ${id}.`);
  }
  return spec;
}

function markedTargetSelector(selector: string): string {
  return `${selector}[data-section-motion-target]`;
}

function markedTargets(section: Locator, spec: SectionSpec): Locator {
  return section.locator(
    spec.targetSelectors.map(markedTargetSelector).join(", "),
  );
}

function primaryTarget(section: Locator, spec: SectionSpec): Locator {
  return section.locator(markedTargetSelector(spec.primaryTargetSelector)).first();
}

function isIdentityTransform(transform: string): boolean {
  if (transform === "none") return true;

  const match = /^matrix(3d)?\(([^)]+)\)$/u.exec(transform);
  if (!match) return false;

  const values = match[2].split(",").map(Number);
  if (match[1] === "3d") {
    const identity = [
      1, 0, 0, 0,
      0, 1, 0, 0,
      0, 0, 1, 0,
      0, 0, 0, 1,
    ];
    return (
      values.length === identity.length &&
      values.every(
        (value, index) =>
          Math.abs(value - (identity[index] ?? 0)) < TRANSFORM_EPSILON,
      )
    );
  }

  const identity = [1, 0, 0, 1, 0, 0];
  return (
    values.length === identity.length &&
    values.every(
      (value, index) =>
        Math.abs(value - (identity[index] ?? 0)) < TRANSFORM_EPSILON,
    )
  );
}

function isPlateauState(state: MotionState): boolean {
  return state.opacity >= 0.99 && isIdentityTransform(state.transform);
}

function isBoundaryState(state: MotionState): boolean {
  return state.opacity < 0.99 || !isIdentityTransform(state.transform);
}

async function readMotionStates(targets: Locator): Promise<MotionState[]> {
  return targets.evaluateAll((elements) =>
    elements.map((element) => {
      const styles = getComputedStyle(element);
      const activeAnimations = element
        .getAnimations()
        .filter((animation) => !["idle", "finished"].includes(animation.playState))
        .length;

      return {
        activeAnimations,
        opacity: Number.parseFloat(styles.opacity),
        transform: styles.transform,
      };
    }),
  );
}

async function readMotionState(target: Locator): Promise<MotionState> {
  const states = await readMotionStates(target);
  const state = states[0];
  if (!state) {
    throw new Error("The motion target state was not observed.");
  }
  return state;
}

async function readSectionMetrics(section: Locator): Promise<SectionMetrics> {
  return section.evaluate((element) => {
    const rect = element.getBoundingClientRect();
    return {
      height: rect.height,
      top: rect.top + window.scrollY,
      viewportHeight: window.innerHeight,
    };
  });
}

async function scrollInstant(page: Page, targetTop: number): Promise<void> {
  const maxScrollTop = await page.evaluate(() =>
    Math.max(0, document.documentElement.scrollHeight - window.innerHeight),
  );
  const nextTop = Math.min(Math.max(targetTop, 0), maxScrollTop);

  await page.evaluate((top) => {
    window.scrollTo({ top, behavior: "instant" as ScrollBehavior });
  }, nextTop);
  await page.evaluate(
    () => new Promise<void>((resolve) => requestAnimationFrame(() => resolve())),
  );
}

async function waitForMotionStates(
  targets: Locator,
  predicate: (state: MotionState) => boolean,
): Promise<MotionState[]> {
  let latest: MotionState[] = [];
  await expect
    .poll(
      async () => {
        latest = await readMotionStates(targets);
        return latest.length > 0 && latest.every(predicate);
      },
      { timeout: SURFACE_STATE_TIMEOUT_MS },
    )
    .toBe(true);

  if (latest.length === 0) {
    throw new Error("The section motion target states were not observed.");
  }
  return latest;
}

async function waitForMotionState(
  target: Locator,
  predicate: (state: MotionState) => boolean,
): Promise<MotionState> {
  const states = await waitForMotionStates(target, predicate);
  const state = states[0];
  if (!state) {
    throw new Error("The primary motion target state was not observed.");
  }
  return state;
}

function expectPlateauState(state: MotionState): void {
  expect(state.opacity).toBeGreaterThanOrEqual(0.99);
  expect(isIdentityTransform(state.transform)).toBe(true);
}

function expectStaticState(state: MotionState): void {
  expectPlateauState(state);
  expect(state.activeAnimations).toBe(0);
}

function expectPlateauStates(states: MotionState[]): void {
  states.forEach(expectPlateauState);
}

function expectStaticStates(states: MotionState[]): void {
  states.forEach(expectStaticState);
}

test("renders seven named section motion targets with varied computed recipes", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });

  const sections = page.locator("main > section[data-section-motion]");
  await expect(sections).toHaveCount(EXPECTED_SECTION_COUNT);

  const sectionReports = await sections.evaluateAll((elements) =>
    elements.map((element) => ({
      directChildren: Array.from(element.children).map((child) => ({
        className: child.className,
        tagName: child.tagName,
      })),
      variant: element.getAttribute("data-section-motion"),
    })),
  );
  expect(sectionReports.map(({ variant }) => variant)).toEqual(
    SECTION_SPECS.map(({ variant }) => variant),
  );
  expect(
    sectionReports.every(
      ({ directChildren }) =>
        directChildren.length === 1 &&
        directChildren[0]?.tagName === "DIV" &&
        directChildren[0].className.split(/\s+/u).includes("section-motion-surface"),
    ),
  ).toBe(true);

  for (const spec of SECTION_SPECS) {
    const section = page.locator(spec.selector);
    await expect(section).toHaveCount(1);

    for (const selector of spec.targetSelectors) {
      const unmarkedTargets = section.locator(selector);
      const marked = section.locator(markedTargetSelector(selector));
      const expectedCount = await unmarkedTargets.count();
      expect(expectedCount).toBeGreaterThan(0);
      await expect(marked).toHaveCount(expectedCount);
    }
  }

  const closingSpec = SECTION_SPECS[EXPECTED_SECTION_COUNT - 1];
  if (!closingSpec) {
    throw new Error("Closing section test configuration is missing.");
  }
  const closingSection = page.locator(closingSpec.selector);
  await expect(closingSection).toHaveAttribute(
    "data-section-motion-state",
    "static",
  );
  expectStaticStates(await readMotionStates(markedTargets(closingSection, closingSpec)));

  const sampledRecipes: string[] = [];
  for (const spec of SECTION_SPECS) {
    const section = page.locator(spec.selector);
    const target = primaryTarget(section, spec);
    const metrics = await readSectionMetrics(section);

    await scrollInstant(
      page,
      metrics.top - metrics.viewportHeight * ENTRY_VIEWPORT_RATIO,
    );
    const boundary = await waitForMotionState(target, isBoundaryState);
    await expect(section).toHaveAttribute("data-section-motion-state", "active");
    sampledRecipes.push(
      `${boundary.transform}|${boundary.opacity.toFixed(2)}`,
    );

    await scrollInstant(
      page,
      metrics.top + metrics.height / 2 - metrics.viewportHeight / 2,
    );
    expectPlateauStates(
      await waitForMotionStates(markedTargets(section, spec), isPlateauState),
    );
  }

  expect(new Set(sampledRecipes).size).toBeGreaterThanOrEqual(4);
});

test("moves process motion targets through entry, rest, exit, and reverse scroll", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });

  const spec = findSectionSpec("process");
  const section = page.locator(spec.selector);
  const targets = markedTargets(section, spec);
  const metrics = await readSectionMetrics(section);

  await scrollInstant(
    page,
    metrics.top - metrics.viewportHeight * ENTRY_VIEWPORT_RATIO,
  );
  const entry = await waitForMotionStates(targets, isBoundaryState);
  await expect(section).toHaveAttribute("data-section-motion-state", "active");
  expect(entry.every(isBoundaryState)).toBe(true);

  await scrollInstant(
    page,
    metrics.top + metrics.height / 2 - metrics.viewportHeight / 2,
  );
  const rest = await waitForMotionStates(targets, isPlateauState);
  expectPlateauStates(rest);

  await scrollInstant(
    page,
    metrics.top + metrics.height - metrics.viewportHeight * EXIT_VIEWPORT_RATIO,
  );
  const exit = await waitForMotionStates(targets, isBoundaryState);
  expect(exit.every(isBoundaryState)).toBe(true);

  await scrollInstant(
    page,
    metrics.top + metrics.height / 2 - metrics.viewportHeight / 2,
  );
  const reverseRest = await waitForMotionStates(targets, isPlateauState);
  expectPlateauStates(reverseRest);
});

test("keeps fixed companions still while marked targets animate", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" });

  const evidenceSpec = findSectionSpec("evidence");
  const evidenceSection = page.locator(evidenceSpec.selector);
  const evidenceList = primaryTarget(evidenceSection, evidenceSpec);
  const evidenceIntro = evidenceSection.locator(".evidence-intro");
  const evidenceMetrics = await readSectionMetrics(evidenceSection);

  await scrollInstant(
    page,
    evidenceMetrics.top -
      evidenceMetrics.viewportHeight * ENTRY_VIEWPORT_RATIO,
  );
  await waitForMotionState(evidenceList, isBoundaryState);
  expectPlateauState(await readMotionState(evidenceIntro));

  const storySpec = findSectionSpec("story");
  const storySection = page.locator(storySpec.selector);
  const storyCopy = storySection.locator(
    markedTargetSelector(".story-band-copy"),
  );
  const storyImage = storySection.locator(
    markedTargetSelector(".story-band-image"),
  );
  const storyMetrics = await readSectionMetrics(storySection);

  await scrollInstant(
    page,
    storyMetrics.top - storyMetrics.viewportHeight * ENTRY_VIEWPORT_RATIO,
  );
  await waitForMotionStates(
    markedTargets(storySection, storySpec),
    isBoundaryState,
  );
  const storyImageEntry = await readMotionState(storyImage);
  expect(storyImageEntry.opacity).toBeLessThan(0.99);
  expect(isIdentityTransform(storyImageEntry.transform)).toBe(true);
  expect(isBoundaryState(await readMotionState(storyCopy))).toBe(true);

  await scrollInstant(
    page,
    storyMetrics.top + storyMetrics.height / 2 - storyMetrics.viewportHeight / 2,
  );
  const storyImageRest = await waitForMotionState(storyImage, isPlateauState);
  expectPlateauState(storyImageRest);

  const trustSpec = findSectionSpec("trust");
  const trustSection = page.locator(trustSpec.selector);
  const trustLayout = primaryTarget(trustSection, trustSpec);
  const faqBlock = trustSection.locator(".faq-block");
  const trustMetrics = await readSectionMetrics(trustSection);

  await scrollInstant(
    page,
    trustMetrics.top - trustMetrics.viewportHeight * ENTRY_VIEWPORT_RATIO,
  );
  await waitForMotionState(trustLayout, isBoundaryState);
  expectPlateauState(await readMotionState(faqBlock));
});

test("resets all marked targets for reduced motion at load and at runtime", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/", { waitUntil: "networkidle" });

  const allTargets = page.locator("[data-section-motion-target]");
  await expect(allTargets).not.toHaveCount(0);
  expectStaticStates(await readMotionStates(allTargets));

  for (const spec of SECTION_SPECS) {
    await expect(page.locator(spec.selector)).toHaveAttribute(
      "data-section-motion-state",
      "static",
    );
  }

  await page.emulateMedia({ reducedMotion: "no-preference" });
  const processSpec = findSectionSpec("process");
  const processSection = page.locator(processSpec.selector);
  const processTargets = markedTargets(processSection, processSpec);
  const metrics = await readSectionMetrics(processSection);
  await scrollInstant(
    page,
    metrics.top - metrics.viewportHeight * ENTRY_VIEWPORT_RATIO,
  );
  await waitForMotionStates(processTargets, isBoundaryState);

  await page.emulateMedia({ reducedMotion: "reduce" });
  const runtimeStates = await waitForMotionStates(
    processTargets,
    (state) => isPlateauState(state) && state.activeAnimations === 0,
  );
  expectStaticStates(runtimeStates);
  await expect(processSection).toHaveAttribute(
    "data-section-motion-state",
    "static",
  );
});

test("stops marked targets while hidden and resynchronizes when visible", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/", { waitUntil: "networkidle" });

  const spec = findSectionSpec("process");
  const section = page.locator(spec.selector);
  const targets = markedTargets(section, spec);
  const metrics = await readSectionMetrics(section);
  await scrollInstant(
    page,
    metrics.top - metrics.viewportHeight * ENTRY_VIEWPORT_RATIO,
  );
  await waitForMotionStates(targets, isBoundaryState);

  await page.evaluate(() => {
    Object.defineProperty(document, "visibilityState", {
      configurable: true,
      get: () => "hidden",
    });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  const hiddenStates = await waitForMotionStates(
    targets,
    (state) => isPlateauState(state) && state.activeAnimations === 0,
  );
  expectStaticStates(hiddenStates);
  await expect(section).toHaveAttribute(
    "data-section-motion-state",
    "static",
  );

  await page.evaluate(() => {
    Object.defineProperty(document, "visibilityState", {
      configurable: true,
      get: () => "visible",
    });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await scrollInstant(
    page,
    metrics.top - metrics.viewportHeight * ENTRY_VIEWPORT_RATIO,
  );
  await waitForMotionStates(targets, isBoundaryState);
  await expect(section).toHaveAttribute("data-section-motion-state", "active");
});

test("keeps focused section CTAs and FAQ summaries visible", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" });

  const pilotSpec = findSectionSpec("pilot");
  const pilotSection = page.locator(pilotSpec.selector);
  const pilotCopy = primaryTarget(pilotSection, pilotSpec);
  await pilotCopy.locator('a[href="/pilot"]').first().evaluate((element) => {
    (element as HTMLElement).focus({ preventScroll: true });
  });
  const focusedPilotState = await waitForMotionState(
    pilotCopy,
    (state) => isPlateauState(state) && state.activeAnimations === 0,
  );
  expectStaticState(focusedPilotState);
  await expect(pilotSection).toHaveAttribute(
    "data-section-motion-state",
    "static",
  );

  const trustSpec = findSectionSpec("trust");
  const trustSection = page.locator(trustSpec.selector);
  const trustLayout = primaryTarget(trustSection, trustSpec);
  const faqSummary = trustSection.locator(".faq-block details > summary").first();
  await faqSummary.evaluate((element) => {
    (element as HTMLElement).focus({ preventScroll: true });
  });
  const focusedTrustState = await waitForMotionState(
    trustLayout,
    (state) => isPlateauState(state) && state.activeAnimations === 0,
  );
  expectStaticState(focusedTrustState);
  expectPlateauState(await readMotionState(trustSection.locator(".faq-block")));
});

test("keeps a pointer CTA stable while a marked target is transformed", async ({
  page,
}) => {
  // A tall desktop exposes the CTA while its chapter crosses the exit boundary.
  await page.setViewportSize({ width: 1440, height: 1600 });
  await page.goto("/", { waitUntil: "networkidle" });

  const pilotSpec = findSectionSpec("pilot");
  const section = page.locator(pilotSpec.selector);
  const target = primaryTarget(section, pilotSpec);
  const cta = target.locator('a[href="/pilot"]').first();
  const metrics = await readSectionMetrics(section);
  const entryStart = metrics.top - metrics.viewportHeight * ENTRY_VIEWPORT_RATIO;
  const exitEnd =
    metrics.top + metrics.height - metrics.viewportHeight * EXIT_VIEWPORT_RATIO;
  let transformedPoseFound = false;

  for (let index = 0; index < POINTER_POSE_SAMPLE_COUNT; index += 1) {
    const fraction = index / (POINTER_POSE_SAMPLE_COUNT - 1);
    await scrollInstant(page, entryStart + (exitEnd - entryStart) * fraction);

    const targetState = await readMotionState(target);
    const targetPoint = await cta.evaluate((element) => {
      const rect = element.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const hit = document.elementFromPoint(centerX, centerY);
      return {
        hitTarget: hit === element || element.contains(hit),
        visible:
          rect.width > 0 &&
          rect.height > 0 &&
          rect.top >= 0 &&
          rect.bottom <= window.innerHeight &&
          rect.left >= 0 &&
          rect.right <= window.innerWidth,
      };
    });

    if (
      isBoundaryState(targetState) &&
      targetPoint.visible &&
      targetPoint.hitTarget
    ) {
      transformedPoseFound = true;
      break;
    }
  }

  if (!transformedPoseFound) {
    throw new Error("The pilot CTA must be visible during a transformed target pose.");
  }

  const before = await cta.boundingBox();
  if (!before) {
    throw new Error("The pilot CTA must have measurable bounds.");
  }
  const beforeBounds = {
    bottom: before.y + before.height,
    centerX: before.x + before.width / 2,
    centerY: before.y + before.height / 2,
    left: before.x,
    right: before.x + before.width,
    top: before.y,
  };

  // Sample at pointerdown: a scroll timeline may settle between hover and press.
  await cta.evaluate((element) => {
    element.addEventListener("pointerdown", () => {
      const rect = element.getBoundingClientRect();
      (element as HTMLElement).dataset.pointerBounds = JSON.stringify({
        bottom: rect.bottom,
        centerX: rect.left + rect.width / 2,
        centerY: rect.top + rect.height / 2,
        left: rect.left,
        right: rect.right,
        top: rect.top,
      });
    }, { capture: true, once: true });
  });
  await page.mouse.move(beforeBounds.centerX, beforeBounds.centerY);
  await page.mouse.down();
  try {
    const pointerBoundsJson = await cta.getAttribute("data-pointer-bounds");
    if (!pointerBoundsJson) throw new Error("The pointerdown must reach the pilot CTA.");
    const pointerBounds = JSON.parse(pointerBoundsJson) as typeof beforeBounds;
    const duringPointerDown = await cta.boundingBox();
    if (!duringPointerDown) {
      throw new Error("The pilot CTA must remain measurable after pointerdown.");
    }
    const duringBounds = {
      bottom: duringPointerDown.y + duringPointerDown.height,
      centerX: duringPointerDown.x + duringPointerDown.width / 2,
      centerY: duringPointerDown.y + duringPointerDown.height / 2,
      left: duringPointerDown.x,
      right: duringPointerDown.x + duringPointerDown.width,
      top: duringPointerDown.y,
    };
    for (const key of Object.keys(beforeBounds) as Array<keyof typeof beforeBounds>) {
      expect(
        Math.abs(duringBounds[key] - pointerBounds[key]),
        `pointerdown changed CTA ${key}`,
      ).toBeLessThanOrEqual(POINTER_POSITION_TOLERANCE_PX);
    }
  } finally {
    await page.mouse.up();
  }

  await expect(page.getByRole("dialog", { name: "Request a pilot" })).toBeVisible();
});

test("keeps all section content readable without JavaScript on a tall 320px viewport", async ({
  browser,
}) => {
  const context = await browser.newContext({
    javaScriptEnabled: false,
    viewport: { width: 320, height: 900 },
  });
  const page = await context.newPage();

  await page.goto("/", { waitUntil: "domcontentloaded" });
  const sections = page.locator("main > section[data-section-motion]");
  await expect(sections).toHaveCount(EXPECTED_SECTION_COUNT);

  const surfaceReports = await sections.evaluateAll((elements) =>
    elements.map((section) => {
      const surface = section.querySelector<HTMLElement>(
        ":scope > div.section-motion-surface",
      );
      if (!surface) {
        return { opacity: "", text: "", visible: false };
      }
      const styles = getComputedStyle(surface);
      return {
        opacity: styles.opacity,
        text: surface.innerText.trim(),
        visible: surface.getClientRects().length > 0,
      };
    }),
  );
  expect(
    surfaceReports.every(
      ({ opacity, text, visible }) =>
        opacity === "1" && text.length > 0 && visible,
    ),
  ).toBe(true);

  for (const spec of SECTION_SPECS) {
    const section = page.locator(spec.selector);
    for (const selector of spec.targetSelectors) {
      const reports = await section.locator(selector).evaluateAll((elements) =>
        elements.map((element) => {
          const styles = getComputedStyle(element);
          return {
            opacity: styles.opacity,
            visible: element.getClientRects().length > 0,
          };
        }),
      );
      expect(reports.length).toBeGreaterThan(0);
      expect(
        reports.every(({ opacity, visible }) => opacity === "1" && visible),
      ).toBe(true);
    }
  }

  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await page.locator("#process").scrollIntoViewIfNeeded();
  await expect(
    page.getByRole("heading", { level: 2, name: /From billed to reviewed/i }),
  ).toBeVisible();
  const processList = page.locator("#process .process-list");
  await expect(processList).toBeVisible();
  expect((await processList.innerText()).trim()).not.toBe("");

  await context.close();
});

test("keeps section surfaces within the 320px reading width", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 900 });
  await page.goto("/", { waitUntil: "networkidle" });

  const bounds = await page
    .locator("main > section[data-section-motion]")
    .evaluateAll((sections) => ({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      surfaces: sections.map((section) => {
        const surface = section.querySelector<HTMLElement>(
          ":scope > div.section-motion-surface",
        );
        const rect = surface?.getBoundingClientRect();
        return rect
          ? { left: rect.left, right: rect.right }
          : { left: Number.NaN, right: Number.NaN };
      }),
    }));

  expect(bounds.scrollWidth).toBeLessThanOrEqual(bounds.clientWidth + 1);
  expect(
    bounds.surfaces.every(
      ({ left, right }) => left >= -1 && right <= bounds.clientWidth + 1,
    ),
  ).toBe(true);
});
