export interface ProductionBlocker {
  readonly id: string;
  readonly requirement: string;
  readonly resolved: boolean;
}

export const productionBlockers = [
  { id: "EXT-01", requirement: "Approved legal entity and authority", resolved: false },
  { id: "EXT-02", requirement: "Approved privacy notice", resolved: false },
  { id: "EXT-03", requirement: "Approved terms", resolved: false },
  { id: "EXT-04", requirement: "Approved contact and CTA destination", resolved: false },
  { id: "EXT-05", requirement: "Approved product and service wording", resolved: false },
  { id: "EXT-06", requirement: "Approved commercial wording", resolved: false },
  { id: "EXT-07", requirement: "Approved data intake and security controls", resolved: false },
  { id: "EXT-08", requirement: "Named reviewer and exact claim approvals", resolved: false },
  { id: "EXT-09", requirement: "Approved canonical production origin", resolved: false },
  { id: "EXT-10", requirement: "Approved production metadata", resolved: false },
  { id: "EXT-11", requirement: "Approved brand assets", resolved: false },
  { id: "EXT-12", requirement: "Production promotion authority", resolved: false },
] as const satisfies readonly ProductionBlocker[];
