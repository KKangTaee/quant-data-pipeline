import React, { useEffect, useState } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import "./style.css";
import CurrentEvidenceSection from "./CurrentEvidenceSection";
import SentimentHero from "./SentimentHero";
import SentimentHistorySection from "./SentimentHistorySection";

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

function componentChangeLabel(item: CnnEvidence) {
  return signedValue(item.change, "p");
}

function rowColumns(rows: SentimentEvidenceRows) {
  const keys: string[] = [];
  rows.forEach((row) => Object.keys(row).forEach((key) => {
    if (!keys.includes(key)) keys.push(key);
  }));
  return keys.slice(0, 7);
}

function EvidenceTable({ rows, title }: { rows: SentimentEvidenceRows; title: string }) {
  const columns = rowColumns(rows);
  return (
    <div className="sentiment-workbench__evidence-table">
      <div className="sentiment-workbench__evidence-table-title"><span>{title}</span><strong>{rows.length}</strong></div>
      {rows.length === 0 || columns.length === 0 ? (
        <p className="sentiment-workbench__empty">표시할 저장 근거가 없습니다.</p>
      ) : (
        <div className="sentiment-workbench__evidence-scroll">
          <table>
            <thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={`${title}-${rowIndex}`}>
                  {columns.map((column) => <td key={`${title}-${rowIndex}-${column}`}>{displayValue(row[column])}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
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

      <section className="sentiment-workbench__evidence-section">
        <div className="sentiment-workbench__section-heading"><div><span>Evidence</span><h3>두 축의 상세 근거</h3></div><small>중복 없이 source별 한 번만 표시</small></div>
        <div className="sentiment-workbench__evidence-columns">
          <article className="sentiment-workbench__cnn-evidence">
            <header><div><strong>CNN 구성요소</strong><small>시장 행동의 내부 근거</small></div><span>{payload.evidence.cnn_components.length}</span></header>
            {payload.evidence.cnn_components.map((item) => (
              <div className="sentiment-workbench__cnn-evidence-row" key={item.series}>
                <div><strong>{item.label_ko || item.series}</strong><small>{item.what_it_checks}</small></div>
                <div><b>{displayValue(item.score)}</b><span>{item.rating}</span></div>
                <p>{item.current_reading}</p>
                <small className="sentiment-workbench__evidence-change">직전 대비 {componentChangeLabel(item)}</small>
              </div>
            ))}
          </article>
          <article className="sentiment-workbench__aaii-evidence">
            <header><div><strong>AAII 장기평균 비교</strong><small>개인투자자 인식의 기준점</small></div><span>3</span></header>
            {payload.evidence.aaii_comparison.map((item) => (
              <div className="sentiment-workbench__aaii-row" key={item.key}>
                <strong>{item.label}</strong>
                <div><b>{displayValue(item.current, "%")}</b><span>장기평균 {displayValue(item.historical_average, "%")}</span></div>
                <em>{signedValue(item.difference_pp, "pp")}</em>
              </div>
            ))}
          </article>
        </div>
      </section>

      <SentimentHistorySection charts={payload.charts} />

      <section className="sentiment-workbench__watch-section">
        <div className="sentiment-workbench__section-heading"><div><span>Watch</span><h3>다음 확인 조건</h3></div><small>예측이 아닌 관찰 checklist</small></div>
        <div className="sentiment-workbench__watch-grid">
          {payload.watch_conditions.map((item) => <article key={item.label}><span>{item.label}</span><p>{item.condition}</p><small>{item.basis}</small></article>)}
        </div>
      </section>

      <details className="sentiment-workbench__raw-disclosure">
        <summary>원본 / 저장 근거 보기</summary>
        {payload.raw_evidence.warnings.length ? <div className="sentiment-workbench__warnings">{payload.raw_evidence.warnings.map((warning) => <span key={warning}>{warning}</span>)}</div> : null}
        <div className="sentiment-workbench__raw-grid">
          <EvidenceTable rows={payload.raw_evidence.sentiment_rows} title="Sentiment rows" />
          <EvidenceTable rows={payload.raw_evidence.component_rows} title="Component rows" />
          <EvidenceTable rows={payload.raw_evidence.history_rows} title="History rows" />
        </div>
      </details>
    </section>
  );
}

export default withStreamlitConnection(SentimentWorkbench);
