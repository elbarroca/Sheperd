const steps = ["Billing", "Operational", "Governing", "Stop"] as const;

export function RecordMarker() {
  return (
    <aside className="marker-margin" aria-label="Evidence progress">
      <div className="marker-rail">
        <p className="rail-label">Review sequence</p>
        <ol className="rail-track">
          {steps.map((step, index) => (
            <li
              className="rail-item"
              aria-current={index === 0 ? "step" : undefined}
              key={step}
            >
              {step}
            </li>
          ))}
        </ol>
        <span className="marker-cursor" aria-hidden="true" />
        <p className="marker-status">Start with Billing. Stop after Governing.</p>
        <p className="reduced-motion-note">
          Reduced motion: the complete sequence remains visible without reveal motion.
        </p>
      </div>
    </aside>
  );
}
