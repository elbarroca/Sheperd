"use client";

import { CheckCircle, WarningCircle } from "@phosphor-icons/react";
import {
  type FormEvent,
  useState,
  useSyncExternalStore,
} from "react";

import { roleOptions, volumeOptions } from "@/lib/content";

type SubmitState = "idle" | "submitting" | "sent" | "error";

export interface PilotFormProps {
  idPrefix?: string;
}

const deliveryEnabled =
  process.env.NEXT_PUBLIC_PILOT_DELIVERY_ENABLED === "true";
const GENERIC_ERROR_MESSAGE =
  "We couldn’t send this request. Please try again later.";

function readApiMessage(value: unknown): string | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return null;
  }

  const message = (value as { message?: unknown }).message;
  return typeof message === "string" && message.length > 0 ? message : null;
}

function subscribeToHydration(): () => void {
  return () => undefined;
}

function getClientHydrationSnapshot(): boolean {
  return true;
}

function getServerHydrationSnapshot(): boolean {
  return false;
}

export function PilotForm({ idPrefix = "pilot" }: PilotFormProps) {
  const isHydrated = useSyncExternalStore(
    subscribeToHydration,
    getClientHydrationSnapshot,
    getServerHydrationSnapshot,
  );
  const [submitState, setSubmitState] = useState<SubmitState>("idle");
  const [errorMessage, setErrorMessage] = useState(GENERIC_ERROR_MESSAGE);
  const prefix = idPrefix.trim() || "pilot";
  const formId = `${prefix}-form`;
  const availabilityId = `${prefix}-availability`;
  const isAvailable = isHydrated && deliveryEnabled;
  const isSubmitting = submitState === "submitting";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!isAvailable) return;

    const form = event.currentTarget;
    setSubmitState("submitting");
    setErrorMessage(GENERIC_ERROR_MESSAGE);

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
        setErrorMessage(readApiMessage(body) ?? GENERIC_ERROR_MESSAGE);
        setSubmitState("error");
        return;
      }

      form.reset();
      setSubmitState("sent");
    } catch {
      setSubmitState("error");
    }
  }

  const fieldId = (name: string) => `${prefix}-${name}`;

  return (
    <form
      id={formId}
      className="pilot-form"
      method="post"
      action="/api/pilot"
      aria-describedby={!isAvailable ? availabilityId : undefined}
      aria-busy={isSubmitting}
      tabIndex={-1}
      onSubmit={handleSubmit}
    >
      {!isAvailable ? (
        <p
          id={availabilityId}
          className="form-notice pilot-form-availability"
          role="status"
        >
          <WarningCircle aria-hidden="true" size={20} weight="fill" />
          Pilot intake is currently unavailable. No details are collected,
          stored, or sent.
        </p>
      ) : null}

      <fieldset
        className="pilot-form-fields"
        disabled={!isAvailable || isSubmitting}
      >
        <legend className="visually-hidden">Pilot request details</legend>

        <div className="pilot-form-grid">
          <label htmlFor={fieldId("full-name")}>
            <span>Full name</span>
            <input
              id={fieldId("full-name")}
              name="fullName"
              type="text"
              autoComplete="name"
              placeholder="Jane Smith"
              maxLength={100}
              required
            />
          </label>

          <label htmlFor={fieldId("work-email")}>
            <span>Work email</span>
            <input
              id={fieldId("work-email")}
              name="workEmail"
              type="email"
              autoComplete="email"
              placeholder="jane@company.com"
              maxLength={254}
              required
            />
          </label>

          <label htmlFor={fieldId("company")}>
            <span>Company</span>
            <input
              id={fieldId("company")}
              name="company"
              type="text"
              autoComplete="organization"
              placeholder="Company Inc."
              maxLength={120}
              required
            />
          </label>

          <label htmlFor={fieldId("role")}>
            <span>Your role</span>
            <select id={fieldId("role")} name="role" defaultValue="" required>
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

          <label htmlFor={fieldId("annual-volume")}>
            <span>Annual import volume</span>
            <select
              id={fieldId("annual-volume")}
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

          <label className="pilot-form-wide" htmlFor={fieldId("review-context")}>
            <span>What prompted the review?</span>
            <textarea
              id={fieldId("review-context")}
              name="reviewContext"
              rows={4}
              maxLength={1000}
              placeholder="Tell us what your team is trying to understand."
              required
            />
          </label>

          <label className="pilot-consent" htmlFor={fieldId("consent")}>
            <input
              id={fieldId("consent")}
              name="consent"
              type="checkbox"
              value="yes"
              required
            />
            <span>
              I agree to be contacted about a SheperD pilot conversation.
            </span>
          </label>

          <label
            className="form-honeypot"
            aria-hidden="true"
            htmlFor={fieldId("website")}
          >
            <span>Website</span>
            <input
              id={fieldId("website")}
              name="website"
              type="text"
              autoComplete="off"
              tabIndex={-1}
            />
          </label>
        </div>
      </fieldset>

      <button
        className="form-submit"
        type="submit"
        disabled={!isAvailable || isSubmitting}
      >
        {isSubmitting
          ? "Sending…"
          : submitState === "sent"
            ? "Request sent"
            : "Request a pilot"}
      </button>

      <p className="form-privacy">
        {isAvailable
          ? "Your details go only to the approved SheperD pilot owner."
          : "Pilot delivery is disabled for this release."}
      </p>

      {submitState === "sent" ? (
        <p
          className="form-success"
          role="status"
        >
          <CheckCircle aria-hidden="true" size={20} weight="fill" />
          Pilot request sent. SheperD will follow up using the approved
          response path.
        </p>
      ) : null}

      {submitState === "error" ? (
        <p
          className="form-error"
          role="alert"
        >
          <WarningCircle aria-hidden="true" size={20} weight="fill" />
          {errorMessage}
        </p>
      ) : null}
    </form>
  );
}
