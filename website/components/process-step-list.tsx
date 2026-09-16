import Image from "next/image";
import { type ReactElement } from "react";
import { recoverySteps } from "@/lib/recovery-content";

const stepAssets = {
  invoice: "invoice",
  review: "review",
  recovery: "container",
  value: "value",
} as const;

interface ProcessStepListProps {
  className?: string;
  detailed?: boolean;
}

export function ProcessStepList({
  className,
  detailed = false,
}: ProcessStepListProps): ReactElement {
  const classes = ["recovery-process", className].filter(Boolean).join(" ");

  return (
    <ol className={classes}>
      {recoverySteps.map((step, index) => (
        <li key={step.kind}>
          <span className="step-owner">{step.owner}</span>
          <div className={`step-art step-art-${step.kind}`}>
            <Image
              src={`/media/motion-v2/recovery-${stepAssets[step.kind]}-glass-transparent.png`}
              alt=""
              width={160}
              height={160}
              loading="eager"
              unoptimized
            />
            <span className="step-number">0{index + 1}</span>
          </div>
          <h3>{step.title}</h3>
          {detailed && <p>{step.description}</p>}
        </li>
      ))}
    </ol>
  );
}
