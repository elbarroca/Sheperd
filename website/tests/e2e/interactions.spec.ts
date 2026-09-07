import { expect, test, type Locator, type Page } from "@playwright/test";

const FAQ_SELECTOR = '.faq-block details[name="pilot-faq"]';
const REVEAL_SETTLED_TIMEOUT_MS = 3_000;
const TAB_LIMIT = 40;

interface ArrowState {
  transform: string;
  transitionDuration: string;
}

interface ProcessLayout {
  connectorRects: Array<{ height: number; width: number }>;
  itemRects: Array<{ height: number; left: number; top: number; width: number }>;
  visualDirections: string[];
}

function translationFromTransform(transform: string): { x: number; y: number } {
  if (transform === "none") {
    return { x: 0, y: 0 };
  }

  const match = /^matrix(3d)?\(([^)]+)\)$/u.exec(transform);
  if (!match) {
    return { x: 0, y: 0 };
  }

  const values = match[2].split(",").map(Number);
  if (match[1] === "3d") {
    return {
      x: values[12] ?? 0,
      y: values[13] ?? 0,
    };
  }

  return {
    x: values[4] ?? 0,
    y: values[5] ?? 0,
  };
}

function isIdentityTransform(transform: string): boolean {
  if (transform === "none") {
    return true;
  }

  const match = /^matrix(3d)?\(([^)]+)\)$/u.exec(transform);
  if (!match) {
    return false;
  }

  const values = match[2].split(",").map(Number);
  const identity =
    match[1] === "3d"
      ? [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
      : [1, 0, 0, 1, 0, 0];

  return (
    values.length === identity.length &&
    values.every(
      (value, index) => Math.abs(value - (identity[index] ?? 0)) < 0.01,
    )
  );
}

async function readArrowState(arrow: Locator): Promise<ArrowState> {
  return arrow.evaluate((element) => {
    const styles = getComputedStyle(element);
    return {
      transform: styles.transform,
      transitionDuration: styles.transitionDuration,
    };
  });
}

async function focusWithKeyboard(page: Page, target: Locator): Promise<void> {
  await page.evaluate(() => {
    const active = document.activeElement;
    if (active instanceof HTMLElement) active.blur();
  });

  const tabKey =
    page.context().browser()?.browserType().name() === "webkit"
      ? "Alt+Tab"
      : "Tab";

  for (let index = 0; index < TAB_LIMIT; index += 1) {
    await page.keyboard.press(tabKey);
    if (await target.evaluate((element) => element === document.activeElement)) {
      return;
    }
  }

  throw new Error("The source link was not reachable with keyboard navigation.");
}

async function readProcessLayout(processSection: Locator): Promise<ProcessLayout> {
  return processSection.evaluate((section) => {
    const items = Array.from(
      section.querySelectorAll<HTMLElement>(".process-list > li"),
    );
    const visuals = items.map((item) =>
      item.querySelector<HTMLElement>(".process-visual"),
    );
    const connectors = Array.from(
      section.querySelectorAll<HTMLElement>(".process-connector"),
    );

    return {
      connectorRects: connectors.map((connector) => {
        const rect = connector.getBoundingClientRect();
        return { height: rect.height, width: rect.width };
      }),
      itemRects: items.map((item) => {
        const rect = item.getBoundingClientRect();
        return {
          height: rect.height,
          left: rect.left,
          top: rect.top,
          width: rect.width,
        };
      }),
      visualDirections: visuals.map(
        (visual) => (visual ? getComputedStyle(visual).flexDirection : ""),
      ),
    };
  });
}

async function readConnectorTransforms(processSection: Locator): Promise<string[]> {
  return processSection.locator(".process-connector").evaluateAll((elements) =>
    elements.map((element) => getComputedStyle(element).transform),
  );
}

test("opens one native FAQ item at a time with click and keyboard", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });

  const faqItems = page.locator(FAQ_SELECTOR);
  await expect(faqItems).toHaveCount(10);
  expect(
    await faqItems.evaluateAll(
      (elements) => elements.filter((element) => element.hasAttribute("open")).length,
    ),
  ).toBe(0);

  const firstItem = faqItems.nth(0);
  const secondItem = faqItems.nth(1);
  const thirdItem = faqItems.nth(2);

  await firstItem.locator("summary").click();
  await expect(firstItem).toHaveAttribute("open", "");
  await expect(secondItem).not.toHaveAttribute("open", "");

  await secondItem.locator("summary").focus();
  await page.keyboard.press("Enter");
  await expect(secondItem).toHaveAttribute("open", "");
  await expect(firstItem).not.toHaveAttribute("open", "");

  await thirdItem.locator("summary").focus();
  await page.keyboard.press(" ");
  await expect(thirdItem).toHaveAttribute("open", "");
  await expect(secondItem).not.toHaveAttribute("open", "");
});

