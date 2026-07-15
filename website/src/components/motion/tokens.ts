export const MOTION = {
  duration: {
    none: 0,
    micro: 0.16,
    state: 0.24,
    disclosure: 0.32,
    narrative: 0.48,
    hero: 0.72,
  },
  ease: [0.22, 1, 0.36, 1] as const,
  spring: {
    stiffness: 260,
    damping: 30,
    mass: 0.8,
  },
  distance: {
    enter: 12,
    relation: 16,
    hover: 2,
  },
  scale: {
    press: 0.98,
    settle: 0.99,
  },
  stagger: {
    compact: 0.04,
    hero: 0.08,
  },
  viewport: {
    once: true,
    amount: 0.25,
  },
} as const;
