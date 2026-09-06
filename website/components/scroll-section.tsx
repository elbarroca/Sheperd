"use client";

import { scroll } from "motion";
import { animate } from "motion/mini";
import { type ReactElement, type ReactNode, useEffect, useRef } from "react";

const REDUCED_MOTION_QUERY = "(prefers-reduced-motion: reduce)";
const SECTION_OFFSETS = ["start end", "start 75%", "end 25%", "end start"] as const;
const MOTION_TARGETS = {
  intro: ".intro-layout > h2, .intro-layout > p",
  process: ".section-heading, .process-list",
  evidence: ".evidence-list",
  story: ".story-band-copy, .story-band-image",
  pilot: ".pilot-scope-copy, .pilot-scope-list",
  trust: ".trust-layout",
  closing: ".closing-copy",
} as const;

type SectionMotion = keyof typeof MOTION_TARGETS;

interface ScrollBinding {
  animation: ReturnType<typeof animate>;
  release: () => void;
}

interface ScrollSectionProps {
  children: ReactNode;
  className: string;
  labelledBy: string;
  variant: SectionMotion;
  id?: string;
}

export function ScrollSection({
  children,
  className,
  labelledBy,
  variant,
  id,
}: ScrollSectionProps): ReactElement {
  const sectionRef = useRef<HTMLElement>(null);
  const surfaceRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const section = sectionRef.current;
    const surface = surfaceRef.current;
    if (!section || !surface || typeof IntersectionObserver === "undefined") return;

    const preference = window.matchMedia(REDUCED_MOTION_QUERY);
    let nearViewport = false;
    let bindings: ScrollBinding[] = [];
    let focusFrame = 0;
    const targets = Array.from(section.querySelectorAll<HTMLElement>(MOTION_TARGETS[variant]));
    targets.forEach((target) => { target.dataset.sectionMotionTarget = ""; });

    const stop = (): void => {
      bindings.forEach(({ animation, release }) => { release(); animation.stop(); });
      bindings = [];
      targets.forEach((target) => {
        target.style.removeProperty("opacity");
        target.style.removeProperty("transform");
      });
      section.dataset.sectionMotionState = "static";
    };

    const sync = (): void => {
      stop();
      if (
        !nearViewport || preference.matches ||
        document.visibilityState !== "visible" ||
        section.contains(document.activeElement)
      ) return;

      bindings = targets.map((target) => {
        const styles = getComputedStyle(target);
        const entry = styles.getPropertyValue("--section-entry").trim();
        const exit = styles.getPropertyValue("--section-exit").trim();
        const entryOpacity = Number(styles.getPropertyValue("--section-entry-opacity"));
        const exitOpacity = Number(styles.getPropertyValue("--section-exit-opacity"));
        const animation = animate(target, {
          opacity: [entryOpacity, 1, 1, exitOpacity],
          transform: [entry, "none", "none", exit],
        }, {
          autoplay: false,
          duration: 1,
          ease: "linear",
          times: [0, 1 / 3, 2 / 3, 1],
        });
        return {
          animation,
          release: scroll(animation, { target: section, offset: [...SECTION_OFFSETS] }),
        };
      });
      section.dataset.sectionMotionState = "active";
    };

    const observer = new IntersectionObserver(([entry]) => {
      nearViewport = Boolean(entry?.isIntersecting);
      sync();
    }, { rootMargin: "15% 0px", threshold: 0 });

    const onFocusIn = (event: FocusEvent): void => {
      const pointerFocus = event.target instanceof HTMLElement &&
        !event.target.matches(":focus-visible");
      const transforms = targets.map((target) => getComputedStyle(target).transform);
      stop();
      // Keep a pointer target in place between pointerdown and click.
      if (pointerFocus) targets.forEach((target, index) => {
        target.style.transform = transforms[index] ?? "none";
      });
    };

    const onFocusOut = (): void => {
      cancelAnimationFrame(focusFrame);
      focusFrame = requestAnimationFrame(sync);
    };

    observer.observe(section);
    preference.addEventListener("change", sync);
    document.addEventListener("visibilitychange", sync);
    section.addEventListener("focusin", onFocusIn);
    section.addEventListener("focusout", onFocusOut);

    return () => {
      observer.disconnect();
      preference.removeEventListener("change", sync);
      document.removeEventListener("visibilitychange", sync);
      section.removeEventListener("focusin", onFocusIn);
      section.removeEventListener("focusout", onFocusOut);
      cancelAnimationFrame(focusFrame);
      stop();
      targets.forEach((target) => { delete target.dataset.sectionMotionTarget; });
      delete section.dataset.sectionMotionState;
    };
  }, [variant]);

  return (
    <section ref={sectionRef} id={id} className={`scroll-section ${className}`} aria-labelledby={labelledBy} data-section-motion={variant}>
      <div ref={surfaceRef} className="section-motion-surface">{children}</div>
    </section>
  );
}
