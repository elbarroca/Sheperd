export function Distribution({
  title,
  eyebrow,
  counts,
}: {
  title: string;
  eyebrow: string;
  counts: Record<string, number>;
}) {
  const entries = Object.entries(counts).sort((left, right) => right[1] - left[1]);
  const maximum = Math.max(...entries.map(([, value]) => value), 1);
  return (
    <article className="distribution-card">
      <p className="eyebrow">{eyebrow}</p>
      <h3>{title}</h3>
      <div className="distribution-list">
        {entries.map(([label, value]) => (
          <div key={label} className="distribution-row">
            <div className="distribution-label"><span>{label.replaceAll("-", " ")}</span><strong>{value}</strong></div>
            <div className="distribution-track"><span style={{ width: `${(value / maximum) * 100}%` }} /></div>
          </div>
        ))}
      </div>
    </article>
  );
}
