import type { MetadataRoute } from "next";

import { getPublicationTarget } from "@/content/publication";

export default function sitemap(): MetadataRoute.Sitemap {
  if (getPublicationTarget() === "preview") {
    return [];
  }

  throw new Error(
    "Production sitemap is blocked until canonical origin approval is recorded.",
  );
}
