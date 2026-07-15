"use client";

import { spring } from "motion";
import { useReducedMotion } from "motion/react";
import { useAnimate } from "motion/react-mini";
import { useEffect, useState } from "react";

import { MOTION } from "@/components/motion/tokens";

interface ContainerAssemblyProps {
  readonly evidenceClasses: readonly {
    readonly label: string;
    readonly detail: string;
  }[];
}

const OFFSETS = [
  { x: MOTION.distance.relation, y: -MOTION.distance.enter },
  { x: -MOTION.distance.enter, y: MOTION.distance.relation },
  { x: MOTION.distance.enter, y: MOTION.distance.enter },
] as const;

export function ContainerAssembly({
  evidenceClasses,
}: ContainerAssemblyProps): React.JSX.Element {
  const reduceMotion = useReducedMotion();
  const [scope, animate] = useAnimate<HTMLUListElement>();
  const [pinnedIndex, setPinnedIndex] = useState<number | null>(null);

  useEffect(() => {
    if (reduceMotion || !scope.current) {
      return;
    }

    const modules = Array.from(
      scope.current.querySelectorAll<HTMLElement>(".container-module"),
    );
    const controls = modules.map((module, index) => {
      const offset = OFFSETS[index] ?? OFFSETS[0];
      return animate(
        module,
        {
          transform: [
            `translate(${offset.x}px, ${offset.y}px)`,
            "translate(0px, 0px)",
          ],
        },
        {
          ...MOTION.spring,
          type: spring,
          delay: index * MOTION.stagger.compact,
        },
      );
    });

    return () => controls.forEach((control) => control.stop());
  }, [animate, reduceMotion, scope]);

  return (
    <ul
      className="container-assembly"
      aria-label="Review record categories"
      ref={scope}
    >
      {evidenceClasses.map(({ detail, label }, index) => (
        <li key={label}>
          <button
            aria-describedby={`hero-evidence-detail-${index}`}
            aria-pressed={pinnedIndex === index}
            className="container-module"
            onClick={() => {
              setPinnedIndex((current) => (current === index ? null : index));
            }}
            type="button"
          >
            <span className="container-module-title">{label}</span>
            <span
              className="container-module-detail"
              id={`hero-evidence-detail-${index}`}
            >
              {detail}
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
}
