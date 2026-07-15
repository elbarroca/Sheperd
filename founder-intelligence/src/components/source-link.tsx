import Link from "next/link";
import type { JSX } from "react";
import { researchFileHref } from "../lib/content";

export function SourceLink({ path, label = "Read source" }: { path: string; label?: string }): JSX.Element {
  return (
    <Link className="source-link" href={researchFileHref(path)}>
      {label}<span aria-hidden="true">→</span>
    </Link>
  );
}
