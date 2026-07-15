"use client";

import { useReducedMotion } from "motion/react";
import { useAnimate } from "motion/react-mini";
import { useEffect, useState } from "react";

import { MOTION } from "@/components/motion/tokens";

interface SealLinkProps {
  readonly children: React.ReactNode;
  readonly className?: string;
  readonly href: string;
  readonly external?: boolean;
}

export function SealLink({
  children,
  className = "",
  href,
  external = false,
}: SealLinkProps): React.JSX.Element {
  const reduceMotion = useReducedMotion();
  const [pressed, setPressed] = useState(false);
  const [scope, animate] = useAnimate<HTMLAnchorElement>();

  useEffect(() => {
    if (reduceMotion || !scope.current) {
      return;
    }

    const controls = animate(
      scope.current,
      {
        transform: `scale(${pressed ? MOTION.scale.press : 1})`,
      },
      { duration: MOTION.duration.micro, ease: MOTION.ease },
    );

    return () => controls.stop();
  }, [animate, pressed, reduceMotion, scope]);

  return (
    <a
      className={`seal-link ${className}`.trim()}
      href={href}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          setPressed(true);
        }
      }}
      onKeyUp={() => setPressed(false)}
      onPointerCancel={() => setPressed(false)}
      onPointerDown={() => setPressed(true)}
      onPointerLeave={() => setPressed(false)}
      onPointerUp={() => setPressed(false)}
      ref={scope}
      rel={external ? "noopener noreferrer" : undefined}
      target={external ? "_blank" : undefined}
    >
      <span className="seal-link-mark" aria-hidden="true" />
      <span>{children}</span>
    </a>
  );
}
