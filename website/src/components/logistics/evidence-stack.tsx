import { EvidenceDisclosure } from "@/components/motion/evidence-disclosure";
import { siteCopy } from "@/content/site";

export function EvidenceStack(): React.JSX.Element {
  return (
    <section
      className="section evidence-section"
      id="review-requirements"
      aria-labelledby="requirements-heading"
    >
      <div className="evidence-heading">
        <h2 id="requirements-heading">{siteCopy.requirements.heading}</h2>
        <p>{siteCopy.requirements.body}</p>
      </div>
      <EvidenceDisclosure items={siteCopy.requirements.items} />
    </section>
  );
}
