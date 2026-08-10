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
  completed_as_of_date: string;
  observation_mode: "INTRADAY_PROVISIONAL" | "COMPLETED";
  observation_label: string;
  observation_detail: string;
  observed_at_utc?: string | null;
  observed_at_et?: string | null;
  freshness_minutes?: number | null;
  observation_status: ObservationStatus;
  coverage_label: string;
  evidence: string[];
};

export type SessionEvidence = {
  latest_final_session?: string | null;
  pending_session?: string | null;
  status?: string | null;
};
