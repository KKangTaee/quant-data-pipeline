export type Period = "since_close" | "last_hour";
export type Tone =
  "positive" | "negative" | "mixed" | "neutral" | "unavailable";
export type Price = {
  key: string;
  label: string;
  return_pct: number | null;
  source_symbols: string[];
  instrument_kind: "futures" | "custom_proxy";
  description: string;
};
export type ConditionEvidence = {
  symbol: string;
  label: string;
  return_pct: number | null;
  direction: string;
};
export type Condition = {
  key: string;
  title: string;
  case: string;
  verdict: string;
  tone: Tone;
  explanation: string;
  evidence: ConditionEvidence[];
  comparison: {
    status: "UNCHANGED" | "CHANGED" | "UNAVAILABLE";
    summary: string;
    previous_verdict?: string;
    previous_start_utc?: string;
    previous_end_utc?: string;
    previous_evidence?: ConditionEvidence[];
  };
};
export type Reading = {
  headline: string;
  tone: Tone;
  observation_facts: string[];
  interpretation: string;
  counter_evidence: string[];
  condition_results: Condition[];
};
export type WindowData = {
  status: string;
  start_utc: string | null;
  end_utc: string | null;
  prices: Price[];
  reading: Reading;
  missing_symbols: string[];
  time_context: {
    basis: string;
    label: string;
    explanation: string;
    evaluated_at_utc: string;
    observation_age_minutes: number | null;
  };
  evidence: {
    source: string;
    rule_version: string;
    calendar_quality: string;
    caveats: string[];
  };
};
export type Payload = {
  schema_version: string;
  windows: Record<Period, WindowData>;
  cycle_background: { state: string; as_of_date: string | null };
  command: {
    ack_nonce?: string;
    pending: boolean;
    result?: { status?: string; message?: string };
  };
};
