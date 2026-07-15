import { describe, expect, it } from "vitest";
import { SHEPERD_BRAND } from "./brand";

describe("SheperD live brand source", () => {
  it("preserves the observed public identity and asset provenance", () => {
    expect(SHEPERD_BRAND.name).toBe("SheperD");
    expect(SHEPERD_BRAND.publicSite).toBe("https://www.sheperd.io/");
    expect(SHEPERD_BRAND.logo.path).toBe("/brand/sheperd-dog-white.png");
    expect(SHEPERD_BRAND.logo.sha256).toHaveLength(64);
  });

  it("keeps the public contact mismatch explicit", () => {
    expect(SHEPERD_BRAND.publicContactConflict.displayed).not.toBe(SHEPERD_BRAND.publicContactConflict.linked);
    expect(SHEPERD_BRAND.publicContactConflict.state).toBe("unresolved");
  });
});
