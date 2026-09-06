import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const HERO_TITLE = "Recover the D&D money hiding in your invoices.";
const ANCHOR_IDS = ["process", "evidence", "pilot-scope", "trust"] as const;
const ROUTES = ["/", "/pilot", "/privacy", "/terms"] as const;

for (const width of [390, 1440]) {
  test(`downloads only the matching hero image at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    const heroRequests: string[] = [];
    page.on("request", (request) => {
      const url = new URL(request.url());
      if (url.pathname === "/_next/image" && url.searchParams.get("url")?.startsWith("/media/recovery-terminal")) {
        heroRequests.push(url.searchParams.get("url") ?? "");
      }
    });
    await page.goto("/", { waitUntil: "networkidle" });
    expect(heroRequests).toEqual([
      width < 768 ? "/media/recovery-terminal-mobile.png" : "/media/recovery-terminal.png",
    ]);
  });
}

test("presents the centered recovery hero with contained, loaded imagery", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });

  const hero = page.getByTestId("hero-scene");
  const heading = page.getByRole("heading", {
    level: 1,
    name: HERO_TITLE,
  });
  await expect(hero).toBeVisible();
  await expect(heading).toBeVisible();
  await expect(heading).toHaveCSS("text-align", "center");
  for (const selector of [".recovery-hero", '[data-section-motion="closing"]', "footer"]) {
    await expect(page.locator(selector)).not.toContainText(/case-specific review|no guaranteed recovery/i);
  }

  const heroImages = hero.locator("img");
  const imageDetails = await heroImages.evaluateAll((images) =>
    images.map((element) => {
      const image = element as HTMLImageElement;
      const values = [image.getAttribute("src") ?? "", image.currentSrc];
      return {
        sources: values.map((value) => {
          try {
            return decodeURIComponent(value);
          } catch {
            return value;
          }
        }),
        naturalWidth: image.naturalWidth,
      };
    }),
  );
  const recoveryImageIndex = imageDetails.findIndex((image) =>
    image.sources.some((source) => source.includes("/media/recovery-terminal.png")),
  );
  expect(recoveryImageIndex).toBeGreaterThanOrEqual(0);
  expect(imageDetails[recoveryImageIndex]?.naturalWidth).toBeGreaterThan(0);

  const recoveryImage = heroImages.nth(recoveryImageIndex);
  const heroBox = await hero.boundingBox();
  const imageBox = await recoveryImage.boundingBox();
  expect(heroBox).not.toBeNull();
  expect(imageBox).not.toBeNull();
  if (heroBox === null || imageBox === null) {
    throw new Error("The hero and recovery image must have measurable bounds.");
  }

  const tolerance = 2;
  expect(imageBox.x).toBeGreaterThanOrEqual(heroBox.x - tolerance);
  expect(imageBox.y).toBeGreaterThanOrEqual(heroBox.y - tolerance);
  expect(imageBox.x + imageBox.width).toBeLessThanOrEqual(
    heroBox.x + heroBox.width + tolerance,
  );
  expect(imageBox.y + imageBox.height).toBeLessThanOrEqual(
    heroBox.y + heroBox.height + tolerance,
  );

  const heroText = (await hero.innerText()).replace(/\s+/g, " ");
  expect(heroText).not.toMatch(/D&D invoice/i);
  await expect(
    hero.getByText(
      /^(Billing|Billing record|Operational|Operational record|Governing|Governing terms|Review packet)$/i,
    ),
  ).toHaveCount(0);
  await expect(hero.locator("figcaption")).toHaveCount(0);
  await expect(
    hero.locator('[data-invoice-panel], [class*="invoice-panel"], [class*="invoice-card"]'),
  ).toHaveCount(0);
});

test("keeps lower-section imagery loaded and contained by its section", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });

  const images = page.locator("main img");
  expect(await images.count()).toBeGreaterThanOrEqual(2);
  await images.nth(1).scrollIntoViewIfNeeded();
  await expect
    .poll(
      async () =>
        images.evaluateAll((elements) =>
          elements
            .filter((element) => !element.closest('[data-testid="hero-scene"]'))
            .every((element) => {
              const image = element as HTMLImageElement;
              return image.complete && image.naturalWidth > 0;
            }),
        ),
      { timeout: 10_000 },
    )
    .toBe(true);

  const lowerImageReports = await images.evaluateAll((elements) =>
    elements
      .filter((element) => !element.closest('[data-testid="hero-scene"]'))
      .map((element) => {
        const image = element as HTMLImageElement;
        const imageBox = image.getBoundingClientRect();
        const frame = image.closest("figure, section") ?? image.parentElement;
        const frameBox = frame?.getBoundingClientRect();
        return {
          complete: image.complete,
          naturalWidth: image.naturalWidth,
          image: {
            left: imageBox.left,
            right: imageBox.right,
            top: imageBox.top,
            bottom: imageBox.bottom,
          },
          frame: frameBox
            ? {
                left: frameBox.left,
                right: frameBox.right,
                top: frameBox.top,
                bottom: frameBox.bottom,
              }
            : null,
        };
      }),
  );
  expect(lowerImageReports.length).toBeGreaterThan(0);

  for (const report of lowerImageReports) {
    expect(report.complete).toBe(true);
    expect(report.naturalWidth).toBeGreaterThan(0);
    expect(report.frame).not.toBeNull();
    if (report.frame === null) {
      throw new Error("Every lower-section image must have a containing frame.");
    }
    const tolerance = 2;
    expect(report.image.left).toBeGreaterThanOrEqual(report.frame.left - tolerance);
    expect(report.image.right).toBeLessThanOrEqual(report.frame.right + tolerance);
    expect(report.image.top).toBeGreaterThanOrEqual(report.frame.top - tolerance);
    expect(report.image.bottom).toBeLessThanOrEqual(report.frame.bottom + tolerance);
  }
});

test("keeps the navigation anchors and evidence labels in the reading order", async ({
  page,
}) => {
  await page.goto("/", { waitUntil: "networkidle" });

  for (const id of ANCHOR_IDS) {
    const section = page.locator(`#${id}`);
    await expect(section).toHaveCount(1);
    await expect(section).toBeAttached();
    expect(await page.locator(`a[href="#${id}"]`).count()).toBeGreaterThan(0);
  }

  const heroBox = await page.getByTestId("hero-scene").boundingBox();
  const evidenceBox = await page.locator("#evidence").boundingBox();
  expect(heroBox).not.toBeNull();
  expect(evidenceBox).not.toBeNull();
  if (heroBox === null || evidenceBox === null) {
    throw new Error("The hero and evidence sections must have measurable bounds.");
  }
  expect(evidenceBox.y).toBeGreaterThan(heroBox.y + heroBox.height - 2);

  const evidenceLabelCount = await page
    .locator("#evidence")
    .getByText(/billing|operational|governing/i)
    .count();
  expect(evidenceLabelCount).toBeGreaterThanOrEqual(3);
  expect(
    await page
      .getByTestId("hero-scene")
      .getByText(/billing|operational|governing/i)
      .count(),
  ).toBe(0);
});

