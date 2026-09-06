import { expect, test } from "@playwright/test";

const CANONICAL_ORIGIN = "https://sheperd-website.vercel.app";

test("uses the preview robots policy and canonical homepage origin", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" });

  await expect(page.locator('meta[name="robots"]')).toHaveAttribute(
    "content",
    /noindex.*nofollow/i,
  );
  const canonicalHref = await page
    .locator('link[rel="canonical"]')
    .getAttribute("href");
  expect([CANONICAL_ORIGIN, `${CANONICAL_ORIGIN}/`]).toContain(canonicalHref);
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
  expect(robotsBody).toMatch(/disallow:\s*\//i);

  const sitemapResponse = await request.get("/sitemap.xml");
  expect(sitemapResponse.status()).toBe(200);
  expect(sitemapResponse.headers()["content-type"]).toMatch(/xml|text/i);
  const sitemapBody = await sitemapResponse.text();
  expect(sitemapBody).toMatch(/<urlset[\s>]/i);
  expect(sitemapBody).not.toContain("<loc>");
});
