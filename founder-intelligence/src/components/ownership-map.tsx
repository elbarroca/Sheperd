const roles = [
  { name: "Avi", responsibility: "Approves authority, commercial terms, claims, and activation" },
  { name: "Product and data", responsibility: "Owns capability truth, delivery evidence, and capacity" },
  { name: "Domain and legal", responsibility: "Reviews regulatory meaning, eligibility, and claims" },
  { name: "Privacy and security", responsibility: "Approves systems, data classes, retention, and incidents" },
  { name: "Website and content", responsibility: "Publishes only approved, accessible, privacy-safe material" },
] as const;

export function OwnershipMap() {
  return (
    <section className="ownership-map section-block" aria-labelledby="ownership-map-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Ownership map</p>
          <h2 id="ownership-map-title">Michael coordinates the system, specialists retain material authority</h2>
        </div>
        <p>Each connection is an operating dependency, not a transfer of approval rights.</p>
      </div>
      <div className="ownership-visual">
        <div className="ownership-center">
          <span>Operating lead</span>
          <strong>Michael</strong>
          <p>GTM and Revenue Operations</p>
        </div>
        <ul>
          {roles.map((role) => (
            <li key={role.name}>
              <strong>{role.name}</strong>
              <span>{role.responsibility}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
