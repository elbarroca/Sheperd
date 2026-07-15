"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Brief", mark: "01" },
  { href: "/improvements", label: "Decision map", mark: "02" },
  { href: "/mikey", label: "Operating plan", mark: "03" },
  { href: "/research", label: "Evidence", mark: "04" },
  { href: "/ricardo", label: "Analysis", mark: "05" },
];

export function Navigation() {
  const pathname = usePathname();
  return (
    <nav className="side-nav" aria-label="Founder intelligence sections">
      {links.map((link) => {
        const active = link.href === "/" ? pathname === "/" : pathname.startsWith(link.href);
        return (
          <Link key={link.href} href={link.href} className="nav-link" aria-current={active ? "page" : undefined}>
            <span className="nav-mark" aria-hidden="true">{link.mark}</span>
            <span>{link.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
