import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("explains invoice-only recovery and follows the enquiry path without collecting data", async ({ page }) => {
  const errors: string[] = [];
  const posts: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => { if (request.method() === "POST") posts.push(request.url()); });
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("SheperD.");
  await expect(page.locator("#cfo-title")).toHaveText(/Your time\s*stays yours\./);
  await expect(page.locator(".cfo-promise")).toHaveText("You send the invoices. We handle the recovery.");
  await expect(page.locator(".cfo-dock-illustration img")).toHaveCount(1);
  await expect(page.locator(".responsibility-flow ol li")).toHaveCount(3);
  await expect(page.locator(".recovery-process li")).toHaveCount(4);
  await expect(page.locator("#process-title")).toHaveText("A clear path.An entirely managed process.");
  await expect(page.locator("#evidence")).toHaveAttribute("data-market-state", "approved");
  await expect(page.locator(".market-opportunity-node")).toContainText("$13B");
  await expect(page.locator(".market-opportunity-node")).toContainText("annual port-delay cost");
  await expect(page.locator(".market-source")).toHaveAttribute(
    "href",
    "https://nam.org/wp-content/uploads/securepdfs/2026/02/BTW-2026-Web.vF_.pdf",
  );
  const marketMap = page.locator('img[src$="opportunity-trade-map-transparent.png"]');
  await expect(marketMap).toHaveCount(1);
  expect(await marketMap.evaluate((element) => (element as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
  await expect(page.locator(".industry")).toHaveCount(8);
  await expect(page.locator('img[src$="-glass-transparent.png"]')).toHaveCount(12);
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
  await expect(page.locator("#cfo-title")).toHaveText(/Your time\s*stays yours\./);
  await expect(page.locator(".cfo-promise")).toHaveText("You send the invoices. We handle the recovery.");
  await expect(page.locator(".ai-review-copy")).toHaveText(
    "AI helps organize the complex recovery record; human reviewers decide what the evidence supports.",
  );
  await expect(page.locator("#process-title")).toHaveText("A clear path.An entirely managed process.");
  await expect(page.locator(".process-ai")).toHaveText("AI-assisted review. Human-led recovery follow-up.");
  await expect(page.locator(".hero-headline")).toHaveCSS("font-size", "34px");
  await expect(page.locator(".hero-description")).toHaveCSS("font-size", "17px");
  await expect(page.locator(".process-heading .section-description")).toHaveCSS("font-size", "18px");

  await page.setViewportSize({ width: 375, height: 900 });
  await page.reload();
  await expect(page.locator(".hero-headline")).toHaveCSS("font-size", "28px");
  await expect(page.locator(".hero-description")).toHaveCSS("font-size", "15px");
  await expect(page.locator(".process-heading .section-description")).toHaveCSS("font-size", "16px");
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
