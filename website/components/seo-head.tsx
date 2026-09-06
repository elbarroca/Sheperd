import Head from "next/head";

import {
  CANONICAL_ORIGIN,
  getSeoMetadata,
  ORGANIZATION_LOGO_URL,
  type SeoPath,
} from "@/lib/seo";

export interface SeoHeadProps {
  title: string;
  description: string;
  path: SeoPath;
  indexable?: boolean;
}

const STRUCTURED_DATA = [
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "SheperD",
    url: CANONICAL_ORIGIN,
    logo: ORGANIZATION_LOGO_URL,
  },
  {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "SheperD",
    url: CANONICAL_ORIGIN,
  },
] as const;

export function SeoHead({
  title,
  description,
  path,
  indexable,
}: SeoHeadProps) {
  const metadata = getSeoMetadata({ title, description, path, indexable });

  return (
    <Head>
      <title key="title">{metadata.title}</title>
      <meta key="description" name="description" content={metadata.description} />
      <meta key="robots" name="robots" content={metadata.robots} />
      <link key="canonical" rel="canonical" href={metadata.canonicalUrl} />

      <meta key="og:type" property="og:type" content={metadata.openGraphType} />
      <meta key="og:url" property="og:url" content={metadata.canonicalUrl} />
      <meta key="og:site_name" property="og:site_name" content={metadata.siteName} />
      <meta key="og:locale" property="og:locale" content="en_US" />
      <meta key="og:title" property="og:title" content={metadata.title} />
      <meta
        key="og:description"
        property="og:description"
        content={metadata.description}
      />
      <meta key="og:image" property="og:image" content={metadata.socialImageUrl} />
      <meta key="og:image:type" property="og:image:type" content="image/png" />
      <meta key="og:image:width" property="og:image:width" content="1200" />
      <meta key="og:image:height" property="og:image:height" content="630" />
      <meta
        key="og:image:alt"
        property="og:image:alt"
        content={metadata.socialImageAlt}
      />

      <meta key="twitter:card" name="twitter:card" content={metadata.twitterCard} />
      <meta key="twitter:title" name="twitter:title" content={metadata.title} />
      <meta
        key="twitter:description"
        name="twitter:description"
        content={metadata.description}
      />
      <meta
        key="twitter:image"
        name="twitter:image"
        content={metadata.socialImageUrl}
      />
      <meta
        key="twitter:image:alt"
        name="twitter:image:alt"
        content={metadata.socialImageAlt}
      />

      {metadata.includeStructuredData ? (
        <script
          key="structured-data"
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(STRUCTURED_DATA) }}
        />
      ) : null}
    </Head>
  );
}
