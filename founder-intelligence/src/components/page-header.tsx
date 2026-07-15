import type { ReactNode } from "react";

export function PageHeader({
  eyebrow,
  title,
  description,
  meta,
}: {
  eyebrow: string;
  title: string;
  description: string;
  meta?: ReactNode;
}) {
  return (
    <header className="page-header">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="page-lede">{description}</p>
      </div>
      {meta ? <div className="page-meta">{meta}</div> : null}
    </header>
  );
}
