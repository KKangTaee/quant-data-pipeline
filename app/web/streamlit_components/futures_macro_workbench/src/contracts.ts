import type { ObservationStatus } from "./presentation";

export type FuturesMacroAction = {
  id: "daily_refresh" | "reload";
  label: string;
  kind: "primary" | "secondary";
  detail?: string;
};

export type CommandPayload = {
  title: string;
  detail: string;
  actions: FuturesMacroAction[];
};

export type HeroPayload = {
  kicker: string;
  title: string;
  transition_label: string;
  summary: string;
  today_summary?: string;
  as_of_date: string;
  observation_status: ObservationStatus;
  coverage_label: string;
  evidence: string[];
};

export type SessionEvidence = {
  latest_final_session?: string | null;
  pending_session?: string | null;
  status?: string | null;
};
