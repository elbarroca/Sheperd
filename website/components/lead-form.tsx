import { CheckCircle, WarningCircle } from "@phosphor-icons/react";
import { AnimatePresence, m } from "motion/react";
import { type FormEvent, useState } from "react";

import { volumeOptions } from "@/lib/content";

type SubmitState = "idle" | "submitting" | "success" | "error";

const deliveryEnabled =
  process.env.NEXT_PUBLIC_AUDIT_DELIVERY_ENABLED === "true";

export function LeadForm() {
  const [submitState, setSubmitState] = useState<SubmitState>("idle");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;

    if (!deliveryEnabled) {
      form.reset();
      setSubmitState("success");
      return;
    }

    setSubmitState("submitting");
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    try {
      const response = await fetch("/api/audit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-SheperD-Form": "audit-request",
        },
        body: JSON.stringify({
          ...payload,
          submissionId: window.crypto.randomUUID(),
        }),
      });

      if (!response.ok) {
        setSubmitState("error");
        return;
      }

      form.reset();
      setSubmitState("success");
    } catch {
      setSubmitState("error");
    }
  }

  const isSubmitting = submitState === "submitting";

  return (
    <form
      id="audit-form"
      className="audit-form"
      action="#audit-form"
      onSubmit={handleSubmit}
      aria-busy={isSubmitting}
    >
      <div className="form-grid">
        <label>
          <span>Full name</span>
          <input
            id="full-name"
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
            id="work-email"
            name="workEmail"
            type="email"
            autoComplete="email"
            placeholder="jane@company.com"
            maxLength={254}
            required
          />
        </label>
        <label>
          <span>Phone</span>
          <input
            id="phone"
            name="phone"
            type="tel"
            autoComplete="tel"
            placeholder="(555) 000-0000"
            maxLength={40}
            required
          />
        </label>
        <label>
          <span>Company</span>
          <input
            id="company"
            name="company"
            type="text"
            autoComplete="organization"
            placeholder="Company Inc."
            maxLength={120}
            required
          />
        </label>
        <label>
          <span>City</span>
          <input
            id="city"
            name="city"
            type="text"
            autoComplete="address-level2"
            placeholder="Los Angeles"
            maxLength={80}
            required
          />
        </label>
        <label>
          <span>State</span>
          <input
            id="state"
            name="state"
            type="text"
            autoComplete="address-level1"
            placeholder="CA"
            maxLength={80}
            required
          />
        </label>
        <label className="form-wide">
          <span>Estimated annual import volume</span>
          <select
            id="annual-volume"
            name="annualVolume"
            defaultValue={volumeOptions[0]}
            required
          >
            {volumeOptions.map((option) => (
              <option value={option} key={option}>
                {option}
              </option>
            ))}
          </select>
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
          : submitState === "success"
            ? deliveryEnabled
              ? "Request sent"
              : "Preview complete"
            : "Submit"}
      </button>

      <p className="form-privacy">
        {deliveryEnabled
          ? "Your details will be sent securely to SheperD for this audit request."
          : "Local Preview only. Nothing is transmitted or stored."}
      </p>

      <AnimatePresence initial={false} mode="wait">
        {submitState === "success" ? (
          <m.p
            className="form-success"
            role="status"
            key="success"
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
          >
            <CheckCircle aria-hidden="true" size={20} weight="fill" />
            {deliveryEnabled
              ? "Your audit request was sent to SheperD."
              : "Interaction verified. No details were sent."}
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
            We couldn’t send this request. Please try again or email
            info@sheperd.io.
          </m.p>
        ) : null}
      </AnimatePresence>
    </form>
  );
}
