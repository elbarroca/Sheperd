export const legalCopy = {
  privacy: {
    title: "Preview Data Notice",
    intro:
      "This is a design and engineering Preview. It is not an approved company privacy notice.",
    sections: [
      {
        heading: "Application behavior",
        body: "The application has no forms, uploads, accounts, analytics, advertising pixels, cookies, or contact capture.",
      },
      {
        heading: "Delivery data",
        body: "A hosting provider may process standard request data needed to deliver and protect the Preview. A production privacy notice and retention policy are not approved.",
      },
      {
        heading: "Do not submit records",
        body: "Do not send invoices, shipment records, contact details, credentials, or personal information through this Preview.",
      },
    ],
  },
  terms: {
    title: "Preview Use Notice",
    intro:
      "This page is a temporary Preview notice. It is not production terms, a commercial offer, or legal advice.",
    sections: [
      {
        heading: "Preview purpose",
        body: "Use this Preview only to review layout, content structure, motion, accessibility, and engineering behavior.",
      },
      {
        heading: "No case reliance",
        body: "The Preview does not assess a charge, select a dispute route, state an outcome, or establish a deadline.",
      },
      {
        heading: "Production gate",
        body: "Approved entity details, company wording, privacy, terms, contact, security, and commercial language are required before production publication.",
      },
    ],
  },
} as const;
