import { useEffect, type RefObject } from "react";
import { useRouter } from "next/router";

/** Progressive enhancement: the server-rendered page never starts hidden. */
export function useRecoveryMotion(root: RefObject<HTMLElement | null>): void {
  const { pathname } = useRouter();
  useEffect(() => {
    const element = root.current;
    if (!element || typeof IntersectionObserver === "undefined") return;

    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const targets = Array.from(element.querySelectorAll<HTMLElement>(
      "h1, h2, .hero-headline, .section-description, .hero-description, .responsibility-flow, .recovery-process li, .industry, .market-visual, .market-opportunity-node, .market-proof, .recovery-faq .section-label, .recovery-faq h3, .recovery-faq details",
    ));
    const sections = Array.from(element.querySelectorAll<HTMLElement>(":scope > section"));
    let observer: IntersectionObserver | undefined;

    const reset = (): void => {
      observer?.disconnect();
      targets.forEach((target) => {
        target.classList.remove("recovery-enter", "recovery-exit");
        target.style.removeProperty("--reveal-delay");
      });
    };
    const configure = (): void => {
      reset();
      if (preference.matches) return;
      observer = new IntersectionObserver((entries) => {
        let order = 0;
        entries.forEach((entry) => {
          const sectionTargets = targets.filter((target) => entry.target.contains(target));
          sectionTargets.forEach((target) => {
          if (target.contains(document.activeElement)) {
            target.classList.remove("recovery-enter", "recovery-exit");
          } else if (entry.isIntersecting && entry.boundingClientRect.top < 0 && entry.intersectionRatio < 0.15) {
            target.classList.remove("recovery-enter");
            target.classList.add("recovery-exit");
          } else if (entry.isIntersecting) {
            target.classList.remove("recovery-exit");
            target.style.setProperty("--reveal-delay", `${Math.min(order++, 3) * 90}ms`);
            target.classList.add("recovery-enter");
          } else if (!target.contains(document.activeElement)) {
            // Reset only outside the viewport, so scrolling never fades readable copy out.
            target.classList.remove("recovery-enter", "recovery-exit");
          }
          });
        });
      }, { threshold: [0, 0.15, 1] });
      sections.forEach((section) => observer?.observe(section));
    };
    configure();
    preference.addEventListener("change", configure);
    return () => {
      reset();
      preference.removeEventListener("change", configure);
    };
  }, [root, pathname]);
}
