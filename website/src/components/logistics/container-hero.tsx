"use client";

import { useReducedMotion } from "motion/react";
import { useAnimate } from "motion/react-mini";
import { useEffect } from "react";

import { ContainerAssembly } from "@/components/motion/container-assembly";
import { MOTION } from "@/components/motion/tokens";
import { SealLink } from "@/components/motion/seal-link";
import { EditorialImage } from "@/components/ui/editorial-image";
import { siteCopy } from "@/content/site";

export function ContainerHero(): React.JSX.Element {
  const reduceMotion = useReducedMotion();
  const [scope, animate] = useAnimate<HTMLElement>();

  useEffect(() => {
    if (reduceMotion || !scope.current) {
      return;
    }

    const copyElements = Array.from(
      scope.current.querySelectorAll<HTMLElement>(".hero-copy > *"),
    );
    const controls = copyElements.map((element, index) =>
      animate(
        element,
        {
          transform: [
            `translateY(${MOTION.distance.relation}px)`,
            "translateY(0px)",
          ],
        },
        {
          delay: index * MOTION.stagger.hero,
          duration: MOTION.duration.narrative,
          ease: MOTION.ease,
        },
      ),
    );
    const visual = scope.current.querySelector<HTMLElement>(
      ".hero-picture-shell",
    );

    if (visual) {
      controls.push(
        animate(
          visual,
          {
            clipPath: ["inset(0 0 10% 0)", "inset(0 0 0% 0)"],
            opacity: [0.86, 1],
          },
          {
            delay: MOTION.stagger.hero,
            duration: MOTION.duration.hero,
            ease: MOTION.ease,
          },
        ),
      );
    }

    return () => controls.forEach((control) => control.stop());
  }, [animate, reduceMotion, scope]);

  return (
    <section
      className="container-hero"
      aria-labelledby="hero-heading"
      ref={scope}
    >
      <div className="hero-copy">
        <p className="eyebrow">{siteCopy.hero.audience}</p>
        <h1 id="hero-heading">{siteCopy.hero.headline}</h1>
        <p className="hero-support">{siteCopy.hero.support}</p>
        <SealLink href="#review-requirements">{siteCopy.hero.cta}</SealLink>
      </div>

      <div className="hero-visual">
        <div className="hero-picture-shell">
          <EditorialImage
            alt="Blank review papers clipped beside corrugated container steel at an illustrative terminal setting."
            className="hero-picture"
            height={941}
            name="sheperd-control-room-v2"
            priority
            sizes="(max-width: 767px) 100vw, (max-width: 1023px) 78vw, 48vw"
            width={1672}
            widths={[640, 960, 1440]}
          />
        </div>
        <ContainerAssembly evidenceClasses={siteCopy.hero.evidenceClasses} />
      </div>
    </section>
  );
}
