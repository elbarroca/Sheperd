import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

import { productionBlockers } from "../src/content/blockers";
import { claims, productionRequiredClaimIds } from "../src/content/claims";
import {
  channelForTarget,
  getPublicationTarget,
  isClaimPublishable,
} from "../src/content/publication";

const SOURCE_FILES = [
  "src/content/site.ts",
  "src/content/legal.ts",
] as const;

const PROHIBITED_PUBLIC_PATTERNS = [
  /\bguaranteed?\b/i,
  /\bsuccess rate\b/i,
  /\bcustomer logo\b/i,
  /\btestimonial\b/i,
  /\bfree audit\b/i,
  /\bno fee\b/i,
  /\bwe recover\b/i,
  /\bautomatically files?\b/i,
] as const;

async function readSource(path: string): Promise<string> {
  return readFile(resolve(process.cwd(), path), "utf8");
}

async function validatePreview(): Promise<void> {
  const renderedSources = await Promise.all(
    SOURCE_FILES.map(async (path) => ({ path, source: await readSource(path) })),
  );
  const renderedText = renderedSources.map(({ source }) => source).join("\n");
  const leakedClaims = Object.values(claims).flatMap((claim) =>
    renderedSources
      .filter(({ source }) => source.includes(claim.exactText))
      .map(({ path }) => `${claim.claimId}@${path}`),
  );

  if (leakedClaims.length > 0) {
    throw new Error(
      `Preview contains unapproved exact claim text: ${leakedClaims.join(", ")}`,
    );
  }

  const forbiddenPatterns = [
    /<form\b/i,
    /type=["']file["']/i,
    /mailto:/i,
    /typeform/i,
    /google-analytics/i,
    /googletagmanager/i,
    /segment\.com/i,
  ];

  for (const pattern of forbiddenPatterns) {
    if (pattern.test(renderedText)) {
      throw new Error(`Preview content matches forbidden pattern: ${pattern}`);
    }
  }

  for (const pattern of PROHIBITED_PUBLIC_PATTERNS) {
    if (pattern.test(renderedText)) {
      throw new Error(`Preview copy matches prohibited claim pattern: ${pattern}`);
    }
  }
}

function validateProduction(): void {
  const unresolved = productionBlockers.filter((blocker) => !blocker.resolved);
  const channel = channelForTarget("production");
  const unpublishedClaims = productionRequiredClaimIds.filter(
    (claimId) => !isClaimPublishable(claims[claimId], channel),
  );

  if (unresolved.length > 0 || unpublishedClaims.length > 0) {
    const blockerIds = unresolved.map((blocker) => blocker.id).join(", ");
    throw new Error(
      `Production publication blocked. Unresolved: ${blockerIds}. Unapproved claims: ${unpublishedClaims.join(", ")}.`,
    );
  }
}

async function main(): Promise<void> {
  if (getPublicationTarget() === "production") {
    validateProduction();
    return;
  }

  await validatePreview();
  process.stdout.write("Preview content gate passed.\n");
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  process.stderr.write(`${message}\n`);
  process.exitCode = 1;
});
