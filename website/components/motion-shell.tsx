import type { ReactNode } from "react";
import {
  domAnimation,
  LazyMotion,
  m,
  MotionConfig,
} from "motion/react";

interface MotionShellProps {
  children: ReactNode;
}

interface RevealProps {
  children: ReactNode;
  className?: string;
  delay?: number;
}

export function MotionShell({ children }: MotionShellProps) {
  return (
    <LazyMotion features={domAnimation} strict>
      <MotionConfig reducedMotion="user">{children}</MotionConfig>
    </LazyMotion>
  );
}

export function Reveal({ children, className, delay = 0 }: RevealProps) {
  const classes = ["motion-reveal", className].filter(Boolean).join(" ");

  return (
    <m.div
      className={classes}
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.18 }}
      transition={{ duration: 0.56, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </m.div>
  );
}