test("uses valid list semantics for grouped content", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" });

  const lists = await page.locator("ol, ul").evaluateAll((elements) =>
    elements.map((element) => ({
      childTags: Array.from(element.children).map((child) => child.tagName),
      itemCount: Array.from(element.children).filter(
        (child) => child.tagName === "LI",
      ).length,
    })),
  );
  expect(lists.length).toBeGreaterThan(0);
  expect(
    lists.every(
      ({ childTags, itemCount }) =>
        childTags.length > 0 &&
        itemCount === childTags.length &&
        childTags.every((tag) => tag === "LI"),
    ),
  ).toBe(true);
  expect(await page.getByRole("listitem").count()).toBeGreaterThan(0);
});

for (const route of ROUTES) {
  test(`has no serious accessibility violations on ${route}`, async ({ page }) => {
    await page.goto(route, { waitUntil: "networkidle" });
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();
    expect(results.violations).toEqual([]);
  });
}

for (const route of ["/pilot", "/privacy", "/terms"] as const) {
  test(`shares a clean header and footer without Preview branding on ${route}`, async ({
    page,
  }) => {
    await page.goto(route, { waitUntil: "networkidle" });
    await expect(page.locator("header").first()).toBeVisible();
    await expect(page.locator("footer").first()).toBeVisible();
    const chromeText = `${await page.locator("header").innerText()} ${await page
      .locator("footer")
      .innerText()}`;
    expect(chromeText).not.toMatch(/Preview/i);
  });
}

test("keeps the complete content and native navigation path without JavaScript", async ({
  browser,
}) => {
  const context = await browser.newContext({
    javaScriptEnabled: false,
    viewport: { width: 390, height: 900 },
  });
  const page = await context.newPage();

  await page.goto("/", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { level: 1, name: HERO_TITLE })).toBeVisible();
  await expect(
    page.locator('a[href="/pilot"]:visible').filter({ hasText: "Request a pilot" }).first(),
  ).toBeVisible();
  await expect(page.locator("main")).toContainText("Request a pilot");
  for (const id of ANCHOR_IDS) {
    await expect(page.locator(`#${id}`)).toBeAttached();
  }
  await expect(page.locator("main img").first()).toBeAttached();

  const navigation = page.locator('details:has(summary[aria-label="Navigation menu"])');
  const summary = navigation.locator('summary[aria-label="Navigation menu"]');
  await expect(summary).toBeVisible();
  await summary.click();
  await expect(navigation).toHaveAttribute("open", "");
  await navigation.locator('a[href="#process"]').click();
  await expect(page).toHaveURL(/#process$/);

  await page.locator('a[href="/pilot"]:visible').filter({ hasText: "Request a pilot" }).first().click();
  await expect(page).toHaveURL(/\/pilot\/?$/);
  await expect(page.locator("form").filter({ hasText: "Work email" }).first()).toBeVisible();

  await context.close();
});
