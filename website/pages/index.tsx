import Head from "next/head";

import { RecoveryCorridor } from "@/components/recovery-corridor";

export default function HomePage() {
  return (
    <>
      <Head>
        <title>SheperD | Shipping Container Charge Recovery</title>
        <meta
          name="description"
          content="Recover eligible demurrage and detention overcharges from shipping-container invoices with a clear invoice-to-refund workflow."
        />
        <meta name="robots" content="noindex,nofollow,noarchive,noimageindex" />
        <meta property="og:type" content="website" />
        <meta
          property="og:title"
          content="SheperD | Shipping Container Charge Recovery"
        />
        <meta
          property="og:description"
          content="Recover eligible demurrage and detention overcharges from shipping-container invoices with a clear invoice-to-refund workflow."
        />
        <meta property="og:image" content="/og/recovery-corridor.png" />
        <meta property="og:image:width" content="1200" />
        <meta property="og:image:height" content="630" />
        <meta
          property="og:image:alt"
          content="SheperD shipping container charge recovery corridor"
        />
        <meta name="twitter:card" content="summary_large_image" />
        <meta
          name="twitter:title"
          content="SheperD | Shipping Container Charge Recovery"
        />
        <meta
          name="twitter:description"
          content="Recover eligible demurrage and detention overcharges from shipping-container invoices with a clear invoice-to-refund workflow."
        />
        <meta name="twitter:image" content="/og/recovery-corridor.png" />
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link
          rel="icon"
          href="/brand/sheperd-favicon-32.png"
          type="image/png"
          sizes="32x32"
        />
        <link
          rel="apple-touch-icon"
          href="/brand/sheperd-apple-touch-icon.png"
          sizes="180x180"
        />
        <link rel="manifest" href="/site.webmanifest" />
      </Head>
      <RecoveryCorridor />
    </>
  );
}
