import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("renders the Recovery Corridor and follows its conversion path", async ({
  page,
}) => {
  const consoleErrors: string[] = [];
  const failedRequests: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("requestfailed", (request) => failedRequests.push(request.url()));

  await page.goto("/", { waitUntil: "networkidle" });

  await expect(
    page.getByRole("heading", { level: 1, name: "Recover What’s Yours" }),
  ).toBeVisible();
  await expect(page.getByText("$2.1B", { exact: true })).toBeVisible();
  await expect(page.getByText("$6.2B", { exact: true })).toBeVisible();
  await expect(page.getByText("3 years", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("heading", {
      level: 2,
      name: "Make container-charge recovery a standard part of import operations.",
    }),
  ).toBeVisible();
  await expect(page.locator('img[src*="recovery-dashboard"]')).toBeVisible();

  await page
    .locator(".hero-actions")
    .getByRole("link", { name: "Get a Free Invoice Audit" })
    .click();
  await expect(page.locator("#audit-form")).toBeInViewport();

  await page.locator("#full-name").fill("Jane Smith");
  await page.locator("#work-email").fill("jane@example.com");
  await page.locator("#phone").fill("5550000000");
  await page.locator("#company").fill("Example Imports");
  await page.locator("#city").fill("Los Angeles");
  await page.locator("#state").fill("CA");
  await page.getByRole("button", { name: "Submit" }).click();

  await expect(
    page.getByText("Interaction verified. No details were sent."),
  ).toBeVisible();
  expect(consoleErrors).toEqual([]);
  expect(failedRequests).toEqual([]);
});

test("opens, closes, and follows the mobile navigation", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 900 });
  await page.goto("/");

  const menuButton = page.getByRole("button", { name: "Open navigation" });
  await menuButton.click();
  await expect(
    page.getByRole("button", { name: "Close navigation" }),
  ).toBeVisible();

  await page
    .locator("#mobile-navigation")
    .getByRole("link", { name: "Our mission" })
    .click();
  await expect(page.locator("#mission")).toBeInViewport();
  await expect(menuButton).toBeVisible();
});

for (const route of ["/", "/privacy", "/terms"] as const) {
  test(`has no serious accessibility violations on ${route}`, async ({ page }) => {
    await page.goto(route, { waitUntil: "networkidle" });
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();
    expect(results.violations).toEqual([]);
  });
}

test("keeps the complete reading path without JavaScript", async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(page.getByText("Send container invoices", { exact: true })).toBeVisible();
  await expect(page.getByText("We audit every charge", { exact: true })).toBeVisible();
  await expect(
    page
      .locator("#mission")
      .getByRole("heading", { name: "Recover eligible fees" }),
  ).toBeVisible();
  await expect(page.locator('img[src*="recovery-dashboard"]')).toBeVisible();
  await expect(page.locator("#audit-form")).toBeVisible();
  await context.close();
});
