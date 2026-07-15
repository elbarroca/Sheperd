import { expect, test } from "@playwright/test";

const VIEWPORTS = [
  { name: "mobile-320", width: 320, height: 900 },
  { name: "mobile-375", width: 375, height: 900 },
  { name: "tablet-768", width: 768, height: 1024 },
  { name: "desktop-1024", width: 1024, height: 900 },
  { name: "desktop-1440", width: 1440, height: 1000 },
  { name: "wide-1920", width: 1920, height: 1080 },
] as const;

test.describe("responsive visual contract", () => {
  for (const viewport of VIEWPORTS) {
    test(`${viewport.name} has no horizontal overflow and matches baseline`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto("/");
      await page.evaluate(() => document.fonts.ready);
      const invalidImages = await page.locator("img").evaluateAll(async (images) => {
        const htmlImages = images.filter(
          (image): image is HTMLImageElement => image instanceof HTMLImageElement,
        );
        for (const image of htmlImages) {
          image.loading = "eager";
        }
        await Promise.allSettled(htmlImages.map((image) => image.decode()));
        return (
          images.length - htmlImages.length +
          htmlImages.filter((image) => !image.complete || image.naturalWidth === 0).length
        );
      });
      expect(invalidImages).toBe(0);

      const sizes = await page.evaluate(() => ({
        documentWidth: document.documentElement.scrollWidth,
        viewportWidth: document.documentElement.clientWidth,
      }));
      expect(sizes.documentWidth).toBeLessThanOrEqual(sizes.viewportWidth);
      await expect(page).toHaveScreenshot(`${viewport.name}.png`, {
        fullPage: true,
        animations: "disabled",
      });
    });
  }
});
