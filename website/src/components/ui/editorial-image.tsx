interface EditorialImageProps {
  readonly alt: string;
  readonly className?: string;
  readonly height: number;
  readonly name: string;
  readonly priority?: boolean;
  readonly sizes: string;
  readonly width: number;
  readonly widths: readonly number[];
}

export function EditorialImage({
  alt,
  className = "",
  height,
  name,
  priority = false,
  sizes,
  width,
  widths,
}: EditorialImageProps): React.JSX.Element {
  const avifSources = widths
    .map((sourceWidth) => `/media/${name}-${sourceWidth}.avif ${sourceWidth}w`)
    .join(", ");

  return (
    <picture className={`editorial-image ${className}`.trim()}>
      <source sizes={sizes} srcSet={avifSources} type="image/avif" />
      <img
        alt={alt}
        decoding="async"
        fetchPriority={priority ? "high" : "auto"}
        height={height}
        loading={priority ? "eager" : "lazy"}
        sizes={sizes}
        src={`/media/${name}-960.jpg`}
        width={width}
      />
    </picture>
  );
}
