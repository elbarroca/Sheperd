import { RelationLine } from "@/components/motion/relation-line";
import { EditorialImage } from "@/components/ui/editorial-image";
import { siteCopy } from "@/content/site";

export function InvoiceManifest(): React.JSX.Element {
  return (
    <section className="section manifest-section" aria-labelledby="manifest-heading">
      <div className="manifest-intro">
        <div>
          <h2 id="manifest-heading">{siteCopy.manifest.heading}</h2>
          <p>{siteCopy.manifest.body}</p>
        </div>
        <span aria-hidden="true">01 / 03</span>
      </div>
      <div className="manifest-composition">
        <EditorialImage
          alt="Three groups of blank paper records arranged around a physical timeline strip."
          className="manifest-picture"
          height={1086}
          name="sheperd-records-v2"
          sizes="(max-width: 767px) 100vw, 45vw"
          width={1448}
          widths={[640, 960, 1280]}
        />
        <dl className="manifest-list">
          {siteCopy.manifest.items.map((item, index) => (
            <div className="manifest-row" key={item.title}>
              <dt>{item.title}</dt>
              <dd>{item.prompt}</dd>
              <RelationLine order={index} />
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}
