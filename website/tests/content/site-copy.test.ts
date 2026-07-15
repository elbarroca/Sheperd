import { describe, expect, it } from "vitest";

import { siteCopy } from "../../src/content/site";
import { publicSources } from "../../src/content/sources";

describe("Preview content", () => {
  it("uses a same-page primary action", () => {
    expect(siteCopy.navigation.some((item) => item.href === "#review-requirements")).toBe(true);
    expect(siteCopy.hero.cta).toBe("Review requirements");
  });

  it("links only to HTTPS primary sources", () => {
    expect(publicSources.length).toBeGreaterThanOrEqual(3);
    for (const source of publicSources) {
      expect(source.href.startsWith("https://")).toBe(true);
    }
  });

  it("states the Preview boundary directly", () => {
    expect(siteCopy.footer.notice).toContain("Preview only");
    expect(siteCopy.footer.notice).toContain("no form");
  });

  it("provides concise detail for each inspectable hero evidence class", () => {
    for (const evidenceClass of siteCopy.hero.evidenceClasses) {
      expect(evidenceClass.label.length).toBeGreaterThan(0);
      expect(evidenceClass.detail.length).toBeGreaterThan(0);
    }
  });
});
