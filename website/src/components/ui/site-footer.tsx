import Link from "next/link";

import { siteCopy } from "@/content/site";

export function SiteFooter(): React.JSX.Element {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner">
        <div>
          <span className="wordmark">{siteCopy.brand}</span>
          <p>{siteCopy.footer.notice}</p>
        </div>
        <nav aria-label="Preview notices">
          <Link href="/privacy">Data notice</Link>
          <Link href="/terms">Use notice</Link>
        </nav>
      </div>
    </footer>
  );
}
