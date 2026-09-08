"use client";

import { CheckCircle, WarningCircle } from "@phosphor-icons/react";
import { AnimatePresence, m } from "motion/react";
import { type FormEvent, useState } from "react";

import { roleOptions, volumeOptions } from "@/lib/content";

type SubmitState = "idle" | "submitting" | "sent" | "disabled" | "error";

const deliveryEnabled =
  process.env.NEXT_PUBLIC_PILOT_DELIVERY_ENABLED === "true";

function readApiMessage(value: unknown): string | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return null;
  }

  const message = (value as { message?: unknown }).message;
  return typeof message === "string" && message.length > 0 ? message : null;
}

export function PilotForm() {
  const [submitState, setSubmitState] = useState<SubmitState>("idle");
  const [errorMessage, setErrorMessage] = useState(
    "We couldn’t send this request. Please try again later.",
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;

    if (!deliveryEnabled) {
      setSubmitState("disabled");
      return;
    }

    setSubmitState("submitting");
    setErrorMessage("We couldn’t send this request. Please try again later.");

    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    try {
      const response = await fetch("/api/pilot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-SheperD-Form": "pilot-request",
        },
        body: JSON.stringify({
          ...payload,
          submissionId: window.crypto.randomUUID(),
        }),
      });
      const body: unknown = await response.json().catch(() => null);

      if (!response.ok) {
        setErrorMessage(readApiMessage(body) ?? errorMessage);
        setSubmitState("error");
        return;
      }

      form.reset();
      setSubmitState("sent");
    } catch {
      setSubmitState("error");
    }
  }

  const isSubmitting = submitState === "submitting";

  if (!deliveryEnabled) {
    return <div className="intake-unavailable" role="status">
      <WarningCircle size={28} aria-hidden="true" />
      <h2>Online enquiries are not open yet.</h2>
      <p>No details are collected, stored, or sent. Invoice handoff will be arranged separately when enquiries open.</p>
      <a className="quiet-link" href="/how-it-works">See how recovery works</a>
    </div>;
  }

  return (
    <form
      id="pilot-form"
      className="pilot-form"
      action="/pilot#pilot-form"
      onSubmit={handleSubmit}
      aria-busy={isSubmitting}
    >
      <div className="pilot-form-grid">
        <label>
          <span>Full name</span>
          <input
            id="pilot-full-name"
            name="fullName"
            type="text"
            autoComplete="name"
            placeholder="Jane Smith"
            maxLength={100}
            required
          />
        </label>

        <label>
          <span>Work email</span>
          <input
            id="pilot-work-email"
            name="workEmail"
            type="email"
            autoComplete="email"
            placeholder="jane@company.com"
            maxLength={254}
            required
          />
        </label>

        <label>
          <span>Company</span>
          <input
            id="pilot-company"
            name="company"
            type="text"
            autoComplete="organization"
            placeholder="Company Inc."
            maxLength={120}
            required
          />
        </label>

        <label>
          <span>Your role</span>
          <select id="pilot-role" name="role" defaultValue="" required>
            <option value="" disabled>
              Select a role
            </option>
            {roleOptions.map((role) => (
              <option value={role} key={role}>
                {role}
              </option>
            ))}
          </select>
        </label>

        <label>
          <span>Annual import volume</span>
          <select
            id="pilot-annual-volume"
            name="annualVolume"
            defaultValue=""
            required
          >
            <option value="" disabled>
              Select a range
            </option>
            {volumeOptions.map((option) => (
              <option value={option} key={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="pilot-form-wide">
          <span>What prompted the review?</span>
          <textarea
            id="pilot-review-context"
            name="reviewContext"
            rows={4}
            maxLength={1000}
            placeholder="Tell us what your team is trying to understand."
            required
          />
        </label>

        <label className="pilot-consent">
          <input name="consent" type="checkbox" value="yes" required />
          <span>
            I agree to be contacted about a SheperD recovery enquiry.
          </span>
        </label>

        <label className="form-honeypot" aria-hidden="true">
          <span>Website</span>
          <input
            name="website"
            type="text"
            autoComplete="off"
            tabIndex={-1}
          />
        </label>
      </div>

      <button className="form-submit" type="submit" disabled={isSubmitting}>
        {isSubmitting
          ? "Sending…"
          : submitState === "sent"
            ? "Request sent"
            : submitState === "disabled"
              ? "Preview intake disabled"
          : "Find Recoverable Value"}
      </button>

      <p className="form-privacy">
        {deliveryEnabled
          ? "Your details go only to the approved SheperD pilot owner."
          : "Preview only. Nothing is transmitted or stored."}
      </p>

      <AnimatePresence initial={false} mode="wait">
        {submitState === "sent" ? (
          <m.p
            className="form-success"
            role="status"
            key="sent"
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
          >
            <CheckCircle aria-hidden="true" size={20} weight="fill" />
            Enquiry sent. SheperD will follow up about your recovery enquiry.
          </m.p>
        ) : null}

        {submitState === "disabled" ? (
          <m.p
            className="form-notice"
            role="status"
            key="disabled"
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
          >
            <WarningCircle aria-hidden="true" size={20} weight="fill" />
            Pilot intake is disabled in this Preview. No details were sent.
          </m.p>
        ) : null}

        {submitState === "error" ? (
          <m.p
            className="form-error"
            role="alert"
            key="error"
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
          >
            <WarningCircle aria-hidden="true" size={20} weight="fill" />
            {errorMessage}
          </m.p>
        ) : null}
      </AnimatePresence>
    </form>
  );
}
