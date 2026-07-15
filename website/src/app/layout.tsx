import type { Metadata, Viewport } from "next";
import { Azeret_Mono, Barlow } from "next/font/google";

import { SiteFooter } from "@/components/ui/site-footer";
import { SiteHeader } from "@/components/ui/site-header";
import { getPublicationTarget } from "@/content/publication";

import "@/styles/globals.css";

const sans = Barlow({
  display: "swap",
  subsets: ["latin"],
  variable: "--font-sans",
  weight: ["400", "500", "600"],
});

const mono = Azeret_Mono({
  display: "swap",
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "500"],
});

const isPreview = getPublicationTarget() === "preview";
const deploymentHost = process.env.VERCEL_URL;

export const metadata: Metadata = {
  metadataBase: new URL(
    deploymentHost ? `https://${deploymentHost}` : "http://localhost:3000",
  ),
  title: {
    default: "SheperD | Preview",
    template: "%s | SheperD Preview",
  },
  description:
    "A no-collection design and engineering Preview for reviewing record-alignment questions.",
  applicationName: "SheperD Preview",
  robots: isPreview
    ? {
        index: false,
        follow: false,
        nocache: true,
        googleBot: {
          index: false,
          follow: false,
          noimageindex: true,
        },
      }
    : undefined,
  openGraph: {
    title: "SheperD | Preview",
    description: "A design and engineering Preview for record review structure.",
    siteName: "SheperD Preview",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "SheperD | Preview",
    description: "A design and engineering Preview for record review structure.",
  },
  icons: {
    icon: "/icon.svg",
  },
};

export const viewport: Viewport = {
  colorScheme: "light",
  themeColor: "#eef4f3",
};

interface RootLayoutProps {
  readonly children: React.ReactNode;
}

export default function RootLayout({
  children,
}: RootLayoutProps): React.JSX.Element {
  return (
    <html className={`${sans.variable} ${mono.variable}`} lang="en">
      <head>
        <link
          as="image"
          fetchPriority="high"
          href="/media/sheperd-control-room-v2-960.avif"
          imageSizes="(max-width: 767px) 100vw, (max-width: 1023px) 78vw, 48vw"
          imageSrcSet="/media/sheperd-control-room-v2-640.avif 640w, /media/sheperd-control-room-v2-960.avif 960w, /media/sheperd-control-room-v2-1440.avif 1440w"
          rel="preload"
          type="image/avif"
        />
      </head>
      <body>
        <a className="skip-link" href="#main-content">
          Skip to content
        </a>
        <div className="site-shell">
          <SiteHeader />
          {children}
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
