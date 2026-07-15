import type { Metadata } from "next";
import { AppShell } from "@/components/app-shell";
import { SHEPERD_BRAND } from "@/lib/brand";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: `${SHEPERD_BRAND.name} Founder Intelligence`,
    template: `%s | ${SHEPERD_BRAND.name} Intelligence`,
  },
  description: "Evidence-controlled research, Ricardo interpretation, and founder decisions for SheperD.",
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: SHEPERD_BRAND.logo.path, type: "image/png" },
    ],
    shortcut: "/favicon.svg",
    apple: [{ url: SHEPERD_BRAND.logo.path, type: "image/png" }],
  },
  robots: { index: false, follow: false },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <body><AppShell>{children}</AppShell></body>
    </html>
  );
}
