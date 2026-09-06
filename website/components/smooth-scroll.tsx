"use client";

import type Lenis from "lenis";
import { useEffect } from "react";

import { usePilotDialog } from "./pilot-dialog";

const SCROLL_KEYS = new Set(["ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End", " ", "Tab"]);

export function SmoothScroll(): null {
  const { isOpen } = usePilotDialog();

  useEffect(() => {
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const dialog = document.querySelector("dialog");
    let instance: Lenis | undefined;
    let frame = 0;
    let disposed = false;
    let loading = false;

    const tick = (time: number): void => {
      frame = 0;
      if (!instance || disposed) return;
      if (dialog?.open || document.visibilityState !== "visible") {
        instance.stop();
        return;
      }
      instance.raf(time);
      frame = requestAnimationFrame(tick);
    };

    const sync = (): void => {
      cancelAnimationFrame(frame);
      frame = 0;
      if (isOpen || preference.matches) {
        instance?.destroy();
        instance = undefined;
        return;
      }
      if (document.visibilityState !== "visible") {
        instance?.stop();
        return;
      }
      if (instance) {
        instance.start();
        frame = requestAnimationFrame(tick);
        return;
      }
      if (loading) return;
      loading = true;
      void import("lenis").then(({ default: LenisConstructor }) => {
        loading = false;
        if (disposed || isOpen || preference.matches || document.visibilityState !== "visible") return;
        instance = new LenisConstructor({
          autoRaf: false,
          smoothWheel: true,
          syncTouch: false,
          lerp: 0.085,
          anchors: false,
          stopInertiaOnNavigate: true,
          respectReducedMotion: true,
          prevent: (node) => node.closest("dialog[open]") !== null,
        });
        sync();
      }).catch((error: unknown) => {
        loading = false;
        console.warn("Smooth scrolling unavailable; native scrolling remains available.", error);
      });
    };

    const onAnchorClick = (event: MouseEvent): void => {
      if (!instance || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const anchor = event.target instanceof Element ? event.target.closest<HTMLAnchorElement>('a[href*="#"]') : null;
      if (!anchor || anchor.hasAttribute("download") || (anchor.target && anchor.target !== "_self")) return;
      const url = new URL(anchor.href);
      if (url.origin !== location.origin || url.pathname !== location.pathname || url.search !== location.search || !url.hash) return;
      let targetId: string;
      try {
        targetId = decodeURIComponent(url.hash.slice(1));
      } catch {
        return;
      }
      const target = document.getElementById(targetId);
      if (!target) return;
      event.preventDefault();
      const initiatingFocus = document.activeElement;
      instance.scrollTo(target, {
        immediate: anchor.classList.contains("skip-link"),
        onComplete: () => {
          if (document.activeElement !== initiatingFocus) return;
          // Update native history after arrival so it cannot compete with easing.
          if (location.hash !== url.hash) location.hash = url.hash;
          if (!target.hasAttribute("tabindex")) {
            target.tabIndex = -1;
            target.addEventListener("blur", () => target.removeAttribute("tabindex"), { once: true });
          }
          target.focus({ preventScroll: true });
        },
      });
    };

    const onKeyDown = (event: KeyboardEvent): void => {
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey || !SCROLL_KEYS.has(event.key)) return;
      const target = event.target;
      if (target instanceof HTMLElement && target.closest('input, textarea, select, [contenteditable="true"]')) return;
      if (instance?.isScrolling !== "smooth") return;
      // Cancel easing before the browser applies keyboard scroll or focus movement.
      instance.stop();
      instance.start();
    };

    preference.addEventListener("change", sync);
    document.addEventListener("visibilitychange", sync);
    document.addEventListener("click", onAnchorClick);
    document.addEventListener("keydown", onKeyDown);
    sync();
    return () => {
      disposed = true;
      preference.removeEventListener("change", sync);
      document.removeEventListener("visibilitychange", sync);
      document.removeEventListener("click", onAnchorClick);
      document.removeEventListener("keydown", onKeyDown);
      cancelAnimationFrame(frame);
      instance?.destroy();
    };
  }, [isOpen]);

  return null;
}
