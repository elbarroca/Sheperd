"use client";

import { animate } from "motion/mini";
import { Fragment, type ReactElement, type ReactNode, useEffect, useRef } from "react";

const REDUCED_MOTION_QUERY = "(prefers-reduced-motion: reduce)";
const REVEAL_THRESHOLD = 0.16;
const REVEAL_ROOT_MARGIN = "0px 0px -8% 0px";
const REVEAL_DURATION = 0.62;
const HEADING_OFFSET = "translateY(110%)";
const LIFT_OFFSET = "translateY(24px)";
const SLIDE_OFFSET = "translateX(28px)";

type ScrollRevealTag = "article" | "div" | "h2" | "h3" | "li" | "p";
export type ScrollRevealVariant = "fade" | "lift" | "mask" | "slide";
export type ScrollHeadingTreatment = "line" | "block" | "word" | "plain";

export interface ScrollRevealProps {
  children: ReactNode;
  as?: ScrollRevealTag;
  className?: string;
  delay?: number;
  id?: string;
  stagger?: number;
  targetSelector?: string;
  variant?: ScrollRevealVariant;
}

export interface ScrollHeadingProps {
  lines: readonly string[];
  className?: string;
  id?: string;
  treatment?: ScrollHeadingTreatment;
}

type AnimationControl = { stop: () => void };

interface RevealTransforms {
  from: string;
  to: string;
}

function joinClasses(...classes: Array<string | undefined>): string {
  return classes.filter((className): className is string => Boolean(className)).join(" ");
}

function setVisible(elements: readonly HTMLElement[], targetSelector?: string): void {
  for (const element of elements) {
    if (targetSelector) {
      element.dataset.scrollRevealTargetState = "revealed";
    } else {
      element.dataset.scrollRevealState = "revealed";
    }
    element.style.removeProperty("opacity");
    element.style.removeProperty("transform");
  }
}

function resetVisibility(elements: readonly HTMLElement[], targetSelector?: string): void {
  for (const element of elements) {
    if (targetSelector) {
      delete element.dataset.scrollRevealTargetState;
    } else {
      delete element.dataset.scrollRevealState;
    }
    element.style.removeProperty("opacity");
    element.style.removeProperty("transform");
  }
}

function markPending(elements: readonly HTMLElement[], targetSelector?: string): void {
  for (const element of elements) {
    if (targetSelector) {
      element.dataset.scrollRevealTargetState = "pending";
    } else {
      element.dataset.scrollRevealState = "pending";
    }
  }
}

function getRevealTransforms(variant: ScrollRevealVariant): RevealTransforms {
  if (variant === "mask") return { from: HEADING_OFFSET, to: "none" };
  if (variant === "slide") return { from: SLIDE_OFFSET, to: "none" };
  if (variant === "fade") return { from: "none", to: "none" };
  return { from: LIFT_OFFSET, to: "none" };
}

function animateReveal(
  elements: readonly HTMLElement[],
  variant: ScrollRevealVariant,
  delay: number,
  stagger: number,
): AnimationControl[] {
  const animations: AnimationControl[] = [];
  const transforms = getRevealTransforms(variant);

  elements.forEach((element, index) => {
    const animation = animate(
      element,
      {
        opacity: [0, 1],
        transform: [transforms.from, transforms.to],
      },
      {
        delay: delay + index * stagger,
        duration: REVEAL_DURATION,
        ease: "easeOut",
      },
    );
    animations.push(animation);
  });

  return animations;
}

