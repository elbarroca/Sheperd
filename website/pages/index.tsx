import { RecoveryCorridor } from "@/components/recovery-corridor";
import { SeoHead } from "@/components/seo-head";
import { liveSource } from "@/lib/content";

export default function HomePage() {
  return (
    <>
      <SeoHead
        title="SheperD | D&D Services for U.S. Importers"
        description={liveSource.description}
        path="/"
      />
      <RecoveryCorridor />
    </>
  );
}
