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

type ChartTab = "cnn" | "aaii_responses" | "aaii_spread";

type ParsedChartPoint = ChartPoint & {
  timestamp: number;
  numericValue: number;
};

type HoveredChartPoint = {
  date: string;
  timestamp: number;
  values: ParsedChartPoint[];
  x: number;
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

const chartWidth = 900;
const chartHeight = 320;
const chartMargin = { top: 18, right: 24, bottom: 42, left: 54 };
const plotWidth = chartWidth - chartMargin.left - chartMargin.right;
const plotHeight = chartHeight - chartMargin.top - chartMargin.bottom;
const spreadGuideValues = [-10, 0, 10];

function parsedChartPoints(panel: ChartPanel) {
  return panel.series.flatMap((point) => {
    const timestamp = Date.parse(point.date);
    const value = numericValue(point.value);
    if (!Number.isFinite(timestamp) || value === null) return [];
    return [{ ...point, timestamp, numericValue: value }];
  }).sort((left, right) => left.timestamp - right.timestamp);
}

function chartExtent(points: ParsedChartPoint[]) {
  if (!points.length) return { min: 0, max: 1 };
  const min = points[0].timestamp;
  const max = points[points.length - 1].timestamp;
  return min === max ? { min: min - 43_200_000, max: max + 43_200_000 } : { min, max };
}

function chartDomain(panel: ChartPanel, points: ParsedChartPoint[]) {
  if (panel.unit !== "percentage_point") return { min: 0, max: 100 };
  const maxAbs = Math.max(10, ...points.map((point) => Math.abs(point.numericValue)));
  const rounded = Math.ceil(maxAbs / 10) * 10;
  return { min: -rounded, max: rounded };
}

function xForTimestamp(timestamp: number, extent: { min: number; max: number }) {
  return chartMargin.left + ((timestamp - extent.min) / (extent.max - extent.min)) * plotWidth;
}

function yForValue(value: number, domain: { min: number; max: number }) {
  return chartMargin.top + ((domain.max - value) / (domain.max - domain.min)) * plotHeight;
}

function buildDateTicks(extent: { min: number; max: number }, maxTickCount = 6) {
  return Array.from({ length: maxTickCount }, (_, index) => {
    const ratio = maxTickCount === 1 ? 0 : index / (maxTickCount - 1);
    return extent.min + (extent.max - extent.min) * ratio;
  });
}

function formatChartDate(timestamp: number) {
  const date = new Date(timestamp);
  return `${String(date.getMonth() + 1).padStart(2, "0")}.${String(date.getDate()).padStart(2, "0")}`;
}

function chartSeriesColor(series: string) {
  const normalized = series.toLowerCase();
  if (normalized.includes("bullish")) return "#0f766e";
  if (normalized.includes("bearish")) return "#dc2626";
  if (normalized.includes("neutral")) return "#64748b";
  if (normalized.includes("spread")) return "#7c3aed";
  return "#2563eb";
}

function chartValueSuffix(panel: ChartPanel) {
  if (panel.unit === "percent") return "%";
  if (panel.unit === "percentage_point") return "pp";
  return "";
}

function SentimentLineChart({ panel, chartTab }: { panel: ChartPanel; chartTab: ChartTab }) {
  const points = parsedChartPoints(panel);
  const extent = chartExtent(points);
  const domain = chartDomain(panel, points);
  const [hoveredChartPoint, setHoveredChartPoint] = useState<HoveredChartPoint | null>(null);
  const grouped = points.reduce<Record<string, ParsedChartPoint[]>>((result, point) => {
    (result[point.series] ||= []).push(point);
    return result;
  }, {});
  const dateTicks = buildDateTicks(extent);
  const yTicks = panel.unit === "percentage_point"
    ? [domain.min, domain.min / 2, 0, domain.max / 2, domain.max]
    : [0, 25, 50, 75, 100];
  const guides = chartTab === "aaii_spread" ? spreadGuideValues : [];

  const handleChartHover = (event: React.MouseEvent<SVGSVGElement>) => {
    if (!points.length) return;
    const bounds = event.currentTarget.getBoundingClientRect();
    const viewBoxX = ((event.clientX - bounds.left) / bounds.width) * chartWidth;
    const ratio = Math.max(0, Math.min(1, (viewBoxX - chartMargin.left) / plotWidth));
    const targetTimestamp = extent.min + ratio * (extent.max - extent.min);
    const timestamps = Array.from(new Set(points.map((point) => point.timestamp)));
    const nearestTimestamp = timestamps.reduce((nearest, timestamp) => (
      Math.abs(timestamp - targetTimestamp) < Math.abs(nearest - targetTimestamp) ? timestamp : nearest
    ));
    const values = points.filter((point) => point.timestamp === nearestTimestamp);
    setHoveredChartPoint({
      date: values[0]?.date || new Date(nearestTimestamp).toISOString(),
      timestamp: nearestTimestamp,
      values,
      x: xForTimestamp(nearestTimestamp, extent),
    });
  };

  return (
    <div className="sentiment-workbench__line-chart">
      <header className="sentiment-workbench__chart-title">
        <div><strong>{panel.title}</strong><small>{panel.basis}</small></div>
        <span>{points.length}개 관측</span>
      </header>
      {points.length ? (
        <div className="sentiment-workbench__line-chart-plot">
          <svg
            aria-label="심리 근거 그래프"
            onMouseLeave={() => setHoveredChartPoint(null)}
            onMouseMove={handleChartHover}
            role="img"
            viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          >
            {chartTab === "cnn" ? (
              <g aria-hidden="true">
                <rect className="sentiment-workbench__chart-band sentiment-workbench__chart-band--fear" height={yForValue(25, domain) - yForValue(50, domain)} width={plotWidth} x={chartMargin.left} y={yForValue(50, domain)} />
                <rect className="sentiment-workbench__chart-band sentiment-workbench__chart-band--extreme-fear" height={yForValue(0, domain) - yForValue(25, domain)} width={plotWidth} x={chartMargin.left} y={yForValue(25, domain)} />
                <rect className="sentiment-workbench__chart-band sentiment-workbench__chart-band--greed" height={yForValue(50, domain) - yForValue(75, domain)} width={plotWidth} x={chartMargin.left} y={yForValue(75, domain)} />
                <rect className="sentiment-workbench__chart-band sentiment-workbench__chart-band--extreme-greed" height={yForValue(75, domain) - yForValue(100, domain)} width={plotWidth} x={chartMargin.left} y={yForValue(100, domain)} />
              </g>
            ) : null}
            {yTicks.map((tick) => {
              const y = yForValue(tick, domain);
              return <g key={`y-${tick}`}><line className="sentiment-workbench__chart-gridline" x1={chartMargin.left} x2={chartWidth - chartMargin.right} y1={y} y2={y} /><text className="sentiment-workbench__chart-y-label" textAnchor="end" x={chartMargin.left - 9} y={y + 4}>{tick}</text></g>;
            })}
            {guides.map((guide) => <line className="sentiment-workbench__chart-guide" key={`guide-${guide}`} x1={chartMargin.left} x2={chartWidth - chartMargin.right} y1={yForValue(guide, domain)} y2={yForValue(guide, domain)} />)}
            {dateTicks.map((timestamp) => {
              const x = xForTimestamp(timestamp, extent);
              return <g key={`x-${timestamp}`}><line className="sentiment-workbench__chart-x-tick" x1={x} x2={x} y1={chartHeight - chartMargin.bottom} y2={chartHeight - chartMargin.bottom + 5} /><text className="sentiment-workbench__chart-x-label" textAnchor="middle" x={x} y={chartHeight - 14}>{formatChartDate(timestamp)}</text></g>;
            })}
            {Object.entries(grouped).map(([series, seriesPoints]) => (
              <polyline
                className="sentiment-workbench__chart-line"
                fill="none"
                key={series}
                points={seriesPoints.map((point) => `${xForTimestamp(point.timestamp, extent)},${yForValue(point.numericValue, domain)}`).join(" ")}
                stroke={chartSeriesColor(series)}
              />
            ))}
            {hoveredChartPoint ? (
              <g aria-hidden="true">
                <line className="sentiment-workbench__chart-hover-guide" x1={hoveredChartPoint.x} x2={hoveredChartPoint.x} y1={chartMargin.top} y2={chartHeight - chartMargin.bottom} />
                {hoveredChartPoint.values.map((point) => <circle className="sentiment-workbench__chart-focus-dot" cx={hoveredChartPoint.x} cy={yForValue(point.numericValue, domain)} fill={chartSeriesColor(point.series)} key={`${point.series}-${point.timestamp}`} r={5} />)}
              </g>
            ) : null}
          </svg>
          {hoveredChartPoint ? (
            <div className="sentiment-workbench__chart-tooltip" style={{ left: `${(hoveredChartPoint.x / chartWidth) * 100}%` }}>
              <strong>{hoveredChartPoint.date}</strong>
              {hoveredChartPoint.values.map((point) => <span key={`${point.series}-tooltip`}><i style={{ background: chartSeriesColor(point.series) }} />{point.series}<b>{displayValue(point.numericValue, chartValueSuffix(panel))}</b></span>)}
            </div>
          ) : null}
        </div>
      ) : <p className="sentiment-workbench__empty">추이를 그릴 관측이 부족합니다.</p>}
      <div className="sentiment-workbench__chart-legend">
        {Object.keys(grouped).map((series) => <span key={series}><i style={{ background: chartSeriesColor(series) }} />{series}</span>)}
        {chartTab === "aaii_spread" ? <small>점선: -10 / 0 / +10pp 판정 기준</small> : null}
      </div>
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
  const [chartTab, setChartTab] = useState<ChartTab>("cnn");

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
        <div className="sentiment-workbench__chart-tabs" role="tablist" aria-label="심리 그래프 보기">
          {(["cnn", "aaii_responses", "aaii_spread"] as const).map((key) => (
            <button aria-selected={chartTab === key} className={chartTab === key ? "is-active" : ""} key={key} onClick={() => setChartTab(key)} role="tab" type="button">
              {key === "cnn" ? "CNN 행동" : key === "aaii_responses" ? "AAII 응답" : "AAII Spread"}
            </button>
          ))}
        </div>
        <div aria-live="polite" className="sentiment-workbench__chart-panel" role="tabpanel"><SentimentLineChart chartTab={chartTab} panel={activeChart} /></div>
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
