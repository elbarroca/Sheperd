import { describe, expect, it } from "vitest";

import {
  benefits,
  containerEvents,
  liveSource,
  marketStats,
  missionOutcomes,
  navigationItems,
  recoverySteps,
  volumeOptions,
} from "../../lib/content";

describe("Recovery Corridor content", () => {
  it("preserves the three live market figures", () => {
    expect(marketStats.map(({ value }) => value)).toEqual([
      "$2.1B",
      "$6.2B",
      "3 years",
    ]);
  });

  it("preserves the exact three-step recovery sequence", () => {
    expect(recoverySteps.map(({ title }) => title)).toEqual([
      "Send container invoices",
      "We audit every charge",
      "Recover eligible fees",
    ]);
  });

  it("keeps the three operating benefits", () => {
    expect(benefits.map(({ title }) => title)).toEqual([
      "Zero upfront cost",
      "Less internal work",
      "Every charge tracked",
    ]);
  });

  it("states the three company mission outcomes", () => {
    expect(missionOutcomes.map(({ title }) => title)).toEqual([
      "Prevent leakage",
      "Recover eligible fees",
      "Create accountability",
    ]);
  });

  it("tracks the complete import-container event record", () => {
    expect(containerEvents.map(({ title }) => title)).toEqual([
      "Last free day (LFD)",
      "Terminal availability",
      "Gate-out",
      "Empty return",
      "Invoice line items",
    ]);
  });

  it("keeps every navigation target on the page", () => {
    expect(navigationItems.every(({ href }) => href.startsWith("#"))).toBe(true);
  });

  it("keeps the complete volume range and official contact", () => {
    expect(volumeOptions).toHaveLength(4);
    expect(liveSource.contactEmail).toBe("info@sheperd.io");
    expect(new URL(liveSource.linkedin).hostname).toBe("www.linkedin.com");
  });
});
