export const recoveryCta = "Find Recoverable Value";
export const recoveryPromise = "You send the invoices. We handle the recovery.";
export const aiRecoveryPositioning = "AI-assisted D&D recovery with human review.";
export const aiReviewSupport =
  "AI helps organize the complex recovery record; human reviewers decide what the evidence supports.";
export const aiProcessCue = "AI-assisted review. Human-led recovery follow-up.";
export const recoverySteps = [
  { title: "Send invoices", owner: "Your part", description: "Send your historical detention and demurrage invoices. That's your part of the recovery work.", kind: "invoice" },
  { title: "We review", owner: "SheperD", description: "We review the charges and handle the supporting-record work to identify potential recovery opportunities.", kind: "review" },
  { title: "We pursue recovery", owner: "SheperD", description: "We manage the recovery process and follow-up on your behalf.", kind: "recovery" },
  { title: "Refund or carrier credit", owner: "Your outcome", description: "When recovery succeeds, value returns as a refund or carrier credit. We track the outcome.", kind: "value" },
] as const;
export const industries = ["Furniture", "Consumer goods", "Food & beverage", "Electronics", "Manufacturing", "Retail", "Wholesale", "Industrial"] as const;
export const recoveryFaqs = [
  { question: "What does my team need to do?", answer: "Send your invoices. SheperD handles review, supporting-record work, recovery follow-up, and outcome tracking. Your team does not need to build or manage a recovery function." },
  { question: "Which invoices should we send?", answer: "Historical detention and demurrage invoices related to your imports. Demurrage concerns time at the terminal; detention concerns use of the container outside it. SheperD handles the review of the charges and their circumstances." },
  { question: "What does it cost?", answer: "There is no upfront cost. SheperD is paid when you recover monetary value. The revenue share is agreed before the engagement begins." },
  { question: "Will we receive cash or a carrier credit?", answer: "Successful recovery can result in a cash refund or a carrier credit. These are different outcomes, and SheperD tracks which is actually recovered." },
  { question: "How long does recovery take?", answer: "Timing depends on the charges and the recovery process. SheperD manages follow-up and keeps you informed; there is no fixed recovery timeline." },
  { question: "What if no value is recovered?", answer: "If you recover no monetary value, SheperD earns no recovery fee. A review does not guarantee that a charge will result in a refund or credit." },
] as const;
