"use client";

import {
  type AnchorHTMLAttributes,
  type MouseEvent,
} from "react";

import { usePilotDialog } from "@/components/pilot-dialog";

export type PilotLinkProps = Omit<
  AnchorHTMLAttributes<HTMLAnchorElement>,
  "href"
>;

function isPlainLeftClick(event: MouseEvent<HTMLAnchorElement>): boolean {
  return (
    event.button === 0 &&
    !event.altKey &&
    !event.ctrlKey &&
    !event.metaKey &&
    !event.shiftKey
  );
}

function hasNewTabTarget(anchor: HTMLAnchorElement): boolean {
  return Boolean(anchor.target && anchor.target !== "_self");
}

function focusStandalonePilotForm(): boolean {
  const form = document.getElementById("pilot-form");

  if (!form) return false;

  form.scrollIntoView({
    behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ? "auto"
      : "smooth",
    block: "start",
  });

  const focusTarget =
    form.querySelector<HTMLElement>(
      "input:not(:disabled), select:not(:disabled), textarea:not(:disabled), button:not(:disabled)",
    ) ?? form;

  focusTarget.focus({ preventScroll: true });
  return true;
}

export function PilotLink({ onClick, ...props }: PilotLinkProps) {
  const { openPilotDialog } = usePilotDialog();

  function handleClick(event: MouseEvent<HTMLAnchorElement>): void {
    onClick?.(event);

    if (
      event.defaultPrevented ||
      !isPlainLeftClick(event) ||
      hasNewTabTarget(event.currentTarget)
    ) {
      return;
    }

    if (window.location.pathname === "/pilot") {
      if (focusStandalonePilotForm()) {
        event.preventDefault();
      }
      return;
    }

    if (openPilotDialog(event.currentTarget)) {
      event.preventDefault();
    }
  }

  return <a {...props} href="/pilot" onClick={handleClick} />;
}
