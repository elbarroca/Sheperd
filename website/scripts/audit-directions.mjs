import AxeBuilder from "@axe-core/playwright";
import { chromium } from "@playwright/test";

const BASE_URL = "http://127.0.0.1:8090";
const directions = [
  "direction-a-evidence-tide",
  "direction-b-margin-notes",
  "direction-c-terminal-ledger",
];

const browser = await chromium.launch();
const results = [];

try {
  for (const direction of directions) {
    const context = await browser.newContext({ viewport: { width: 320, height: 900 } });
    const page = await context.newPage();
    const externalRequests = [];
    page.on("request", (request) => {
      const url = new URL(request.url());
      if (url.hostname !== "127.0.0.1") externalRequests.push(request.url());
    });
    await page.goto(`${BASE_URL}/${direction}/`, { waitUntil: "networkidle" });
    const metrics = await page.evaluate(() => ({
      title: document.title,
      h1Count: document.querySelectorAll("h1").length,
      formCount: document.querySelectorAll("form").length,
      fieldCount: document.querySelectorAll("input, textarea, select").length,
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      minimumTarget: Math.min(
        ...Array.from(document.querySelectorAll("a, button"), (node) => {
          const rect = node.getBoundingClientRect();
          return Math.min(rect.width, rect.height);
        }),
      ),
    }));
    const axe = await new AxeBuilder({ page }).analyze();
    results.push({
      direction,
      ...metrics,
      horizontalOverflow: metrics.scrollWidth > metrics.clientWidth,
      axeViolations: axe.violations.map(({ id, impact }) => ({ id, impact })),
      externalRequests,
    });
    await context.close();
  }
} finally {
  await browser.close();
}

console.log(JSON.stringify(results, null, 2));
