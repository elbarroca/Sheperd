import { chromium } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import assert from "node:assert/strict";

const browser = await chromium.launch();
try {
  const page = await browser.newPage({ reducedMotion: "reduce" });
  await mkdir("qa/invoice-only", { recursive: true });
  for (const width of [320, 375, 768, 1024, 1440, 1920]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.goto("http://127.0.0.1:3211", { waitUntil: "networkidle" });
    for (const section of await page.locator("main > section").all())
      await section.scrollIntoViewIfNeeded();
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
    await page.waitForFunction(() =>
      [...document.querySelectorAll("main img")].every(
        (image) => image.complete && image.naturalWidth > 0,
      ),
    );
    await page.screenshot({
      path: `qa/invoice-only/home-${width}.png`,
      fullPage: true,
    });
    if (width === 375 || width === 1440) await page.screenshot({ path: `qa/invoice-only/hero-${width}.png` });
    console.log(width, await page.locator(".recovery-hero").boundingBox());
  }
  for (const route of ["how-it-works", "for-importers", "about", "pilot", "privacy", "terms"]) {
    for (const width of [375, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(`http://127.0.0.1:3211/${route}`, { waitUntil: "networkidle" });
      for (const section of await page.locator("main section").all()) await section.scrollIntoViewIfNeeded();
      await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth), `${route} overflows at ${width}`);
      await page.screenshot({ path: `qa/invoice-only/${route}-${width}.png`, fullPage: true });
    }
  }
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto("http://127.0.0.1:3211");
  assert((await page.locator("#pilot-scope").boundingBox()).y < 667, "Next section must be visible on short mobile viewport");
  await page.screenshot({ path: "qa/invoice-only/hero-short-mobile.png" });
} finally {
  await browser.close();
}
