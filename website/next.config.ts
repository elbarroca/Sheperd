import type { NextConfig } from "next";

const isDevelopment = process.env.NODE_ENV === "development";

if (
  process.env.BUILD_TARGET === "production" ||
  process.env.VERCEL_ENV === "production"
) {
  throw new Error(
    "PRODUCTION_PUBLICATION_BLOCKED: publication authority, approved claims, legal notice, and production ownership remain unresolved.",
  );
}

const nextConfig: NextConfig = {
  poweredByHeader: false,
  reactStrictMode: true,
  images: {
    formats: ["image/avif", "image/webp"],
    qualities: [78, 90, 100],
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Robots-Tag", value: "noindex, nofollow, noarchive" },
          { key: "Referrer-Policy", value: "no-referrer" },
          ...(!isDevelopment
            ? [{ key: "X-Content-Type-Options", value: "nosniff" }]
            : []),
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
          {
            key: "Content-Security-Policy",
            value:
              "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
