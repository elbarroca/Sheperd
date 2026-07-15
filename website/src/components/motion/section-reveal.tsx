"use client";

import { useInView, useReducedMotion } from "motion/react";
import { useAnimate } from "motion/react-mini";
import { useEffect } from "react";

import { MOTION } from "@/components/motion/tokens";

interface SectionRevealProps {
  readonly children: React.ReactNode;
  readonly variant?: "lift" | "shift" | "settle";
}

export function SectionReveal({
  children,
  variant = "lift",
}: SectionRevealProps): React.JSX.Element {
  const reduceMotion = useReducedMotion();
  const [scope, animate] = useAnimate<HTMLDivElement>();
  const isInView = useInView(scope, MOTION.viewport);

  useEffect(() => {
    if (reduceMotion || !isInView || !scope.current) {
      return;
    }

    const initialTransform = {
      lift: `translateY(${MOTION.distance.enter}px)`,
      shift: `translateX(${MOTION.distance.relation}px)`,
      settle: `scale(${MOTION.scale.settle})`,
    }[variant];
    const controls = animate(
      scope.current,
      {
        transform: [initialTransform, "none"],
      },
      { duration: MOTION.duration.narrative, ease: MOTION.ease },
    );

    return () => controls.stop();
  }, [animate, isInView, reduceMotion, scope, variant]);

  return (
    <div className="section-reveal" data-reveal={variant} ref={scope}>
      {children}
    </div>
  );
}
