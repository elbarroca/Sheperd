import { describe, expect, it } from "vitest";

import {
  evidenceLayers,
  faqItems,
  navigationItems,
  pilotScope,
  processSteps,
  volumeOptions,
} from "../../lib/content";

describe("recovery-led landing page content", () => {
  it("leads with the pilot conversion path", () => {
    expect(navigationItems).toEqual([
      { label: "How it works", href: "#process" },
      { label: "What we review", href: "#evidence" },
      { label: "Pilot scope", href: "#pilot-scope" },
      { label: "Trust", href: "#trust" },
    ]);
  });

  it("keeps the process explicit without promising recovery", () => {
    expect(processSteps.map(({ title }) => title)).toEqual([
      "Bring the invoice and operating record",
      "Build the case from the evidence",
      "Support the dispute and track the outcome",
    ]);
    expect(processSteps.at(-1)?.description).toContain("credit or refund");
  });

  it("names the three evidence layers", () => {
    expect(evidenceLayers.map(({ title }) => title)).toEqual([
      "Billing record",
      "Operational timeline",
      "Governing terms",
    ]);
  });

  it("defines a bounded pilot scope", () => {
    expect(pilotScope.map(({ title }) => title)).toEqual([
      "A focused record review",
      "A clear evidence map",
      "A next-step conversation",
    ]);
  });

  it("answers the trust questions without fabricating proof", () => {
    const requiredQuestions = [
      "What happens after I request a pilot?",
      "Do I need to upload invoices now?",
      "Does SheperD guarantee a refund?",
      "What if the review does not support a recovery path?",
      "What does the pilot cost?",
      "How long does a review take?",
      "Is the outcome cash or a carrier credit?",
      "What does detention and demurrage mean?",
      "Is SheperD software?",
      "Can SheperD help with carrier payments?",
    ];
    expect(faqItems.map(({ question }) => question)).toEqual(
      expect.arrayContaining(requiredQuestions),
    );
  });

  it("keeps the approved volume ranges and official contact", () => {
    expect(volumeOptions).toHaveLength(4);
  });
});
