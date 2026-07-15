import { EditorialImage } from "@/components/ui/editorial-image";
import { siteCopy } from "@/content/site";

export function RecoveryRoute(): React.JSX.Element {
  return (
    <section className="section route-section" id="process" aria-labelledby="route-heading">
      <div className="route-intro">
        <h2 id="route-heading">{siteCopy.process.heading}</h2>
        <p>{siteCopy.process.body}</p>
      </div>
      <EditorialImage
        alt="Illustrative unmarked terminal lanes branching between stacks of containers."
        className="route-picture"
        height={941}
        name="sheperd-routes-v2"
        sizes="(max-width: 767px) 100vw, 88vw"
        width={1672}
        widths={[640, 960, 1440]}
      />
      <ol
        aria-label="Conditional review path; scroll horizontally to view all six steps"
        className="route-list"
        tabIndex={0}
      >
        {siteCopy.process.steps.map((step, index) => (
          <li key={step.title}>
            <span className="route-index" aria-hidden="true">
              {String(index + 1).padStart(2, "0")}
            </span>
            <div>
              <h3>{step.title}</h3>
              <p>{step.prompt}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
