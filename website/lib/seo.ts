export const CANONICAL_ORIGIN = "https://sheperd-website.vercel.app";
export const SOCIAL_IMAGE_PATH = "/og/sheperd-recovery.png";
export const SOCIAL_IMAGE_URL = `${CANONICAL_ORIGIN}${SOCIAL_IMAGE_PATH}`;
export const ORGANIZATION_LOGO_URL = `${CANONICAL_ORIGIN}/brand/sheperd-icon-512.png`;
export const SOCIAL_IMAGE_ALT = "SheperD: Recover the D&D money hiding in your invoices, over a container terminal at dusk.";

export const INDEXABLE_ROBOTS = "index, follow";
export const NOINDEX_ROBOTS = "noindex, nofollow, noarchive";
export const NOINDEX_FOLLOW_ROBOTS = "noindex, follow, noarchive";

export const SEO_SERIALIZED_PRODUCTION_FLAG =
  "NEXT_PUBLIC_SHEPERD_SEO_INDEXABLE";

export type SeoPath = "/" | "/pilot" | "/privacy" | "/terms";

export interface SeoEnvironment {
  VERCEL_ENV?: string;
  NEXT_PUBLIC_SHEPERD_SEO_INDEXABLE?: string;
}

export interface SeoPolicyOptions {
  environment?: SeoEnvironment;
  indexable?: boolean;
}

export interface SeoPolicy {
  path: SeoPath;
  canonicalUrl: string;
  isProduction: boolean;
  indexable: boolean;
  includeInSitemap: boolean;
  robots: string;
  xRobotsTag: string;
}

export interface SeoMetadataOptions extends SeoPolicyOptions {
  title: string;
  description: string;
  path: SeoPath;
}

export interface SeoMetadata {
  title: string;
  description: string;
  canonicalUrl: string;
  siteName: "SheperD";
  openGraphType: "website";
  socialImageUrl: string;
  socialImageAlt: string;
  twitterCard: "summary_large_image";
  robots: string;
  xRobotsTag: string;
  includeStructuredData: boolean;
}

function runtimeEnvironment(): SeoEnvironment {
  return {
    VERCEL_ENV: process.env.VERCEL_ENV,
    NEXT_PUBLIC_SHEPERD_SEO_INDEXABLE:
      process.env.NEXT_PUBLIC_SHEPERD_SEO_INDEXABLE,
  };
}

export function isProductionEnvironment(
  environment: SeoEnvironment = runtimeEnvironment(),
): boolean {
  if (environment.VERCEL_ENV !== undefined) {
    return environment.VERCEL_ENV === "production";
  }

  return environment.NEXT_PUBLIC_SHEPERD_SEO_INDEXABLE === "true";
}

export function getCanonicalUrl(path: SeoPath): string {
  return `${CANONICAL_ORIGIN}${path}`;
}

export function getSeoPolicy(
  path: SeoPath,
  options: SeoPolicyOptions = {},
): SeoPolicy {
  const isProduction = isProductionEnvironment(options.environment);
  const homepageRequestedIndexing = options.indexable ?? path === "/";
  const pathCanBeIndexed = path === "/";
  const indexable =
    isProduction && pathCanBeIndexed && homepageRequestedIndexing;
  const robots = indexable
    ? INDEXABLE_ROBOTS
    : path === "/privacy" || path === "/terms"
      ? NOINDEX_FOLLOW_ROBOTS
      : NOINDEX_ROBOTS;

  return {
    path,
    canonicalUrl: getCanonicalUrl(path),
    isProduction,
    indexable,
    includeInSitemap: indexable,
    robots,
    xRobotsTag: robots,
  };
}

export function getSeoMetadata(options: SeoMetadataOptions): SeoMetadata {
  const policy = getSeoPolicy(options.path, options);

  return {
    title: options.title,
    description: options.description,
    canonicalUrl: policy.canonicalUrl,
    siteName: "SheperD",
    openGraphType: "website",
    socialImageUrl: SOCIAL_IMAGE_URL,
    socialImageAlt: SOCIAL_IMAGE_ALT,
    twitterCard: "summary_large_image",
    robots: policy.robots,
    xRobotsTag: policy.xRobotsTag,
    includeStructuredData: options.path === "/",
  };
}

export function getRobotsTxt(options: SeoPolicyOptions = {}): string {
  const homepagePolicy = getSeoPolicy("/", options);
  const lines = ["User-agent: *"];

  if (!homepagePolicy.indexable) {
    lines.push("Disallow: /");
  } else {
    lines.push("Allow: /");
  }

  lines.push("", `Sitemap: ${CANONICAL_ORIGIN}/sitemap.xml`, "");
  return lines.join("\n");
}

export function getSitemapXml(options: SeoPolicyOptions = {}): string {
  const homepagePolicy = getSeoPolicy("/", options);
  const homepageEntry = homepagePolicy.includeInSitemap
    ? `\n  <url>\n    <loc>${homepagePolicy.canonicalUrl}</loc>\n  </url>`
    : "";

  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    homepageEntry,
    "</urlset>",
    "",
  ].join("\n");
}
