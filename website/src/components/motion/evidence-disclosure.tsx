"use client";

import { lazy, Suspense, useId, useState } from "react";

import type { PromptItem } from "@/content/site";

const loadAnimatedDisclosurePanel = () =>
  import("@/components/motion/animated-disclosure-panel").then((module) => ({
    default: module.AnimatedDisclosurePanel,
  }));
const AnimatedDisclosurePanel = lazy(loadAnimatedDisclosurePanel);

interface EvidenceDisclosureProps {
  readonly items: readonly PromptItem[];
}

interface StaticDisclosurePanelProps {
  readonly item: PromptItem | null;
}

function StaticDisclosurePanel({
  item,
}: StaticDisclosurePanelProps): React.JSX.Element {
  if (!item) {
    return (
      <p className="evidence-disclosure-empty">
        Select a checklist category.
      </p>
    );
  }

  return (
    <div aria-live="polite" className="evidence-disclosure-panel">
      <span className="evidence-disclosure-index" aria-hidden="true">
        Record
      </span>
      <div>
        <h3>{item.title}</h3>
        <p>{item.prompt}</p>
      </div>
    </div>
  );
}

export function EvidenceDisclosure({
  items,
}: EvidenceDisclosureProps): React.JSX.Element {
  const [openIndex, setOpenIndex] = useState<number | null>(0);
  const [motionEnabled, setMotionEnabled] = useState(false);
  const baseId = useId();
  const panelId = `${baseId}-panel`;
  const selectedItem = openIndex === null ? null : (items[openIndex] ?? null);

  return (
    <div className="evidence-disclosure">
      <div className="evidence-disclosure-controls">
        {items.map((item, index) => {
          const isOpen = openIndex === index;
          const triggerId = `${baseId}-trigger-${index}`;

          return (
            <button
              aria-controls={panelId}
              aria-expanded={isOpen}
              className="evidence-disclosure-trigger"
              id={triggerId}
              key={item.title}
              onClick={() => {
                setMotionEnabled(true);
                setOpenIndex(isOpen ? null : index);
              }}
              onFocus={() => {
                void loadAnimatedDisclosurePanel();
              }}
              type="button"
            >
              <span>{item.title}</span>
              <span aria-hidden="true">{isOpen ? "Close" : "Open"}</span>
            </button>
          );
        })}
      </div>

      <div
        aria-label={openIndex === null ? "Evidence category details" : undefined}
        aria-labelledby={
          openIndex === null ? undefined : `${baseId}-trigger-${openIndex}`
        }
        className="evidence-disclosure-panel-frame"
        id={panelId}
        role="region"
      >
        {motionEnabled ? (
          <Suspense fallback={<StaticDisclosurePanel item={selectedItem} />}>
            <AnimatedDisclosurePanel item={selectedItem} />
          </Suspense>
        ) : (
          <StaticDisclosurePanel item={selectedItem} />
        )}
      </div>

      <noscript>
        <style>{
          ".evidence-disclosure-controls,.evidence-disclosure-panel-frame{display:none}"
        }</style>
        <ul className="no-script-list">
          {items.map((item) => (
            <li key={item.title}>
              <strong>{item.title}</strong>
              <span>{item.prompt}</span>
            </li>
          ))}
        </ul>
      </noscript>
    </div>
  );
}
