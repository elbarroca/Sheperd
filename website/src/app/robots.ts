import type { MetadataRoute } from "next";

import { getPublicationTarget } from "@/content/publication";

export default function robots(): MetadataRoute.Robots {
  if (getPublicationTarget() === "preview") {
    return {
      rules: {
        userAgent: "*",
        disallow: "/",
      },
    };
  }

  throw new Error(
    "Production robots policy is blocked until canonical origin approval is recorded.",
  );
}