export function ScrollReveal({
  children,
  as = "div",
  className,
  delay = 0,
  id,
  stagger = 0,
  targetSelector,
  variant = "lift",
}: ScrollRevealProps): ReactElement {
  const elementRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const root = elementRef.current;
    if (!root || typeof IntersectionObserver === "undefined") return;

    const preference = window.matchMedia(REDUCED_MOTION_QUERY);
    if (preference.matches || document.visibilityState !== "visible") return;

    const elements = targetSelector
      ? Array.from(root.querySelectorAll<HTMLElement>(targetSelector))
      : [root];
    if (elements.length === 0) return;

    markPending(elements, targetSelector);

    let controls: AnimationControl[] = [];
    let isAnimating = false;
    let isFinished = false;

    const finishImmediately = (): void => {
      if (isFinished) return;
      isFinished = true;
      observer.disconnect();
      controls.forEach((control) => control.stop());
      controls = [];
      setVisible(elements, targetSelector);
    };

    const reveal = (): void => {
      if (isFinished || isAnimating) return;
      isAnimating = true;
      observer.disconnect();
      setVisible(elements, targetSelector);
      controls = animateReveal(elements, variant, delay, stagger);
    };

    const handleVisibilityChange = (): void => {
      if (document.visibilityState !== "visible") finishImmediately();
    };

    const handleMotionPreferenceChange = (event: MediaQueryListEvent): void => {
      if (event.matches) finishImmediately();
    };

    const observer = new IntersectionObserver(
      (entries) => {
        if (document.visibilityState !== "visible" || preference.matches) {
          finishImmediately();
          return;
        }
        if (entries.some((entry) => entry.isIntersecting)) reveal();
      },
      { rootMargin: REVEAL_ROOT_MARGIN, threshold: REVEAL_THRESHOLD },
    );
    observer.observe(root);
    document.addEventListener("visibilitychange", handleVisibilityChange);
    preference.addEventListener("change", handleMotionPreferenceChange);

    return () => {
      observer.disconnect();
      controls.forEach((control) => control.stop());
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      preference.removeEventListener("change", handleMotionPreferenceChange);
      resetVisibility(elements, targetSelector);
    };
  }, [delay, stagger, targetSelector, variant]);

  const classes = joinClasses("scroll-reveal", className);
  const setElementRef = (element: HTMLElement | null): void => {
    elementRef.current = element;
  };

  const Element = as;
  return <Element ref={setElementRef} className={classes} data-scroll-reveal={variant} id={id}>{children}</Element>;
}

function renderPlainLines(lines: readonly string[]): ReactElement[] {
  return lines.flatMap((line, index) => {
    const content = <Fragment key={`line-${index}`}>{line}</Fragment>;
    return index === 0 ? [content] : [<br key={`break-${index}`} />, content];
  });
}

function renderAnimatedLines(lines: readonly string[], treatment: "line" | "word"): ReactElement[] {
  return lines.flatMap((line, lineIndex) => {
    const lineContent = treatment === "line"
      ? <span className="scroll-heading-line-text">{line}</span>
      : line.trim().split(/\s+/u).map((word, wordIndex) => (
        <Fragment key={`${word}-${wordIndex}`}>
          {wordIndex > 0 ? " " : null}
          <span className="scroll-heading-word">{word}</span>
        </Fragment>
      ));
    const lineElement = <span className="scroll-heading-line" key={`line-${lineIndex}`}>{lineContent}</span>;
    return lineIndex === 0 ? [lineElement] : [<Fragment key={`space-${lineIndex}`}> </Fragment>, lineElement];
  });
}

export function ScrollHeading({ lines, className, id, treatment = "plain" }: ScrollHeadingProps): ReactElement {
  const classes = joinClasses("scroll-heading", `scroll-heading-${treatment}`, className);

  if (treatment === "plain") {
    return <h2 className={classes} id={id}>{renderPlainLines(lines)}</h2>;
  }

  if (treatment === "block") {
    return (
      <ScrollReveal as="h2" className={classes} id={id} variant="fade">
        {renderPlainLines(lines)}
      </ScrollReveal>
    );
  }

  return (
    <ScrollReveal
      as="h2"
      className={classes}
      id={id}
      stagger={treatment === "line" ? 0.1 : 0.055}
      targetSelector={treatment === "line" ? ".scroll-heading-line-text" : ".scroll-heading-word"}
      variant="mask"
    >
      {renderAnimatedLines(lines, treatment)}
    </ScrollReveal>
  );
}
