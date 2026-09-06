import type { NextConfig } from "next";

import {
  getSeoPolicy,
  isProductionEnvironment,
  type SeoPath,
} from "./lib/seo";

const isDevelopment = process.env.NODE_ENV === "development";
const seoEnvironment = { VERCEL_ENV: process.env.VERCEL_ENV };
const isProduction = isProductionEnvironment(seoEnvironment);
const seoPaths: SeoPath[] = ["/", "/pilot", "/privacy", "/terms"];

const nextConfig: NextConfig = {
  poweredByHeader: false,
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_SHEPERD_SEO_INDEXABLE: isProduction ? "true" : "false",
    // Intake activation requires a separate release, not an environment-only toggle.
    NEXT_PUBLIC_PILOT_DELIVERY_ENABLED: "false",
  },
  images: {
    formats: ["image/avif", "image/webp"],
    qualities: [78, 90, 100],
  },
  async headers() {
    const securityHeaders = [
      { key: "Referrer-Policy", value: "no-referrer" },
      ...(!isDevelopment
        ? [{ key: "X-Content-Type-Options", value: "nosniff" }]
        : []),
      {
        key: "Permissions-Policy",
        value: "camera=(), microphone=(), geolocation=()",
      },
      {
        key: "Content-Security-Policy",
        value:
          "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
      },
    ];

    const defaultRobotsHeader = isProduction
      ? "index, follow"
      : "noindex, nofollow, noarchive";

    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Robots-Tag", value: defaultRobotsHeader },
          ...securityHeaders,
        ],
      },
      ...seoPaths.map((path) => ({
        source: path,
        headers: [
          {
            key: "X-Robots-Tag",
            value: getSeoPolicy(path, { environment: seoEnvironment })
              .xRobotsTag,
          },
        ],
      })),
    ];
  },
};

export default nextConfig;
