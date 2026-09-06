import { expect, test } from "@playwright/test";

const ROUTES = ["/", "/pilot", "/privacy", "/terms"] as const;

for (const route of ROUTES) {
  test(`renders ${route} without console, hydration, or failed-request errors`, async ({
    page,
  }) => {
    const consoleErrors: string[] = [];
    const pageErrors: string[] = [];
    const failedRequests: string[] = [];

    page.on("console", (message) => {
      if (message.type() === "error") {
        consoleErrors.push(message.text());
      }
    });
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("requestfailed", (request) => {
      failedRequests.push(`${request.method()} ${request.url()}`);
    });

    await page.goto(route, { waitUntil: "networkidle" });
    await expect(page.locator("main")).toBeVisible();

    expect(consoleErrors).toEqual([]);
    expect(pageErrors).toEqual([]);
    expect(failedRequests).toEqual([]);

    const hydrationErrors = [...consoleErrors, ...pageErrors].filter((message) =>
      /hydration|text content does not match|server-rendered html/i.test(message),
    );
    expect(hydrationErrors).toEqual([]);
  });
}

test("serves the clean recovery asset and renders every page image successfully", async ({
  page,
  request,
}) => {
  const assetResponse = await request.get("/media/recovery-terminal.png");
  expect(assetResponse.status()).toBe(200);
  expect(assetResponse.headers()["content-type"]).toMatch(/^image\//);
  expect((await assetResponse.body()).byteLength).toBeGreaterThan(0);

  await page.goto("/", { waitUntil: "networkidle" });
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForLoadState("networkidle");

  const brokenImages = await page.locator("main img").evaluateAll((images) =>
    images
      .filter((element) => {
        const image = element as HTMLImageElement;
        return image.complete && image.naturalWidth === 0;
      })
      .map((image) => image.getAttribute("src") ?? "(missing src)"),
  );
  expect(brokenImages).toEqual([]);
});
