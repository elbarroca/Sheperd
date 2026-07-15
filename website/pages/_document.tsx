import { Head, Html, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta name="color-scheme" content="dark light" />
        <meta name="theme-color" content="#041426" />
      </Head>
      <body>
        <noscript>
          <style>{`.motion-reveal { opacity: 1 !important; transform: none !important; }`}</style>
        </noscript>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