test("moves source arrows on hover and keyboard focus without reduced-motion transitions", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/", { waitUntil: "networkidle" });

  const sourceLink = page.locator(".source-list a.arrow-link").first();
  const arrow = sourceLink.locator("svg");
  await expect(sourceLink).toBeVisible();
  const initial = await readArrowState(arrow);
  expect(translationFromTransform(initial.transform)).toEqual({ x: 0, y: 0 });

  await sourceLink.hover();
  await expect
    .poll(async () => translationFromTransform((await readArrowState(arrow)).transform).x)
    .toBeGreaterThan(1);
  const hovered = translationFromTransform((await readArrowState(arrow)).transform);
  expect(hovered.y).toBeLessThan(-1);

  await page.mouse.move(1, 1);
  await focusWithKeyboard(page, sourceLink);
  await expect
    .poll(async () => translationFromTransform((await readArrowState(arrow)).transform).x)
    .toBeGreaterThan(1);
  const focused = translationFromTransform((await readArrowState(arrow)).transform);
  expect(focused.y).toBeLessThan(-1);

  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.reload({ waitUntil: "networkidle" });

  const reducedLink = page.locator(".source-list a.arrow-link").first();
  const reducedArrow = reducedLink.locator("svg");
  const reducedInitial = await readArrowState(reducedArrow);
  expect(reducedInitial.transitionDuration).toBe("0s");

  await reducedLink.hover();
  await expect
    .poll(async () => (await readArrowState(reducedArrow)).transitionDuration)
    .toBe("0s");

  await page.mouse.move(1, 1);
  await focusWithKeyboard(page, reducedLink);
  await expect
    .poll(async () => (await readArrowState(reducedArrow)).transitionDuration)
    .toBe("0s");
});

test("lays out the process visuals horizontally on desktop and vertically on mobile", async ({
  page,
}) => {
  for (const viewport of [
    { width: 1440, height: 1000, direction: "horizontal" },
    { width: 390, height: 900, direction: "vertical" },
  ] as const) {
    await page.setViewportSize(viewport);
    await page.goto("/", { waitUntil: "networkidle" });

    const processSection = page.locator("#process");
    const processItems = processSection.locator(".process-list > li");
    await expect(processItems).toHaveCount(3);
    await processSection.scrollIntoViewIfNeeded();
      await expect
        .poll(
        async () =>
          processItems.evaluateAll((elements) =>
            elements.every(
              (element) =>
                element.getAttribute("data-scroll-reveal-state") === "revealed",
            ),
          ),
        { timeout: REVEAL_SETTLED_TIMEOUT_MS },
      )
      .toBe(true);
    await expect
      .poll(
        async () => {
          const transforms = await readConnectorTransforms(processSection);
          return transforms.length === 2 && transforms.every(isIdentityTransform);
        },
        { timeout: REVEAL_SETTLED_TIMEOUT_MS },
      )
      .toBe(true);

    const layout = await readProcessLayout(processSection);
    expect(layout.connectorRects).toHaveLength(2);
    expect(layout.visualDirections).toEqual(
      Array.from({ length: 3 }, () =>
        viewport.direction === "horizontal" ? "row" : "column",
      ),
    );

    if (viewport.direction === "horizontal") {
      const itemTops = layout.itemRects.map(({ top }) => top);
      expect(Math.max(...itemTops) - Math.min(...itemTops)).toBeLessThanOrEqual(2);
      expect(layout.itemRects[1]?.left).toBeGreaterThan(
        (layout.itemRects[0]?.left ?? 0) + 10,
      );
      expect(layout.itemRects[2]?.left).toBeGreaterThan(
        (layout.itemRects[1]?.left ?? 0) + 10,
      );
      expect(
        layout.connectorRects.every(({ height, width }) => width > height),
      ).toBe(true);
    } else {
      expect(layout.itemRects[1]?.top).toBeGreaterThan(
        (layout.itemRects[0]?.top ?? 0) + 20,
      );
      expect(layout.itemRects[2]?.top).toBeGreaterThan(
        (layout.itemRects[1]?.top ?? 0) + 20,
      );
      expect(
        layout.connectorRects.every(
          ({ height, width }) => width <= 2 && height > width,
        ),
      ).toBe(true);
    }
  }
});
