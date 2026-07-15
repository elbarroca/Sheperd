"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { FilesIcon } from "@phosphor-icons/react/dist/csr/Files";
import { GraphIcon } from "@phosphor-icons/react/dist/csr/Graph";
import { NotePencilIcon } from "@phosphor-icons/react/dist/csr/NotePencil";
import { UsersFourIcon } from "@phosphor-icons/react/dist/csr/UsersFour";

const links = [
  { href: "/competitors", label: "Competitors", icon: UsersFourIcon },
  { href: "/market", label: "Market", icon: GraphIcon },
  { href: "/michael", label: "Michael", icon: NotePencilIcon },
  { href: "/knowledge", label: "Knowledge map", icon: FilesIcon },
];

export function Navigation() {
  const pathname = usePathname();
  const navRef = useRef<HTMLElement | null>(null);
  const activeLinkRef = useRef<HTMLAnchorElement | null>(null);

  useEffect(() => {
    const nav = navRef.current;
    const activeLink = activeLinkRef.current;
    if (!nav || !activeLink) return;
    nav.scrollLeft = activeLink.offsetLeft - (nav.clientWidth - activeLink.clientWidth) / 2;
  }, [pathname]);

  return (
    <nav ref={navRef} className="side-nav" aria-label="Founder intelligence sections">
      {links.map((link) => {
        const active = pathname.startsWith(link.href);
        const Icon = link.icon;
        return (
          <Link
            key={link.href}
            ref={active ? activeLinkRef : undefined}
            href={link.href}
            className="nav-link"
            aria-current={active ? "page" : undefined}
          >
            <Icon aria-hidden="true" size={17} weight={active ? "fill" : "regular"} />
            <span>{link.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
