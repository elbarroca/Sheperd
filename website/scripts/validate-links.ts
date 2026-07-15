import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

import { siteCopy } from "../src/content/site";

const PAGE_COMPONENTS = [
  "src/components/logistics/evidence-stack.tsx",
  "src/components/logistics/recovery-route.tsx",
  "src/components/logistics/port-grid.tsx",
  "src/components/sections/limits-section.tsx",
  "src/components/ui/site-header.tsx",
  "src/components/ui/site-footer.tsx",
] as const;

async function main(): Promise<void> {
  const pageSources = await Promise.all(
    PAGE_COMPONENTS.map((path) => readFile(resolve(process.cwd(), path), "utf8")),
  );
  const source = pageSources.join("\n");
  const missingTargets = siteCopy.navigation
    .map((item) => item.href)
    .filter((href) => !source.includes(`id="${href.slice(1)}"`));

  if (missingTargets.length > 0) {
    throw new Error(`Missing navigation targets: ${missingTargets.join(", ")}`);
  }

  if (!source.includes('id="review-requirements"')) {
    throw new Error("Preview CTA target is missing.");
  }

  const externalAnchorTags = source.match(/<a\b[^>]*target="_blank"[^>]*>/g) ?? [];
  const hasUnsafeExternalLink = externalAnchorTags.some(
    (tag) => !/rel="noopener noreferrer"/.test(tag),
  );
  if (hasUnsafeExternalLink) {
    throw new Error("External link is missing noopener and noreferrer.");
  }

  if (/href=["'](?:javascript:|data:)/i.test(source)) {
    throw new Error("Unsafe link scheme found in page source.");
  }

  process.stdout.write("Internal link gate passed.\n");
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  process.stderr.write(`${message}\n`);
  process.exitCode = 1;
});
