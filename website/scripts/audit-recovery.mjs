import lighthouse from "lighthouse";
import { chromium } from "@playwright/test";
import { mkdir, writeFile } from "node:fs/promises";

const debugPort = 9224;
const browser = await chromium.launch({ args: [`--remote-debugging-port=${debugPort}`] });
try {
  const result = await lighthouse("http://127.0.0.1:3211", {
    port: debugPort,
    output: "json",
    onlyCategories: ["performance", "accessibility", "best-practices", "seo"],
  });
  if (!result) throw new Error("Lighthouse returned no result");
  await mkdir("qa/invoice-only", { recursive: true });
  await writeFile("qa/invoice-only/lighthouse-mobile.json", result.report);
  console.log(JSON.stringify({ scores: Object.fromEntries(Object.entries(result.lhr.categories).map(([key, category]) => [key, category.score * 100])), lcp: result.lhr.audits["largest-contentful-paint"].numericValue, cls: result.lhr.audits["cumulative-layout-shift"].numericValue, tbt: result.lhr.audits["total-blocking-time"].numericValue }));
} finally {
  await browser.close();
}
