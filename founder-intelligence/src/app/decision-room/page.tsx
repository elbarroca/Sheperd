import type { Metadata } from "next";
import type { JSX } from "react";
import { CustomerDecisionRoom } from "@/components/customer-decision-room";
import { getDecisionRoomExperiments } from "@/lib/data";

export const metadata: Metadata = {
  title: "Customer and decision room",
  description: "Customer, economics, offer, claims, journey, experiment, and outcome decisions for SheperD.",
};

export default function DecisionRoomPage(): JSX.Element {
  return <CustomerDecisionRoom experiments={getDecisionRoomExperiments()} />;
}
