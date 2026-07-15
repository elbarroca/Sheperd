import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "SheperD Preview",
    short_name: "SheperD",
    description: "Design and engineering Preview.",
    start_url: "/",
    display: "standalone",
    background_color: "#fbfcfc",
    theme_color: "#fbfcfc",
    icons: [
      {
        src: "/icon.svg",
        sizes: "any",
        type: "image/svg+xml",
      },
    ],
  };
}
