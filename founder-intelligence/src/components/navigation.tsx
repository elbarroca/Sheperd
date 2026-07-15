"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Founder brief", mark: "FB" },
  { href: "/research", label: "Research", mark: "RX" },
  { href: "/mikey", label: "Mikey workflow", mark: "MW" },
  { href: "/ricardo", label: "Ricardo notes", mark: "RN" },
  { href: "/improvements", label: "Priority lab", mark: "PL" },
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
