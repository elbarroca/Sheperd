"use client";

import { useState, type FormEvent, type ReactElement } from "react";

type ContactFormProps = {
  formName: "contact-home" | "contact-page";
};

type SubmissionState = "idle" | "sending" | "success" | "error" | "preview";

const inquiryTypes = ["Investor", "Partner", "Importer", "Other"] as const;
const deliveryEnabled = process.env.NEXT_PUBLIC_CONTACT_DELIVERY_ENABLED === "true";

export function ContactForm({ formName }: ContactFormProps): ReactElement {
  const [submissionState, setSubmissionState] = useState<SubmissionState>("idle");
  const isContactPage = formName === "contact-page";

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!deliveryEnabled) {
      setSubmissionState("preview");
      return;
    }

    const form = event.currentTarget;
    const formData = new FormData(form);
    const encodedData = new URLSearchParams();
    for (const [name, value] of formData.entries()) {
      if (typeof value === "string") encodedData.append(name, value);
    }

    setSubmissionState("sending");
    try {
      const response = await fetch("/__forms.html", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: encodedData.toString(),
      });
      if (!response.ok) throw new Error("The contact form request failed.");
      form.reset();
      setSubmissionState("success");
    } catch {
      setSubmissionState("error");
    }
  }

  const fieldPrefix = formName;

  return (
    <section className="contact-section" id="contact" aria-labelledby={`${fieldPrefix}-title`}>
      <div className="recovery-container contact-content">
        <div className="contact-intro">
          <p className="section-label">Your next step</p>
          {isContactPage ? (
            <h1 id={`${fieldPrefix}-title`}>Contact SheperD.</h1>
          ) : (
            <h2 id={`${fieldPrefix}-title`}>Let’s talk about your shipping history.</h2>
          )}
          <p>
            Tell us what you would like to discuss. We’ll follow up by email.
          </p>
          <p className="contact-email">
            Prefer email? <a href="mailto:michaelk@sheperd.io">michaelk@sheperd.io</a>
          </p>
        </div>

        <div className="contact-card">
          <form
            name={formName}
            method="POST"
            action="/__forms.html"
            data-netlify="true"
            netlify-honeypot="bot-field"
            onSubmit={handleSubmit}
          >
            <input type="hidden" name="form-name" value={formName} />
            <div className="contact-honeypot" aria-hidden="true">
              <label htmlFor={`${fieldPrefix}-bot-field`}>
                Leave this field empty
                <input id={`${fieldPrefix}-bot-field`} name="bot-field" tabIndex={-1} autoComplete="off" />
              </label>
            </div>
            <div className="contact-fields">
              <div className="contact-field">
                <label htmlFor={`${fieldPrefix}-name`}>Name</label>
                <input id={`${fieldPrefix}-name`} name="name" type="text" autoComplete="name" required />
              </div>
              <div className="contact-field">
                <label htmlFor={`${fieldPrefix}-email`}>Email</label>
                <input id={`${fieldPrefix}-email`} name="email" type="email" autoComplete="email" required />
              </div>
              <div className="contact-field">
                <label htmlFor={`${fieldPrefix}-company`}>Company</label>
                <input id={`${fieldPrefix}-company`} name="company" type="text" autoComplete="organization" required />
              </div>
              <div className="contact-field">
                <label htmlFor={`${fieldPrefix}-inquiryType`}>Inquiry type</label>
                <select id={`${fieldPrefix}-inquiryType`} name="inquiryType" defaultValue="" required>
                  <option value="" disabled>Select an inquiry type</option>
                  {inquiryTypes.map((inquiryType) => (
                    <option key={inquiryType} value={inquiryType}>{inquiryType}</option>
                  ))}
                </select>
              </div>
              <div className="contact-field contact-message-field">
                <label htmlFor={`${fieldPrefix}-message`}>Message</label>
                <textarea id={`${fieldPrefix}-message`} name="message" rows={5} required />
              </div>
            </div>
            <button className="recovery-action contact-submit" type="submit" disabled={submissionState === "sending"}>
              {submissionState === "sending" ? "Sending…" : "Send inquiry"}
            </button>
            {submissionState === "success" && (
              <p className="contact-feedback" role="status">
                Thank you. Your inquiry was sent. We’ll follow up by email.
              </p>
            )}
            {submissionState === "error" && (
              <p className="contact-feedback contact-feedback-error" role="alert">
                We could not send your inquiry. Please try again or email{" "}
                <a href="mailto:michaelk@sheperd.io">michaelk@sheperd.io</a>.
              </p>
            )}
            {submissionState === "preview" && (
              <p className="contact-feedback" role="status">
                Preview mode: your inquiry was not sent. Email{" "}
                <a href="mailto:michaelk@sheperd.io">michaelk@sheperd.io</a> instead.
              </p>
            )}
          </form>
        </div>
      </div>
    </section>
  );
}
