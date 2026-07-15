import {
  ALLOWED_PUBLIC_STATES,
  claims,
  type ClaimId,
  type PublicationChannel,
  type PublicClaim,
} from "@/content/claims";

export type PublicationTarget = "preview" | "production";

export function getPublicationTarget(): PublicationTarget {
  const target =
    process.env.SITE_PUBLICATION_TARGET ?? process.env.VERCEL_ENV ?? "preview";

  return target === "production" ? "production" : "preview";
}

export function channelForTarget(
  target: PublicationTarget,
): PublicationChannel {
  return target === "production" ? "production-web" : "preview-web";
}

export function isClaimPublishable(
  claim: PublicClaim,
  channel: PublicationChannel,
  now = new Date(),
): boolean {
  const allowedState = ALLOWED_PUBLIC_STATES.includes(
    claim.evidenceStatus as (typeof ALLOWED_PUBLIC_STATES)[number],
  );
  const expiry = new Date(`${claim.expiresOn}T23:59:59.999Z`);

  return (
    allowedState &&
    claim.sourceIds.length > 0 &&
    claim.sourceUrls.length > 0 &&
    claim.approvedFor.includes(channel) &&
    Boolean(claim.approvedBy) &&
    Boolean(claim.approvalDate) &&
    !Number.isNaN(expiry.getTime()) &&
    expiry >= now
  );
}

export function resolveClaim(
  claimId: ClaimId,
  target = getPublicationTarget(),
): PublicClaim | null {
  const claim = claims[claimId];
  return isClaimPublishable(claim, channelForTarget(target)) ? claim : null;
}
