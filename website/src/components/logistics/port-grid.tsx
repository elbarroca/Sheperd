import { SealLink } from "@/components/motion/seal-link";
import { publicSources } from "@/content/sources";

export function PortGrid(): React.JSX.Element {
  const fmcGuidance = publicSources.find(
    (source) => source.sourceId === "SRC-008",
  );

  return (
    <section className="section sources-section" id="sources" aria-labelledby="sources-heading">
      <div className="sources-heading">
        <h2 id="sources-heading">Check the source text.</h2>
        <p>Official links are listed without interpretation or endorsement.</p>
      </div>
      <ul className="source-register">
        {publicSources.map((source, index) => (
          <li key={source.sourceId}>
            <span className="source-index" aria-hidden="true">
              {String(index + 1).padStart(2, "0")}
            </span>
            <div>
              <span className="source-issuer">{source.issuer}</span>
              <h3>{source.title}</h3>
            </div>
            <div className="source-action">
              <p>Checked {source.checkedDate}</p>
              <a href={source.href} rel="noopener noreferrer" target="_blank">
                Open source
              </a>
            </div>
          </li>
        ))}
      </ul>
      {fmcGuidance ? (
        <SealLink external href={fmcGuidance.href} className="source-cta">
          Open FMC guidance
        </SealLink>
      ) : null}
    </section>
  );
}
