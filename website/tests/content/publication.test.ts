import { afterEach, describe, expect, it } from "vitest";

import { productionBlockers } from "../../src/content/blockers";
import { claims } from "../../src/content/claims";
import {
  channelForTarget,
  getPublicationTarget,
  isClaimPublishable,
  resolveClaim,
} from "../../src/content/publication";

const originalTarget = process.env.SITE_PUBLICATION_TARGET;

afterEach(() => {
  if (originalTarget === undefined) {
    delete process.env.SITE_PUBLICATION_TARGET;
  } else {
    process.env.SITE_PUBLICATION_TARGET = originalTarget;
  }
});

describe("publication gate", () => {
  it("defaults unknown and local environments to Preview", () => {
    process.env.SITE_PUBLICATION_TARGET = "local";
    expect(getPublicationTarget()).toBe("preview");
  });

  it("recognizes an explicit production target", () => {
    process.env.SITE_PUBLICATION_TARGET = "production";
    expect(getPublicationTarget()).toBe("production");
  });

  it("suppresses every unapproved candidate claim", () => {
    for (const claim of Object.values(claims)) {
      expect(isClaimPublishable(claim, channelForTarget("preview"))).toBe(false);
      expect(isClaimPublishable(claim, channelForTarget("production"))).toBe(false);
      expect(resolveClaim(claim.claimId as keyof typeof claims, "preview")).toBeNull();
    }
  });

  it("keeps every production blocker unresolved", () => {
    expect(productionBlockers).toHaveLength(12);
    expect(productionBlockers.every((blocker) => !blocker.resolved)).toBe(true);
  });
});
