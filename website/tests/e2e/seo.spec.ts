import { expect, test } from "@playwright/test";

const CANONICAL_ORIGIN = "https://sheperd-website.vercel.app";
const IS_PRODUCTION = process.env.SHEPERD_QA_PRODUCTION === "1";

test("uses the build's robots policy and canonical homepage origin", async ({ page }) => {
  const response = await page.goto("/", { waitUntil: "networkidle" });
  const expectedRobots = IS_PRODUCTION ? "index, follow" : "noindex, nofollow, noarchive";

  await expect(page.locator('meta[name="robots"]')).toHaveAttribute(
    "content",
    expectedRobots,
  );
  expect(response?.headers()["x-robots-tag"]).toBe(expectedRobots);
  const canonicalHref = await page
    .locator('link[rel="canonical"]')
    .getAttribute("href");
  expect([CANONICAL_ORIGIN, `${CANONICAL_ORIGIN}/`]).toContain(canonicalHref);

  const title = "SheperD | D&D Services for U.S. Importers";
  await expect(page).toHaveTitle(title);
  const description = await page.locator('meta[name="description"]').getAttribute("content");
  expect(description).toMatch(/Managed detention and demurrage support for U\.S\. importers/);
  for (const selector of ['meta[property="og:title"]', 'meta[name="twitter:title"]']) {
    await expect(page.locator(selector)).toHaveAttribute("content", title);
  }
  for (const selector of ['meta[property="og:description"]', 'meta[name="twitter:description"]']) {
    await expect(page.locator(selector)).toHaveAttribute("content", description!);
  }
});

test("keeps /pilot out of search indexing in every environment", async ({ page }) => {
  await page.goto("/pilot", { waitUntil: "networkidle" });
  const robotsContent = await page
    .locator('meta[name="robots"]')
    .getAttribute("content");
  expect(robotsContent).toMatch(/noindex/i);
  expect(robotsContent).toMatch(/nofollow/i);
});

for (const route of ["/privacy", "/terms"] as const) {
  test(`keeps ${route} out of search indexing`, async ({ page }) => {
    await page.goto(route, { waitUntil: "networkidle" });
    const robotsContent = await page
      .locator('meta[name="robots"]')
      .getAttribute("content");
    expect(robotsContent).toMatch(/noindex/i);
  });
}

test("serves crawl policy and sitemap endpoints", async ({ request }) => {
  const robotsResponse = await request.get("/robots.txt");
  expect(robotsResponse.status()).toBe(200);
  const robotsBody = await robotsResponse.text();
  expect(robotsBody).toMatch(/user-agent:\s*\*/i);
  expect(robotsBody).toMatch(IS_PRODUCTION ? /^allow:\s*\//im : /^disallow:\s*\//im);

  const sitemapResponse = await request.get("/sitemap.xml");
  expect(sitemapResponse.status()).toBe(200);
  expect(sitemapResponse.headers()["content-type"]).toMatch(/xml|text/i);
  const sitemapBody = await sitemapResponse.text();
  expect(sitemapBody).toMatch(/<urlset[\s>]/i);
  if (IS_PRODUCTION) {
    expect(sitemapBody.match(/<loc>/g)).toHaveLength(1);
    expect(sitemapBody).toContain(`<loc>${CANONICAL_ORIGIN}/</loc>`);
  } else {
    expect(sitemapBody).not.toContain("<loc>");
  }
});
