"use client";

import { useInView, useReducedMotion } from "motion/react";
import { useAnimate } from "motion/react-mini";
import { useEffect } from "react";

import { MOTION } from "@/components/motion/tokens";

interface RelationLineProps {
  readonly order?: number;
}

export function RelationLine({ order = 0 }: RelationLineProps): React.JSX.Element {
  const reduceMotion = useReducedMotion();
  const [scope, animate] = useAnimate<HTMLSpanElement>();
  const isInView = useInView(scope, MOTION.viewport);

  useEffect(() => {
    if (reduceMotion || !isInView || !scope.current) {
      return;
    }

    const controls = animate(
      scope.current,
      { transform: ["scaleX(0)", "scaleX(1)"] },
      {
        delay: order * MOTION.stagger.compact,
        duration: MOTION.duration.state,
        ease: MOTION.ease,
      },
    );

    return () => controls.stop();
  }, [animate, isInView, order, reduceMotion, scope]);

  return (
    <span
      aria-hidden="true"
      className="relation-line"
      ref={scope}
    />
  );
}
