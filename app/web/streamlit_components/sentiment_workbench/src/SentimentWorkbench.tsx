import React, { useEffect, useState } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import "./style.css";

type NumericValue = number | string | null | undefined;

type SentimentAction = {
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

type SentimentAxis = {
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

type AaiiComparison = {
  key: "bullish" | "neutral" | "bearish";
  label: string;
  current?: NumericValue;
  historical_average?: NumericValue;
  difference_pp?: NumericValue;
  tone?: string;
};

type ChartPoint = {
  date: string;
  series: string;
  value?: NumericValue;
  source?: string;
};

type ChartPanel = {
  title: string;
  basis: string;
  unit: "score_0_100" | "percent" | "percentage_point";
  series: ChartPoint[];
};

type WatchCondition = {
  label: string;
  condition: string;
  basis: string;
  tone?: string;
};

type SentimentEvidenceRows = Record<string, number | string | null | undefined>[];

type SentimentWorkbenchPayload = {
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

function toneColor(tone?: string) {
  const normalized = String(tone || "neutral").toLowerCase();
  if (normalized === "positive") return "#0f766e";
  if (normalized === "warning") return "#b45309";
  if (normalized === "danger") return "#dc2626";
  return "#64748b";
}

function displayValue(value: NumericValue, suffix = "") {
  if (value === undefined || value === null || value === "") return "-";
  if (typeof value === "number") return Number.isFinite(value) ? `${value.toFixed(1)}${suffix}` : "-";
  return `${value}${suffix}`;
}

function numericValue(value: NumericValue) {
  if (value === undefined || value === null || value === "") return null;
  const parsed = typeof value === "number" ? value : Number.parseFloat(String(value));
  return Number.isFinite(parsed) ? parsed : null;
}

function signedValue(value: NumericValue, suffix = "") {
  const parsed = numericValue(value);
  if (parsed === null) return "-";
  return `${parsed > 0 ? "+" : ""}${parsed.toFixed(1)}${suffix}`;
}

function componentChangeLabel(item: CnnEvidence) {
  return signedValue(item.change, "p");
}

function rangeWidth(range?: AxisRange) {
  const percentile = numericValue(range?.percentile);
  return `${Math.max(0, Math.min(100, percentile ?? 0))}%`;
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

function SentimentAxisCard({ axis, kind }: { axis: SentimentAxis; kind: "cnn" | "aaii" }) {
  const balance = axis.component_balance;
  const responses = axis.responses;
  return (
    <article
      aria-label={kind === "cnn" ? "시장 행동" : "개인투자자 설문"}
      className="sentiment-workbench__axis-card"
      style={{ "--metric-tone": toneColor(axis.tone) } as React.CSSProperties}
    >
      <header className="sentiment-workbench__axis-head">
        <div><span>{axis.label}</span><small>{axis.source}</small></div>
        <strong>{axis.direction_label}</strong>
      </header>
      <div className="sentiment-workbench__axis-primary">
        <b>{displayValue(axis.current, kind === "aaii" ? "pp" : "")}</b>
        <span>직전 대비 {signedValue(axis.change, kind === "aaii" ? "pp" : "p")}</span>
      </div>
      {kind === "cnn" ? (
        <div className="sentiment-workbench__axis-breakdown">
          <span>탐욕 <b>{balance?.greed_count ?? 0}</b></span>
          <span>중립 <b>{balance?.neutral_count ?? 0}</b></span>
          <span>공포 <b>{balance?.fear_count ?? 0}</b></span>
        </div>
      ) : (
        <div className="sentiment-workbench__axis-breakdown">
          <span>Bullish <b>{displayValue(responses?.bullish, "%")}</b></span>
          <span>Neutral <b>{displayValue(responses?.neutral, "%")}</b></span>
          <span>Bearish <b>{displayValue(responses?.bearish, "%")}</b></span>
        </div>
      )}
      <div className="sentiment-workbench__axis-range">
        <div><span>최근 저장 범위</span><strong>{axis.range?.position_label || "자료 부족"}</strong></div>
        <div className="sentiment-workbench__axis-range-track" aria-label={`${axis.label} recent percentile`}>
          <span style={{ width: rangeWidth(axis.range) }} />
        </div>
        <small>{axis.range?.sample_count ?? 0}개 관측 · percentile {displayValue(axis.range?.percentile)}</small>
      </div>
      <p>{axis.detail}</p>
      {kind === "cnn" && axis.components_support ? <small className="sentiment-workbench__axis-note">{axis.components_support}</small> : null}
    </article>
  );
}

function SimpleChartPreview({ panel }: { panel: ChartPanel }) {
  const latest = panel.series.slice(-4);
  return (
    <div className="sentiment-workbench__chart-preview">
      <header><div><strong>{panel.title}</strong><small>{panel.basis}</small></div><span>{panel.series.length}개</span></header>
      {latest.length ? (
        <div className="sentiment-workbench__chart-preview-list">
          {latest.map((point) => <span key={`${point.series}-${point.date}`}>{point.series} <b>{displayValue(point.value)}</b></span>)}
        </div>
      ) : <p className="sentiment-workbench__empty">추이를 그릴 관측이 부족합니다.</p>}
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
  const [chartTab, setChartTab] = useState<"cnn" | "aaii_responses" | "aaii_spread">("cnn");

  useEffect(() => { syncFrameHeightSoon(); });

  if (!payload) return null;
  const isWorkbenchPayload = payload.component === "SentimentWorkbench";
  const isV2Payload = payload.schema_version === "sentiment_react_workbench_v2";
  if (!isWorkbenchPayload || !isV2Payload) return null;

  const emitAction = (action: SentimentAction) => {
    setPendingActionLabel(action.label);
    Streamlit.setComponentValue({ event: { id: action.id, nonce: Date.now() } });
  };
  const activeChart = payload.charts[chartTab];

  return (
    <section className="sentiment-workbench" data-action-boundary={payload.action_boundary} data-schema-version={payload.schema_version}>
      <section className="sentiment-workbench__hero" style={{ "--sentiment-tone": toneColor(payload.summary.tone) } as React.CSSProperties}>
        <div className="sentiment-workbench__hero-copy">
          <div className="sentiment-workbench__phase-row">
            <span className="sentiment-workbench__phase-pill">{payload.summary.phase_label}</span>
            <span className="sentiment-workbench__kicker">Sentiment</span>
          </div>
          <h2 className="sentiment-workbench__headline">{payload.summary.headline}</h2>
          <p className="sentiment-workbench__summary-copy">{payload.summary.summary}</p>
          <div className="sentiment-workbench__fallback-note">{payload.boundary_note}</div>
        </div>
        <aside className="sentiment-workbench__command">
          <div><strong>{payload.command.title}</strong><small>{payload.command.detail}</small></div>
          <div className="sentiment-workbench__actions">
            {payload.command.actions.map((action) => (
              <button className={`sentiment-workbench__action sentiment-workbench__action--${action.kind}`} key={action.id} onClick={() => emitAction(action)} title={action.detail} type="button">{action.label}</button>
            ))}
          </div>
          {pendingActionLabel ? <span className="sentiment-workbench__action-feedback">요청 전송 · {pendingActionLabel}</span> : null}
        </aside>
      </section>

      <div className="sentiment-workbench__freshness-strip">
        <span>자료 기준 <b>{payload.freshness.latest_observation_date}</b></span>
        <span>{payload.freshness.detail}</span>
        <span>source {payload.freshness.source_count}</span>
      </div>

      <section className="sentiment-workbench__axis-grid">
        <SentimentAxisCard axis={payload.axes.market_behavior} kind="cnn" />
        <SentimentAxisCard axis={payload.axes.investor_survey} kind="aaii" />
      </section>

      <section className="sentiment-workbench__cross-read" style={{ "--metric-tone": toneColor(payload.cross_read.tone) } as React.CSSProperties}>
        <div className="sentiment-workbench__section-heading"><div><span>Cross read</span><h3>현재 판정</h3></div><small>CNN 행동 × AAII 인식</small></div>
        <div className="sentiment-workbench__cross-read-status"><strong>{payload.cross_read.status}</strong><span>{payload.cross_read.phase_label}</span></div>
        <p className="sentiment-workbench__cross-read-meaning">{payload.cross_read.meaning}</p>
        {payload.cross_read.confidence_note ? <small>{payload.cross_read.confidence_note}</small> : null}
      </section>

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

      <section className="sentiment-workbench__chart-section">
        <div className="sentiment-workbench__section-heading"><div><span>History</span><h3>그래프로 보는 근거</h3></div><small>source 단위별 분리</small></div>
        <div className="sentiment-workbench__chart-tabs" role="tablist" aria-label="Sentiment evidence views">
          {(["cnn", "aaii_responses", "aaii_spread"] as const).map((key) => (
            <button aria-selected={chartTab === key} className={chartTab === key ? "is-active" : ""} key={key} onClick={() => setChartTab(key)} role="tab" type="button">
              {key === "cnn" ? "CNN 행동" : key === "aaii_responses" ? "AAII 응답" : "AAII Spread"}
            </button>
          ))}
        </div>
        <div className="sentiment-workbench__chart-panel"><SimpleChartPreview panel={activeChart} /></div>
      </section>

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
