import Head from "next/head";
import { useRef, type ReactElement, type ReactNode } from "react";
import { useRecoveryMotion } from "./use-recovery-motion";
import { SiteHeader } from "./site-header";
import { SiteFooter } from "./site-footer";
import { MotionShell } from "./motion-shell";

interface RecoveryLayoutProps {
  title: string;
  description: string;
  children: ReactNode;
}

export function RecoveryLayout({
  title,
  description,
  children,
}: RecoveryLayoutProps): ReactElement {
  const main = useRef<HTMLElement>(null);
  useRecoveryMotion(main);
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
        <meta name="robots" content="noindex,nofollow,noarchive,noimageindex" />
        <meta property="og:type" content="website" />
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <meta property="og:image" content="/og/recovery-port.webp" />
        <meta property="og:image:width" content="1200" />
        <meta property="og:image:height" content="630" />
        <meta
          property="og:image:alt"
          content="SheperD conceptual container port and shipping activity"
        />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={title} />
        <meta name="twitter:description" content={description} />
        <meta name="twitter:image" content="/og/recovery-port.webp" />
        <link rel="icon" href="/favicon.ico" sizes="any" />
      </Head>
      <MotionShell>
        <div className="recovery-site">
          <a className="skip-link" href="#main-content">
            Skip to content
          </a>
          <SiteHeader />
          <main ref={main} id="main-content" tabIndex={-1}>
            {children}
          </main>
          <SiteFooter />
        </div>
      </MotionShell>
    </>
  );
}
