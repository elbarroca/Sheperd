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
    await expect(page).toHaveScreenshot(`home-${viewport.name}.png`, {
      fullPage: true,
    });
  });
}
