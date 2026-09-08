import { expect, test } from "@playwright/test";

const viewports = [
  { name: "320x900", width: 320, height: 900 },
  { name: "375x900", width: 375, height: 900 },
  { name: "768x1024", width: 768, height: 1024 },
  { name: "1024x900", width: 1024, height: 900 },
  { name: "1440x1000", width: 1440, height: 1000 },
  { name: "1920x1080", width: 1920, height: 1080 },
] as const;

test.skip(({ browserName }) => browserName !== "chromium", "Chromium owns visual baselines");

for (const viewport of viewports) {
  test(`matches the ${viewport.name} baseline`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/", { waitUntil: "networkidle" });
    for (const section of await page.locator("main > section").all()) {
      await section.scrollIntoViewIfNeeded();
    }
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
    await expect.poll(() => page.locator("main img").evaluateAll((images) => images.every((image) => (image as HTMLImageElement).complete && (image as HTMLImageElement).naturalWidth > 0))).toBe(true);
    await expect(page).toHaveScreenshot(`home-${viewport.name}.png`, {
      fullPage: true,
    });
  });
}
