import React, { useEffect, useState } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import "./style.css";
import CurrentEvidenceSection from "./CurrentEvidenceSection";
import SentimentEvidenceDisclosure from "./SentimentEvidenceDisclosure";
import SentimentHero from "./SentimentHero";
import SentimentHistorySection from "./SentimentHistorySection";
import SentimentOutlookSection from "./SentimentOutlookSection";
import WatchConditionsSection from "./WatchConditionsSection";

type NumericValue = number | string | null | undefined;

export type SentimentAction = {
  id: "refresh" | "reload";
  label: string;
  kind: "primary" | "secondary";
  detail?: string;
};

type AxisRange = {
  sample_count?: number;
  percentile?: NumericValue;
  position_label?: string;
  min_value?: NumericValue;
  max_value?: NumericValue;
  detail?: string;
};

export type SentimentAxis = {
  label: string;
  source: string;
  available: boolean;
  direction: string;
  direction_label: string;
  tone: string;
  current?: NumericValue;
  previous?: NumericValue;
  change?: NumericValue;
  latest_date?: string;
  previous_date?: string;
  range?: AxisRange;
  detail?: string;
  component_balance?: {
    greed_count?: number;
    fear_count?: number;
    neutral_count?: number;
    direction?: string;
  };
  components_support?: string;
  spread?: NumericValue;
  responses?: {
    bullish?: NumericValue;
    neutral?: NumericValue;
    bearish?: NumericValue;
  };
};

type CrossRead = {
  phase: string;
  phase_label: string;
  status: string;
  tone: string;
  headline: string;
  meaning: string;
  confidence_note?: string;
  market_direction: string;
  survey_direction: string;
};

type CnnEvidence = {
  series: string;
  label_ko: string;
  score?: NumericValue;
  rating?: string;
  direction?: string;
  tone?: string;
  what_it_checks?: string;
  current_reading?: string;
  latest?: NumericValue;
  latest_date?: string;
  previous?: NumericValue;
  previous_date?: string;
  change?: NumericValue;
  change_direction?: string;
};

export type AaiiComparison = {
  key: "bullish" | "neutral" | "bearish";
  label: string;
  current?: NumericValue;
  historical_average?: NumericValue;
  difference_pp?: NumericValue;
  tone?: string;
};

export type ChartPoint = {
  date: string;
  series: string;
  value?: NumericValue;
  source?: string;
  status_label?: string;
};

export type ChartPanel = {
  title: string;
  basis: string;
  unit: "score_0_100" | "percent" | "percentage_point";
  latest?: {
    date: string;
    value?: NumericValue;
    label: string;
  };
  series: ChartPoint[];
};

export type WatchCondition = {
  key: "confirm" | "reverse" | "persist";
  label: string;
  condition: string;
  basis: string;
  tone?: string;
};

type SentimentEvidenceRows = Record<string, number | string | null | undefined>[];

export type OutlookStatus = "VERIFIED" | "PROVISIONAL" | "UNAVAILABLE";

export type OutlookProbability = {
  key?: string;
  label: string;
  value: number;
  baseline?: number | null;
  difference_pp?: number | null;
};

export type OutlookHorizon = {
  key: "1W" | "1M";
  label: string;
  period_label: string;
  trading_days: 5 | 20;
  status: OutlookStatus;
  status_label: string;
  dominant_path?: string;
  probabilities: OutlookProbability[];
  baseline?: number | null;
  episode_count: number;
  validation_evidence: string[];
  status_reason: string;
};

export type SentimentWorkbenchPayload = {
  schema_version: "sentiment_react_workbench_v2";
  component: "SentimentWorkbench";
  command: {
    title: string;
    detail: string;
    actions: SentimentAction[];
  };
  summary: {
    phase: string;
    phase_label: string;
    status: string;
    tone: string;
    headline: string;
    summary: string;
    latest_observation_date: string;
  };
  axes: {
    market_behavior: SentimentAxis;
    investor_survey: SentimentAxis;
  };
  cross_read: CrossRead;
  freshness: {
    latest_observation_date: string;
    source_count: number;
    stale_count: number;
    missing_count: number;
    detail: string;
    tone: string;
  };
  evidence: {
    cnn_components: CnnEvidence[];
    aaii_comparison: AaiiComparison[];
  };
  charts: {
    cnn: ChartPanel;
    aaii_responses: ChartPanel;
    aaii_spread: ChartPanel;
  };
  outlook: {
    status: "AVAILABLE" | "UNAVAILABLE";
    summary: string;
    horizons: OutlookHorizon[];
  };
  watch_conditions: WatchCondition[];
  raw_evidence: {
    sentiment_rows: SentimentEvidenceRows;
    component_rows: SentimentEvidenceRows;
    history_rows: SentimentEvidenceRows;
    warnings: string[];
  };
  boundary_note: string;
  action_boundary: "python_dispatch_only";
};

type Props = ComponentProps & {
  args: {
    payload?: SentimentWorkbenchPayload;
  };
};

export function toneColor(tone?: string) {
  const normalized = String(tone || "neutral").toLowerCase();
  if (normalized === "positive") return "#0f766e";
  if (normalized === "warning") return "#b45309";
  if (normalized === "danger") return "#dc2626";
  return "#64748b";
}

export function displayValue(value: NumericValue, suffix = "") {
  if (value === undefined || value === null || value === "") return "-";
  if (typeof value === "number") return Number.isFinite(value) ? `${value.toFixed(1)}${suffix}` : "-";
  return `${value}${suffix}`;
}

function numericValue(value: NumericValue) {
  if (value === undefined || value === null || value === "") return null;
  const parsed = typeof value === "number" ? value : Number.parseFloat(String(value));
  return Number.isFinite(parsed) ? parsed : null;
}

export function signedValue(value: NumericValue, suffix = "") {
  const parsed = numericValue(value);
  if (parsed === null) return "-";
  return `${parsed > 0 ? "+" : ""}${parsed.toFixed(1)}${suffix}`;
}

function syncFrameHeightSoon() {
  Streamlit.setFrameHeight();
  window.requestAnimationFrame(() => Streamlit.setFrameHeight());
  window.setTimeout(() => Streamlit.setFrameHeight(), 160);
}

function SentimentWorkbench({ args }: Props) {
  const payload = args.payload;
  const [pendingActionLabel, setPendingActionLabel] = useState("");

  useEffect(() => { syncFrameHeightSoon(); });

  if (!payload) return null;
  const isWorkbenchPayload = payload.component === "SentimentWorkbench";
  const isV2Payload = payload.schema_version === "sentiment_react_workbench_v2";
  if (!isWorkbenchPayload || !isV2Payload) return null;

  const emitAction = (action: SentimentAction) => {
    setPendingActionLabel(action.label);
    Streamlit.setComponentValue({ event: { id: action.id, nonce: Date.now() } });
  };
  return (
    <section className="sentiment-workbench" data-action-boundary={payload.action_boundary} data-schema-version={payload.schema_version}>
      <SentimentHero payload={payload} pendingActionLabel={pendingActionLabel} onAction={emitAction} />
      <CurrentEvidenceSection aaiiComparison={payload.evidence.aaii_comparison} axes={payload.axes} />
      <SentimentHistorySection charts={payload.charts} />
      <SentimentOutlookSection outlook={payload.outlook} />
      <WatchConditionsSection watchConditions={payload.watch_conditions} />
      <SentimentEvidenceDisclosure onToggle={syncFrameHeightSoon} payload={payload} />
    </section>
  );
}

export default withStreamlitConnection(SentimentWorkbench);
