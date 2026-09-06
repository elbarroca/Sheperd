import { describe, expect, it } from "vitest";

import {
  CANONICAL_ORIGIN,
  getRobotsTxt,
  getSeoMetadata,
  getSeoPolicy,
  getSitemapXml,
} from "../../lib/seo";

const productionEnvironment = {
  VERCEL_ENV: "production",
  BUILD_TARGET: "preview",
};
const previewEnvironment = { VERCEL_ENV: "preview" };
const noVercelEnvironment = {};

describe("shared SEO policy", () => {
  it("indexes the homepage only in real Vercel production", () => {
    expect(
      getSeoPolicy("/", { environment: productionEnvironment }),
    ).toMatchObject({
      canonicalUrl: `${CANONICAL_ORIGIN}/`,
      indexable: true,
      includeInSitemap: true,
      robots: "index, follow",
    });

    expect(getSeoPolicy("/", { environment: previewEnvironment }).indexable).toBe(
      false,
    );
    expect(getSeoPolicy("/", { environment: noVercelEnvironment }).indexable).toBe(
      false,
    );
  });

  it("keeps disabled pilot intake out of the index in production", () => {
    const policy = getSeoPolicy("/pilot", {
      environment: productionEnvironment,
    });

    expect(policy).toMatchObject({
      canonicalUrl: `${CANONICAL_ORIGIN}/pilot`,
      indexable: false,
      includeInSitemap: false,
      robots: "noindex, nofollow, noarchive",
      xRobotsTag: "noindex, nofollow, noarchive",
    });
  });

  it("keeps informational pages noindex while allowing follow", () => {
    for (const path of ["/privacy", "/terms"] as const) {
      expect(
        getSeoPolicy(path, { environment: productionEnvironment }),
      ).toMatchObject({
        indexable: false,
        includeInSitemap: false,
        robots: "noindex, follow, noarchive",
      });
    }
  });

  it("builds absolute canonical and social metadata from the shared policy", () => {
    expect(
      getSeoMetadata({
        title: "SheperD",
        description: "Shipping container recovery review.",
        path: "/",
        environment: productionEnvironment,
      }),
    ).toMatchObject({
      title: "SheperD",
      description: "Shipping container recovery review.",
      canonicalUrl: `${CANONICAL_ORIGIN}/`,
      socialImageUrl: `${CANONICAL_ORIGIN}/og/sheperd-recovery.png`,
      robots: "index, follow",
      includeStructuredData: true,
    });

    expect(
      getSeoMetadata({
        title: "Pilot",
        description: "Pilot intake.",
        path: "/pilot",
        environment: productionEnvironment,
      }).includeStructuredData,
    ).toBe(false);
  });

  it("uses the same production gate for robots and sitemap", () => {
    const productionRobots = getRobotsTxt({
      environment: productionEnvironment,
    });
    const previewRobots = getRobotsTxt({ environment: previewEnvironment });
    const noVercelRobots = getRobotsTxt({
      environment: noVercelEnvironment,
    });
    const productionSitemap = getSitemapXml({
      environment: productionEnvironment,
    });
    const previewSitemap = getSitemapXml({ environment: previewEnvironment });

    expect(productionRobots).toContain("User-agent: *");
    expect(productionRobots).toContain("Allow: /");
    expect(productionRobots).not.toMatch(/^Disallow:/m);
    expect(productionRobots).toContain(
      `Sitemap: ${CANONICAL_ORIGIN}/sitemap.xml`,
    );
    expect(productionRobots).not.toContain("Disallow: /\n");
    expect(productionSitemap).toContain(`<loc>${CANONICAL_ORIGIN}/</loc>`);

    expect(previewRobots).toContain("Disallow: /\n");
    expect(previewRobots).not.toContain("Allow: /");
    expect(noVercelRobots).toBe(previewRobots);
    expect(previewSitemap).not.toContain("<loc>");
  });
});
