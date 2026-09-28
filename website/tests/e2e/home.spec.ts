import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("leads with invoice value and follows the enquiry path without collecting data", async ({ page }) => {
  const errors: string[] = [];
  const posts: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => { if (request.method() === "POST") posts.push(request.url()); });
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("SheperD.");
  await expect(page.locator(".recovery-hero + .market-section")).toHaveCount(1);
  await expect(page.locator(".cfo-editorial-scene")).toHaveCount(0);
  await expect(page.locator("#market-title")).toHaveText("Past invoices may hold money for your bottom line.");
  await expect(page.locator("#evidence .recovery-action")).toHaveAttribute("href", "/pilot");
  await expect(page.locator(".recovery-process li")).toHaveCount(4);
  await expect(page.locator("#process-title")).toHaveText("A clear path.An entirely managed process.");
  await expect(page.locator("#evidence")).toContainText("Three years of past U.S. detention and demurrage invoices");
  await expect(page.locator("#evidence")).toContainText("potential cash refunds or carrier credits");
  await expect(page.locator(".invoice-history-timeline li")).toHaveText(["Year 1", "Year 2", "Year 3"]);
  await expect(page.locator(".invoice-history-bracket")).toHaveText("Past 3 years");
  await expect(page.locator(".invoice-history-outcomes li")).toHaveText([
    "Potential cash refund",
    "Potential carrier credit",
  ]);
  await expect(page.locator(".invoice-history-note")).toContainText("not a recovery estimate");
  await page.locator(".invoice-history-visual").scrollIntoViewIfNeeded();
  await expect.poll(() =>
    page.locator(".invoice-stack-art img").evaluateAll((images) =>
      images.every((image) => (image as HTMLImageElement).naturalWidth > 0),
    ),
  ).toBe(true);
  await expect(page.locator("#evidence")).not.toContainText("$13B");
  await expect(page.locator("#evidence")).not.toContainText("global");
  await expect(page.locator(".industry")).toHaveCount(8);
  await expect(page.locator(".industry-icon")).toHaveCount(8);
  await expect(page.locator(".industry img")).toHaveCount(0);
  await expect(page.locator(".industry-icon").first()).toHaveCSS("color", "rgb(13, 109, 253)");
  await page.locator("summary").filter({ hasText: "What does my team need to do?" }).click();
  await expect(page.locator("details[open]")).toContainText("Your team does not need to build or manage a recovery function");
  await page.locator(".hero-actions").getByRole("link", { name: "Find Recoverable Value" }).click();
  await expect(page).toHaveURL(/\/pilot$/);
  await expect(page.getByRole("status")).toContainText("No details are collected, stored, or sent");
  await expect(page.locator("input,textarea,select")).toHaveCount(0);
  expect(posts).toEqual([]);
  expect(errors).toEqual([]);
});

test("keeps the clear-path message and readable type hierarchy", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto("/");
  await expect(page).toHaveTitle("SheperD | A clear path through D&D recovery");
  await expect(page.locator('meta[name="description"]')).toHaveAttribute(
    "content",
    /A clear path from invoice to recovery\./,
  );
  await expect(page.locator(".hero-headline")).toHaveText("A clear path from invoice to recovery.");
  await expect(page.locator(".hero-description")).toHaveText("You send the invoices. We handle the recovery.");
  await expect(page.locator(".hero-ai")).toHaveText("AI-assisted D&D recovery with human review.");
  await expect(page.locator(".recovery-hero + .market-section")).toHaveCount(1);
  await expect(page.locator("#market-title")).toHaveText("Past invoices may hold money for your bottom line.");
  await expect(page.locator("#process-title")).toHaveText("A clear path.An entirely managed process.");
  await expect(page.locator(".process-ai")).toHaveCount(0);
  await expect(page.locator(".hero-headline")).toHaveCSS("font-size", "34px");
  await expect(page.locator(".hero-description")).toHaveCSS("font-size", "17px");
  await expect(page.locator(".process-heading .section-description")).toHaveCSS("font-size", "18px");
  const desktopTitleTops = await page.locator("#process .recovery-process h3").evaluateAll(
    (titles) => titles.map((title) => title.getBoundingClientRect().top),
  );
  expect(Math.max(...desktopTitleTops) - Math.min(...desktopTitleTops)).toBeLessThanOrEqual(1);

  await page.setViewportSize({ width: 375, height: 900 });
  await page.reload();
  await expect(page.locator(".hero-headline")).toHaveCSS("font-size", "28px");
  await expect(page.locator(".hero-description")).toHaveCSS("font-size", "15px");
  await expect(page.locator(".process-heading .section-description")).toHaveCSS("font-size", "16px");
  const mobileTitleLefts = await page.locator("#process .recovery-process h3").evaluateAll(
    (titles) => titles.map((title) => title.getBoundingClientRect().left),
  );
  expect(Math.max(...mobileTitleLefts) - Math.min(...mobileTitleLefts)).toBeLessThanOrEqual(1);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test("mobile navigation follows supporting routes and closes", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 900 });
  await page.goto("/");
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page.locator("#mobile-navigation").getByRole("link", { name: "For importers" }).click();
  await expect(page).toHaveURL(/\/for-importers$/);
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Your shipping history");
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("button", { name: "Open navigation" })).toBeVisible();
});

test("mobile header keeps the value CTA visible and targets touch size", async ({ page }) => {
  for (const width of [320, 375, 420, 540]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/");
    const cta = page.locator(".mobile-audit-link");
    const toggle = page.getByRole("button", { name: "Open navigation" });
    await expect(cta).toBeVisible();
    await expect(cta).toHaveAttribute("href", "/pilot");
    await expect(toggle).toBeVisible();
    const box = await toggle.boundingBox();
    expect(box?.width).toBeGreaterThanOrEqual(44);
    expect(box?.height).toBeGreaterThanOrEqual(44);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
  }
});

test("mobile hero image fills the section background", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  const dimensions = await page.locator(".recovery-hero").evaluate((hero) => {
    const image = hero.querySelector(".port-art img");
    if (!(image instanceof HTMLImageElement)) throw new Error("Hero image not found");
    return {
      heroHeight: hero.getBoundingClientRect().height,
      imageHeight: image.getBoundingClientRect().height,
      objectFit: getComputedStyle(image).objectFit,
    };
  });
  expect(dimensions.objectFit).toBe("cover");
  expect(Math.abs(dimensions.heroHeight - dimensions.imageHeight)).toBeLessThan(1);
});

for (const route of ["/", "/how-it-works", "/for-importers", "/about", "/pilot", "/privacy", "/terms"]) {
  test(`accessible and complete route ${route}`, async ({ page }) => {
    const response = await page.goto(route);
    expect(response?.status()).toBe(200);
    await expect(page.getByRole("heading", { level: 1 })).toHaveCount(1);
    await expect(page.locator('meta[name="description"]')).toHaveAttribute("content", /.+/);
    expect((await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze()).violations).toEqual([]);
  });
}

test("legacy anchors and footer routes point to real destinations", async ({ page }) => {
  await page.goto("/");
  for (const id of ["process", "evidence", "pilot-scope", "trust", "mission"]) await expect(page.locator(`#${id}`)).toHaveCount(1);
  await page.getByRole("navigation", { name: "Footer navigation" }).getByRole("link", { name: "About" }).click();
  await expect(page).toHaveURL(/\/about$/);
  await page.getByRole("navigation", { name: "Footer navigation" }).getByRole("link", { name: "How it works" }).click();
  await expect(page).toHaveURL(/\/how-it-works$/);
});
