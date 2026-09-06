import { RecoveryCorridor } from "@/components/recovery-corridor";
import { SeoHead } from "@/components/seo-head";

export default function HomePage() {
  return (
    <>
      <SeoHead
        title="SheperD | Detention & Demurrage Invoice Review"
        description="SheperD helps importer finance and logistics teams connect detention and demurrage charges to shipment records and governing terms for case-specific review."
        path="/"
      />
      <RecoveryCorridor />
    </>
  );
}
