import { Head, Html, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta name="color-scheme" content="dark light" />
        <meta name="theme-color" content="#061220" />
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
      <body>
        <noscript>
          <style>{`.motion-reveal { opacity: 1 !important; transform: none !important; } .motion-toggle { display: none !important; } html { scroll-behavior: auto !important; }`}</style>
        </noscript>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
