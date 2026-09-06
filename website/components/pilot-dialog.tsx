"use client";

import { X } from "@phosphor-icons/react";
import { useRouter } from "next/router";
import {
  type KeyboardEvent as ReactKeyboardEvent,
  type ReactNode,
  type SyntheticEvent,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";

import { PilotForm } from "@/components/pilot-form";

export interface PilotDialogContextValue {
  isOpen: boolean;
  openPilotDialog: (trigger: HTMLElement) => boolean;
  closePilotDialog: () => void;
}

export interface PilotDialogProviderProps {
  children: ReactNode;
}

const PilotDialogContext = createContext<
  PilotDialogContextValue | undefined
>(undefined);

const FOCUSABLE_SELECTOR = [
  "a[href]",
  "area[href]",
  "button:not(:disabled)",
  "input:not(:disabled):not([type=\"hidden\"])",
  "select:not(:disabled)",
  "textarea:not(:disabled)",
  "details > summary",
  "[contenteditable=\"true\"]",
  "[tabindex]:not([tabindex=\"-1\"])",
].join(",");

function getVisibleFocusableElements(
  dialog: HTMLDialogElement,
): HTMLElement[] {
  return Array.from(dialog.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)).filter(
    (element) => {
      if (
        element.hidden ||
        element.getAttribute("aria-hidden") === "true" ||
        element.getAttribute("aria-disabled") === "true" ||
        element.matches(":disabled")
      ) {
        return false;
      }

      const styles = window.getComputedStyle(element);

      return (
        styles.display !== "none" &&
        styles.visibility !== "hidden" &&
        styles.visibility !== "collapse" &&
        styles.opacity !== "0" &&
        element.getClientRects().length > 0
      );
    },
  );
}

export function usePilotDialog(): PilotDialogContextValue {
  const context = useContext(PilotDialogContext);

  if (!context) {
    throw new Error(
      "usePilotDialog must be used within a PilotDialogProvider.",
    );
  }

  return context;
}

export function PilotDialogProvider({
  children,
}: PilotDialogProviderProps): ReactNode {
  const router = useRouter();
  const dialogRef = useRef<HTMLDialogElement | null>(null);
  const triggerRef = useRef<HTMLElement | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  const handleDialogClose = useCallback(() => {
    setIsOpen(false);

    const trigger = triggerRef.current;
    triggerRef.current = null;

    if (trigger?.isConnected) {
      trigger.focus({ preventScroll: true });
    }
  }, []);

  const closePilotDialog = useCallback(() => {
    const dialog = dialogRef.current;

    if (dialog?.open) {
      dialog.close();
    }

    handleDialogClose();
  }, [handleDialogClose]);

  const openPilotDialog = useCallback((trigger: HTMLElement): boolean => {
    const dialog = dialogRef.current;

    if (!dialog) return false;

    if (dialog.open) {
      dialog.querySelector<HTMLElement>(".pilot-dialog-close")?.focus();
      return true;
    }

    if (typeof dialog.showModal !== "function") return false;

    triggerRef.current = trigger;

    try {
      dialog.showModal();
    } catch {
      triggerRef.current = null;
      return false;
    }

    setIsOpen(true);
    return true;
  }, []);

  useEffect(() => {
    const handleRouteChange = () => {
      if (dialogRef.current?.open) {
        closePilotDialog();
      }
    };

    router.events.on("routeChangeStart", handleRouteChange);

    return () => {
      router.events.off("routeChangeStart", handleRouteChange);
    };
  }, [closePilotDialog, router.events]);

  useEffect(() => {
    if (!isOpen) return undefined;

    const bodyOverflow = document.body.style.overflow;
    const documentOverflow = document.documentElement.style.overflow;
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = bodyOverflow;
      document.documentElement.style.overflow = documentOverflow;
    };
  }, [isOpen]);

  const handleDialogCancel = useCallback(
    (event: SyntheticEvent<HTMLDialogElement>) => {
      event.preventDefault();
      closePilotDialog();
    },
    [closePilotDialog],
  );

  const handleDialogKeyDown = useCallback(
    (event: ReactKeyboardEvent<HTMLDialogElement>) => {
      if (event.key !== "Tab") return;

      const focusableElements = getVisibleFocusableElements(
        event.currentTarget,
      );

      if (focusableElements.length === 0) {
        event.preventDefault();
        return;
      }

      const activeElement = document.activeElement;
      const activeIndex =
        activeElement instanceof HTMLElement
          ? focusableElements.indexOf(activeElement)
          : -1;

      if (event.shiftKey) {
        if (activeIndex <= 0) {
          event.preventDefault();
          focusableElements.at(-1)?.focus({ preventScroll: true });
        }
        return;
      }

      if (activeIndex === -1 || activeIndex === focusableElements.length - 1) {
        event.preventDefault();
        focusableElements[0]?.focus({ preventScroll: true });
      }
    },
    [],
  );

  const contextValue: PilotDialogContextValue = {
    isOpen,
    openPilotDialog,
    closePilotDialog,
  };

  return (
    <PilotDialogContext.Provider value={contextValue}>
      {children}
      <dialog
        ref={dialogRef}
        className="pilot-dialog"
        aria-labelledby="pilot-dialog-heading"
        aria-describedby="pilot-dialog-description"
        onCancel={handleDialogCancel}
        onClose={handleDialogClose}
        onKeyDown={handleDialogKeyDown}
      >
        <div className="pilot-dialog-panel">
          <button
            className="pilot-dialog-close"
            type="button"
            aria-label="Close pilot request"
            onClick={closePilotDialog}
          >
            <X aria-hidden="true" size={20} />
            <span className="visually-hidden">Close</span>
          </button>

          <p className="eyebrow eyebrow-blue">Case-specific conversation</p>
          <h2 className="pilot-dialog-heading" id="pilot-dialog-heading">
            Request a pilot
          </h2>
          <p id="pilot-dialog-description" className="pilot-dialog-description">
            Pilot intake is currently unavailable for this release. If it
            reopens, the conversation will cover scope, ownership, and
            evidence context for a case-specific pilot. No invoice upload
            happens here.
          </p>
          <PilotForm idPrefix="pilot-dialog" />
        </div>
      </dialog>
    </PilotDialogContext.Provider>
  );
}
