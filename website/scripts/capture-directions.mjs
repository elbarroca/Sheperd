import { mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const BASE_URL = "http://127.0.0.1:8090";
const directions = [
  "direction-a-evidence-tide",
  "direction-b-margin-notes",
  "direction-c-terminal-ledger",
];
const viewports = [
  { name: "mobile-375", width: 375, height: 900 },
  { name: "desktop-1440", width: 1440, height: 1000 },
];

const browser = await chromium.launch();

try {
  for (const direction of directions) {
    const outputDir = fileURLToPath(
      new URL(`../design-experiments/${direction}/`, import.meta.url),
    );
    await mkdir(outputDir, { recursive: true });

    for (const viewport of viewports) {
      const page = await browser.newPage({ viewport });
      await page.goto(`${BASE_URL}/${direction}/`, { waitUntil: "networkidle" });
      await page.emulateMedia({ reducedMotion: "reduce" });
      await page.screenshot({
        path: `${outputDir}/${viewport.name}.png`,
        fullPage: true,
        animations: "disabled",
      });
      await page.close();
    }
  }
} finally {
  await browser.close();
}
