"use client";

import { AnimatePresence, motion, useReducedMotion } from "motion/react";

import { MOTION } from "@/components/motion/tokens";
import type { PromptItem } from "@/content/site";

interface AnimatedDisclosurePanelProps {
  readonly item: PromptItem | null;
}

export function AnimatedDisclosurePanel({
  item,
}: AnimatedDisclosurePanelProps): React.JSX.Element {
  const reduceMotion = useReducedMotion();

  return (
    <AnimatePresence initial={false} mode="wait">
      {item ? (
        <motion.div
          animate={{ opacity: 1, y: 0 }}
          aria-live="polite"
          className="evidence-disclosure-panel"
          exit={
            reduceMotion
              ? { opacity: 1, y: 0 }
              : { opacity: 0, y: -MOTION.distance.enter }
          }
          initial={
            reduceMotion ? false : { opacity: 0, y: MOTION.distance.enter }
          }
          key={item.title}
          transition={
            reduceMotion
              ? { duration: MOTION.duration.none }
              : {
                  duration: MOTION.duration.disclosure,
                  ease: MOTION.ease,
                }
          }
        >
          <span className="evidence-disclosure-index" aria-hidden="true">
            Record
          </span>
          <div>
            <h3>{item.title}</h3>
            <p>{item.prompt}</p>
          </div>
        </motion.div>
      ) : (
        <motion.p
          animate={{ opacity: 1 }}
          className="evidence-disclosure-empty"
          exit={{ opacity: 1 }}
          initial={false}
          key="empty"
        >
          Select a checklist category.
        </motion.p>
      )}
    </AnimatePresence>
  );
}
