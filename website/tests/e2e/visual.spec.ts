import { expect, test } from "@playwright/test";

test.skip(({ browserName }) => browserName !== "chromium", "Chromium owns visual baselines");

const visualViewports = [
  {
    name: "desktop",
    width: 1440,
    height: 1000,
  },
  {
    name: "mobile",
    width: 390,
    height: 900,
  },
] as const;

for (const viewport of visualViewports) {
  test(`captures the redesign hero and full page at ${viewport.name}`, async ({
    page,
  }) => {
    await page.setViewportSize(viewport);
    await page.goto("/", { waitUntil: "networkidle" });

    await expect(page).toHaveScreenshot(`home-redesign-${viewport.name}-full.png`, {
      animations: "disabled",
      caret: "hide",
      fullPage: true,
    });
    await expect(page.getByTestId("hero-scene")).toHaveScreenshot(
      `home-redesign-${viewport.name}-hero.png`,
      {
        animations: "disabled",
        caret: "hide",
      },
    );
  });
}
