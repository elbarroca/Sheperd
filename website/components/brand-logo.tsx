import Image from "next/image";

interface BrandLogoProps {
  compact?: boolean;
}

export function BrandLogo({ compact = false }: BrandLogoProps) {
  return (
    <a className="brand-lockup" href="/" aria-label="SheperD home">
      <Image
        className="brand-mark"
        src="/brand/sheperd-logo.png"
        width={512}
        height={395}
        sizes={compact ? "36px" : "44px"}
        quality={100}
        loading="eager"
        fetchPriority={compact ? "low" : "high"}
        alt=""
      />
      <span>SheperD</span>
    </a>
  );
}
