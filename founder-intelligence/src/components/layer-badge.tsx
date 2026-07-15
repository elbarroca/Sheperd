export function LayerBadge({ layer }: { layer: string }) {
  const label = layer === "ricardo-interpretation" ? "Ricardo note" : layer.replaceAll("-", " ");
  return <span className={`layer-badge layer-${layer}`}>{label}</span>;
}
