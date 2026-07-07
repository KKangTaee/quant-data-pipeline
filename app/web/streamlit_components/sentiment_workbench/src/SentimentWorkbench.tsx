import React, { useEffect, useState } from "react";
import { Streamlit, withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
import "./style.css";

type SentimentAction = {
  id: "refresh" | "reload";
  label: string;
  kind: "primary" | "secondary";
  detail?: string;
};

type SentimentMetric = {
  label: string;
  value: string;
  detail?: string;
  tone?: string;
};

type SentimentAnalysisStep = {
  title: string;
  status?: string;
  detail?: string;
  tone?: string;
};

type SentimentRangeContextItem = {
  series_id?: string;
  series: string;
  latest_value?: number | string | null;
  sample_count?: number;
  min_value?: number | string | null;
  max_value?: number | string | null;
  median_value?: number | string | null;
  percentile?: number | string | null;
  position_label?: string;
  tone?: string;
  detail?: string;
};

type SentimentDivergenceAxis = {
  label: string;
  direction?: string;
  direction_label?: string;
  detail?: string;
  tone?: string;
};

type SentimentDivergenceContext = {
  status: string;
  tone?: string;
  headline_direction?: string;
  component_direction?: string;
  aaii_direction?: string;
  summary?: string;
  items: SentimentDivergenceAxis[];
};

type SentimentComponentHistoryItem = {
  series_id?: string;
  series: string;
  label_ko?: string;
  latest?: number | string | null;
  latest_date?: string;
  previous?: number | string | null;
  previous_date?: string;
  change?: number | string | null;
  change_direction?: string;
  tone?: string;
  detail?: string;
};

type SentimentDriverItem = {
  series: string;
  label_ko: string;
  score?: string;
  rating?: string;
  tone?: string;
  direction?: string;
  current_reading?: string;
};

type SentimentDriverLane = {
  key: string;
  label: string;
  tone?: string;
  count: number;
  items: SentimentDriverItem[];
};

type SentimentComponentExplanation = {
  series: string;
  label_ko: string;
  score?: number | string;
  rating_label_ko?: string;
  tone?: string;
  direction?: string;
  what_it_checks?: string;
  current_reading?: string;
};

type SentimentHistoryPoint = {
  date: string;
  series: string;
  value?: number | string | null;
  source?: string;
};

type SentimentComponentChartItem = {
  series: string;
  score?: number | string | null;
  rating?: string;
  tone?: string;
  direction?: string;
  observation_date?: string;
  current_reading?: string;
};

type SentimentEvidenceRows = Record<string, number | string | null | undefined>[];

type HoveredHistoryPoint = {
  date: string;
  series: string;
  source?: string;
  valueLabel: string;
  x: number;
  y: number;
  color: string;
};

type SentimentWorkbenchPayload = {
  schema_version: "sentiment_react_workbench_v1";
  component: "SentimentWorkbench";
  command: {
    title: string;
    detail: string;
    actions: SentimentAction[];
  };
  summary: {
    phase_label: string;
    headline: string;
    summary: string;
    tone: string;
    metrics: SentimentMetric[];
  };
  freshness: {
    latest_observation_date: string;
    source_count: number;
    stale_count: number;
    missing_count: number;
    detail: string;
    tone: string;
  };
  analysis_steps: SentimentAnalysisStep[];
  drivers: {
    lanes: SentimentDriverLane[];
  };
  interpretation: {
    range_context: SentimentRangeContextItem[];
    divergence: SentimentDivergenceContext;
    component_history: SentimentComponentHistoryItem[];
  };
  component_explanations: SentimentComponentExplanation[];
  charts: {
    history: {
      title: string;
      basis: string;
      series: SentimentHistoryPoint[];
    };
    components: {
      title: string;
      basis: string;
      items: SentimentComponentChartItem[];
    };
  };
  evidence: {
    raw_rows: SentimentEvidenceRows;
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

function toneColor(tone: string | undefined) {
  const normalized = String(tone || "neutral").toLowerCase();
  if (normalized === "positive") {
    return "#0f766e";
  }
  if (normalized === "warning") {
    return "#b45309";
  }
  if (normalized === "danger") {
    return "#dc2626";
  }
  return "#64748b";
}

function displayValue(value: number | string | null | undefined) {
  if (value === undefined || value === null || value === "") {
    return "-";
  }
  if (typeof value === "number") {
    return Number.isFinite(value) ? value.toFixed(1) : "-";
  }
  return value;
}

function numericValue(value: number | string | null | undefined) {
  if (value === undefined || value === null || value === "") {
    return null;
  }
  const numeric = typeof value === "number" ? value : Number.parseFloat(String(value));
  return Number.isFinite(numeric) ? numeric : null;
}

function rangePercentileWidth(value: number | string | null | undefined) {
  const percentile = numericValue(value);
  if (percentile === null) {
    return "0%";
  }
  return `${Math.max(0, Math.min(100, percentile))}%`;
}

function componentChangeLabel(item: SentimentComponentHistoryItem) {
  const change = displayValue(item.change);
  if (change === "-") {
    return "-";
  }
  if (String(item.change_direction || "").toLowerCase() === "up" && !String(change).startsWith("+")) {
    return `+${change}`;
  }
  return change;
}

function rowColumns(rows: SentimentEvidenceRows) {
  const columns: string[] = [];
  rows.forEach((row) => {
    Object.keys(row).forEach((key) => {
      if (!columns.includes(key)) {
        columns.push(key);
      }
    });
  });
  return columns.slice(0, 7);
}

function formatCell(value: number | string | null | undefined) {
  if (value === undefined || value === null || value === "") {
    return "-";
  }
  if (typeof value === "number") {
    return Number.isFinite(value) ? value.toLocaleString(undefined, { maximumFractionDigits: 2 }) : "-";
  }
  return String(value);
}

function EvidenceTable({ rows, title }: { rows: SentimentEvidenceRows; title: string }) {
  const columns = rowColumns(rows);
  return (
    <div className="sentiment-workbench__evidence-table">
      <div className="sentiment-workbench__evidence-table-title">
        <span>{title}</span>
        <strong>{rows.length}</strong>
      </div>
      {rows.length === 0 || columns.length === 0 ? (
        <div className="sentiment-workbench__evidence-empty">근거 row가 없습니다.</div>
      ) : (
        <div className="sentiment-workbench__evidence-scroll">
          <table>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={`${title}-${rowIndex}`}>
                  {columns.map((column) => (
                    <td key={`${title}-${rowIndex}-${column}`}>{formatCell(row[column])}</td>
                  ))}
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
  const [hoveredHistoryPoint, setHoveredHistoryPoint] = useState<HoveredHistoryPoint | null>(null);

  useEffect(() => {
    syncFrameHeightSoon();
  });

  if (!payload) {
    return null;
  }

  const isWorkbenchPayload = payload.component === "SentimentWorkbench";
  if (!isWorkbenchPayload) {
    return null;
  }

  const emitAction = (action: SentimentAction) => {
    setPendingActionLabel(action.label);
    Streamlit.setComponentValue({ event: { id: action.id, nonce: Date.now() } });
  };
  const metricByLabel = (label: string) => payload.summary.metrics.find((metric) => metric.label === label);
  const cnnMetric = metricByLabel("CNN Fear & Greed");
  const aaiiBearishMetric = metricByLabel("AAII Bearish");
  const bullBearSpreadMetric = metricByLabel("Bull-Bear Spread");
  const visibleAnalysisSteps = payload.analysis_steps.filter((step) => !step.title.includes("다음 확인"));
  const divergenceContext = payload.interpretation.divergence;
  const historyPoints = payload.charts.history.series.map((point) => ({
    ...point,
    numericValue: numericValue(point.value),
  }));
  const plottableHistory = historyPoints.filter((point) => point.numericValue !== null);
  const historyValues = plottableHistory.map((point) => point.numericValue as number);
  const historyMin = historyValues.length ? Math.min(...historyValues) : 0;
  const historyMax = historyValues.length ? Math.max(...historyValues) : 1;
  const historyDomainPadding = historyMax === historyMin ? 1 : 0;
  const historyDomainMin = historyMin - historyDomainPadding;
  const historyDomainMax = historyMax + historyDomainPadding;
  const historyRange = historyDomainMax === historyDomainMin ? 1 : historyDomainMax - historyDomainMin;
  const historyDates = Array.from(new Set(plottableHistory.map((point) => point.date))).sort();
  const historySeriesNames = Array.from(new Set(plottableHistory.map((point) => point.series)));
  const chartWidth = 320;
  const chartHeight = 136;
  const chartPaddingX = 38;
  const chartPaddingY = 16;
  const chartInnerWidth = chartWidth - chartPaddingX * 2;
  const chartInnerHeight = chartHeight - chartPaddingY * 2;
  const chartPalette = ["#0f766e", "#b45309", "#2563eb", "#7c3aed", "#dc2626"];
  const xForDate = (date: string) => {
    const index = Math.max(0, historyDates.indexOf(date));
    const divisor = Math.max(1, historyDates.length - 1);
    return chartPaddingX + (index / divisor) * chartInnerWidth;
  };
  const yForValue = (value: number) => chartPaddingY + (1 - (value - historyDomainMin) / historyRange) * chartInnerHeight;
  const historyTicks = [historyDomainMax, historyDomainMin + historyRange / 2, historyDomainMin].map((value) => ({
    value,
    label: value.toLocaleString(undefined, { maximumFractionDigits: 1 }),
    y: yForValue(value),
  }));
  const plottedHistoryPoints = plottableHistory.map((point) => {
    const numeric = point.numericValue as number;
    const seriesIndex = Math.max(0, historySeriesNames.indexOf(point.series));
    return {
      date: point.date,
      series: point.series,
      source: point.source,
      valueLabel: numeric.toLocaleString(undefined, { maximumFractionDigits: 2 }),
      x: xForDate(point.date),
      y: yForValue(numeric),
      color: chartPalette[seriesIndex % chartPalette.length],
    };
  });
  const handleHistoryHover = (event: React.MouseEvent<SVGSVGElement>) => {
    if (!plottedHistoryPoints.length) {
      setHoveredHistoryPoint(null);
      return;
    }
    const bounds = event.currentTarget.getBoundingClientRect();
    const pointerX = ((event.clientX - bounds.left) / Math.max(1, bounds.width)) * chartWidth;
    const pointerY = ((event.clientY - bounds.top) / Math.max(1, bounds.height)) * chartHeight;
    const nearest = plottedHistoryPoints.reduce((best, point) => {
      const pointDistance = Math.hypot(point.x - pointerX, point.y - pointerY);
      const bestDistance = Math.hypot(best.x - pointerX, best.y - pointerY);
      return pointDistance < bestDistance ? point : best;
    });
    setHoveredHistoryPoint(nearest);
  };
  const firstHistoryDate = historyDates[0] || "-";
  const lastHistoryDate = historyDates[historyDates.length - 1] || "-";
  const tooltipLeft = hoveredHistoryPoint
    ? `${Math.min(90, Math.max(12, (hoveredHistoryPoint.x / chartWidth) * 100))}%`
    : "0%";
  const tooltipTop = hoveredHistoryPoint
    ? `${Math.min(90, Math.max(12, (hoveredHistoryPoint.y / chartHeight) * 100))}%`
    : "0%";

  return (
    <section
      className="sentiment-workbench"
      data-action-boundary={payload.action_boundary}
      data-schema-version={payload.schema_version}
      style={{ "--sentiment-tone": toneColor(payload.summary.tone) } as React.CSSProperties}
    >
      <div className="sentiment-workbench__hero">
        <div className="sentiment-workbench__hero-copy">
          <div className="sentiment-workbench__phase-row">
            <span className="sentiment-workbench__phase-pill">{payload.summary.phase_label}</span>
            <span className="sentiment-workbench__kicker">Sentiment</span>
          </div>
          <h2 className="sentiment-workbench__headline">{payload.summary.headline}</h2>
          {payload.summary.summary ? (
            <p className="sentiment-workbench__summary-copy">{payload.summary.summary}</p>
          ) : null}
          <div className="sentiment-workbench__fallback-note">{payload.boundary_note}</div>
        </div>

        <aside
          className="sentiment-workbench__freshness-panel"
          style={{ "--sentiment-tone": toneColor(payload.freshness.tone) } as React.CSSProperties}
        >
          <div className="sentiment-workbench__freshness-label">자료 기준</div>
          <strong className="sentiment-workbench__freshness-date">{payload.freshness.latest_observation_date}</strong>
          <div className="sentiment-workbench__freshness-detail">{payload.freshness.detail}</div>
          <div className="sentiment-workbench__freshness-counts">
            <span>source {payload.freshness.source_count}</span>
            <span>missing {payload.freshness.missing_count}</span>
            <span>stale {payload.freshness.stale_count}</span>
          </div>

          <div className="sentiment-workbench__command">
            <div>
              <div className="sentiment-workbench__command-title">{payload.command.title}</div>
              <div className="sentiment-workbench__command-detail">{payload.command.detail}</div>
            </div>
            <div className="sentiment-workbench__actions" aria-label="Sentiment actions">
              {payload.command.actions.map((action) => (
                <button
                  className={`sentiment-workbench__action sentiment-workbench__action--${action.kind}`}
                  key={action.id}
                  onClick={() => emitAction(action)}
                  title={action.detail}
                  type="button"
                >
                  {action.label}
                </button>
              ))}
            </div>
            {pendingActionLabel ? (
              <div className="sentiment-workbench__action-feedback" aria-live="polite">
                요청 전송 · {pendingActionLabel}
              </div>
            ) : null}
          </div>
        </aside>
      </div>

      <div className="sentiment-workbench__metric-grid">
        {payload.summary.metrics.map((metric) => (
          <div
            className="sentiment-workbench__metric-card"
            key={`${metric.label}-${metric.value}`}
            style={{ "--metric-tone": toneColor(metric.tone) } as React.CSSProperties}
          >
            <div className="sentiment-workbench__metric-label">{metric.label}</div>
            <div className="sentiment-workbench__metric-value">{metric.value}</div>
            {metric.detail ? <div className="sentiment-workbench__metric-detail">{metric.detail}</div> : null}
          </div>
        ))}
        {payload.summary.metrics.length === 0 ? (
          <div className="sentiment-workbench__metric-card sentiment-workbench__metric-card--empty">
            <div className="sentiment-workbench__metric-label">Data</div>
            <div className="sentiment-workbench__metric-value">-</div>
            <div className="sentiment-workbench__metric-detail">저장된 sentiment metric이 없습니다.</div>
          </div>
        ) : null}
      </div>

      <section className="sentiment-workbench__cross-read">
        <div className="sentiment-workbench__section-heading">
          <span>CNN / AAII 같이 보기</span>
          <small>service analysis</small>
        </div>
        <div className="sentiment-workbench__cross-metrics">
          {[cnnMetric, aaiiBearishMetric, bullBearSpreadMetric].filter(Boolean).map((metric) => (
            <div
              className="sentiment-workbench__cross-metric"
              key={metric!.label}
              style={{ "--metric-tone": toneColor(metric!.tone) } as React.CSSProperties}
            >
              <span>{metric!.label}</span>
              <strong>{metric!.value}</strong>
              {metric!.detail ? <small>{metric!.detail}</small> : null}
            </div>
          ))}
        </div>
        <div className="sentiment-workbench__range-context">
          {payload.interpretation.range_context.map((item) => (
            <article
              className="sentiment-workbench__range-card"
              key={item.series}
              style={{ "--metric-tone": toneColor(item.tone) } as React.CSSProperties}
            >
              <div className="sentiment-workbench__range-card-top">
                <span>{item.series}</span>
                {item.position_label ? <strong>{item.position_label}</strong> : null}
              </div>
              <div className="sentiment-workbench__range-value">{displayValue(item.latest_value)}</div>
              <div className="sentiment-workbench__range-track" aria-label={`${item.series} percentile`}>
                <div
                  className="sentiment-workbench__range-fill"
                  style={{ width: rangePercentileWidth(item.percentile) } as React.CSSProperties}
                />
              </div>
              <div className="sentiment-workbench__range-meta">
                <span>min {displayValue(item.min_value)}</span>
                <span>pctl {displayValue(item.percentile)}</span>
                <span>max {displayValue(item.max_value)}</span>
              </div>
              {item.detail ? <p>{item.detail}</p> : null}
            </article>
          ))}
        </div>
        {divergenceContext.status || divergenceContext.summary || divergenceContext.items.length ? (
          <div
            className="sentiment-workbench__divergence-panel"
            style={{ "--metric-tone": toneColor(divergenceContext.tone) } as React.CSSProperties}
          >
            <div className="sentiment-workbench__divergence-summary">
              {divergenceContext.status ? <strong>{divergenceContext.status}</strong> : null}
              {divergenceContext.summary ? <p>{divergenceContext.summary}</p> : null}
            </div>
            <div className="sentiment-workbench__divergence-axes">
              {payload.interpretation.divergence.items.map((item) => (
                <article
                  className="sentiment-workbench__divergence-axis"
                  key={`${item.label}-${item.direction || ""}`}
                  style={{ "--metric-tone": toneColor(item.tone) } as React.CSSProperties}
                >
                  <span>{item.label}</span>
                  {item.direction_label ? <strong>{item.direction_label}</strong> : null}
                  {item.detail ? <p>{item.detail}</p> : null}
                </article>
              ))}
            </div>
          </div>
        ) : null}
        <div className="sentiment-workbench__analysis-steps">
          {visibleAnalysisSteps.map((step) => (
            <article
              className="sentiment-workbench__analysis-step"
              key={`${step.title}-${step.status || ""}`}
              style={{ "--metric-tone": toneColor(step.tone) } as React.CSSProperties}
            >
              <div className="sentiment-workbench__analysis-title">{step.title}</div>
              {step.status ? <div className="sentiment-workbench__analysis-status">{step.status}</div> : null}
              {step.detail ? <p>{step.detail}</p> : null}
            </article>
          ))}
        </div>
      </section>

      <section className="sentiment-workbench__driver-section">
        <div className="sentiment-workbench__section-heading">
          <span>무엇이 이 심리를 만들었나</span>
          <small>CNN 구성요소 grouping</small>
        </div>
        <div className="sentiment-workbench__driver-lanes">
          {payload.drivers.lanes.map((lane) => (
            <div
              className="sentiment-workbench__driver-lane"
              key={lane.key}
              style={{ "--metric-tone": toneColor(lane.tone) } as React.CSSProperties}
            >
              <div className="sentiment-workbench__driver-lane-header">
                <span>{lane.label}</span>
                <strong>{lane.count}</strong>
              </div>
              <div className="sentiment-workbench__driver-cards">
                {lane.items.map((item) => (
                  <article className="sentiment-workbench__driver-card" key={`${lane.key}-${item.series}`}>
                    <div className="sentiment-workbench__driver-card-top">
                      <span>{item.label_ko || item.series}</span>
                      <strong>{displayValue(item.score)}</strong>
                    </div>
                    {item.rating ? <div className="sentiment-workbench__driver-rating">{item.rating}</div> : null}
                    {item.current_reading ? <p>{item.current_reading}</p> : null}
                  </article>
                ))}
                {lane.items.length === 0 ? (
                  <div className="sentiment-workbench__driver-empty">해당 방향의 구성요소가 없습니다.</div>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="sentiment-workbench__component-section">
        <div className="sentiment-workbench__section-heading">
          <span>CNN 구성요소 상세</span>
          <small>component explanations</small>
        </div>
        <div className="sentiment-workbench__component-list">
          {payload.component_explanations.map((component) => (
            <article
              className="sentiment-workbench__component-item"
              key={component.series}
              style={{ "--metric-tone": toneColor(component.tone) } as React.CSSProperties}
            >
              <div className="sentiment-workbench__component-score">{displayValue(component.score)}</div>
              <div className="sentiment-workbench__component-copy">
                <div className="sentiment-workbench__component-title">
                  <span>{component.label_ko || component.series}</span>
                  {component.rating_label_ko ? <strong>{component.rating_label_ko}</strong> : null}
                </div>
                {component.what_it_checks ? <p>{component.what_it_checks}</p> : null}
                {component.current_reading ? <small>{component.current_reading}</small> : null}
              </div>
            </article>
          ))}
        </div>
      </section>

      {payload.interpretation.component_history.length ? (
        <section className="sentiment-workbench__component-history">
          <div className="sentiment-workbench__section-heading">
            <span>CNN 구성요소 변화</span>
            <small>latest vs previous</small>
          </div>
          <div className="sentiment-workbench__component-history-grid">
            {payload.interpretation.component_history.map((item) => (
              <article
                className="sentiment-workbench__component-history-card"
                key={item.series}
                style={{ "--metric-tone": toneColor(item.tone) } as React.CSSProperties}
              >
                <div className="sentiment-workbench__component-history-title">
                  <span>{item.label_ko || item.series}</span>
                  <strong>{displayValue(item.latest)}</strong>
                </div>
                <div className="sentiment-workbench__component-history-delta">{componentChangeLabel(item)}</div>
                <div className="sentiment-workbench__component-history-dates">
                  <span>{item.previous_date || "-"}</span>
                  <span>{item.latest_date || "-"}</span>
                </div>
                {item.detail ? <p>{item.detail}</p> : null}
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <section className="sentiment-workbench__chart-section">
        <div className="sentiment-workbench__section-heading">
          <span>그래프로 보는 근거</span>
          <small>{payload.charts.history.basis}</small>
        </div>
        <div className="sentiment-workbench__chart-grid">
          <div className="sentiment-workbench__line-chart">
            <div className="sentiment-workbench__chart-title">
              <span>{payload.charts.history.title}</span>
              <strong>{plottableHistory.length}</strong>
            </div>
            <div className="sentiment-workbench__line-chart-plot">
              <svg
                aria-label={payload.charts.history.title}
                onMouseLeave={() => setHoveredHistoryPoint(null)}
                onMouseMove={handleHistoryHover}
                role="img"
                viewBox={`0 0 ${chartWidth} ${chartHeight}`}
              >
                {historyTicks.map((tick) => (
                  <g key={tick.label}>
                    <line
                      className="sentiment-workbench__chart-gridline"
                      x1={chartPaddingX}
                      x2={chartWidth - chartPaddingX}
                      y1={tick.y}
                      y2={tick.y}
                    />
                    <text
                      className="sentiment-workbench__chart-y-label"
                      textAnchor="end"
                      x={chartPaddingX - 8}
                      y={tick.y + 3}
                    >
                      {tick.label}
                    </text>
                  </g>
                ))}
                <line className="sentiment-workbench__chart-axis" x1={chartPaddingX} x2={chartWidth - chartPaddingX} y1={chartHeight - chartPaddingY} y2={chartHeight - chartPaddingY} />
                <line className="sentiment-workbench__chart-axis" x1={chartPaddingX} x2={chartPaddingX} y1={chartPaddingY} y2={chartHeight - chartPaddingY} />
                {historySeriesNames.map((seriesName, seriesIndex) => {
                  const points = plottedHistoryPoints
                    .filter((point) => point.series === seriesName)
                    .map((point) => `${point.x.toFixed(1)},${point.y.toFixed(1)}`)
                    .join(" ");
                  return (
                    <polyline
                      className="sentiment-workbench__chart-line"
                      fill="none"
                      key={seriesName}
                      points={points}
                      stroke={chartPalette[seriesIndex % chartPalette.length]}
                    />
                  );
                })}
                {plottedHistoryPoints.map((point) => (
                  <circle
                    className="sentiment-workbench__chart-point"
                    cx={point.x}
                    cy={point.y}
                    fill={point.color}
                    key={`${point.series}-${point.date}`}
                    r="1.6"
                  />
                ))}
                {hoveredHistoryPoint ? (
                  <>
                    <line
                      className="sentiment-workbench__chart-hover-guide"
                      x1={hoveredHistoryPoint.x}
                      x2={hoveredHistoryPoint.x}
                      y1={chartPaddingY}
                      y2={chartHeight - chartPaddingY}
                    />
                    <circle
                      className="sentiment-workbench__chart-focus-dot"
                      cx={hoveredHistoryPoint.x}
                      cy={hoveredHistoryPoint.y}
                      fill={hoveredHistoryPoint.color}
                      r="4.2"
                    />
                  </>
                ) : null}
              </svg>
              {hoveredHistoryPoint ? (
                <div className="sentiment-workbench__chart-tooltip" style={{ left: tooltipLeft, top: tooltipTop }}>
                  <strong>{hoveredHistoryPoint.date}</strong>
                  <span>{hoveredHistoryPoint.series}</span>
                  <b>{hoveredHistoryPoint.valueLabel}</b>
                  {hoveredHistoryPoint.source ? <small>{hoveredHistoryPoint.source}</small> : null}
                </div>
              ) : null}
            </div>
            <div className="sentiment-workbench__chart-meta">
              <span>{firstHistoryDate}</span>
              <span>{lastHistoryDate}</span>
            </div>
            <div className="sentiment-workbench__chart-legend">
              {historySeriesNames.map((seriesName, seriesIndex) => (
                <span key={seriesName} style={{ "--metric-tone": chartPalette[seriesIndex % chartPalette.length] } as React.CSSProperties}>
                  {seriesName}
                </span>
              ))}
            </div>
          </div>

          <div className="sentiment-workbench__component-bars">
            <div className="sentiment-workbench__chart-title">
              <span>{payload.charts.components.title}</span>
              <strong>{payload.charts.components.items.length}</strong>
            </div>
            <div className="sentiment-workbench__component-bar-list">
              {payload.charts.components.items.map((item) => {
                const score = numericValue(item.score);
                const width = `${Math.max(0, Math.min(100, score ?? 0))}%`;
                return (
                  <div className="sentiment-workbench__component-bar-row" key={item.series}>
                    <div className="sentiment-workbench__component-bar-label">
                      <span>{item.series}</span>
                      <strong>{displayValue(item.score ?? undefined)}</strong>
                    </div>
                    <div className="sentiment-workbench__component-bar-track">
                      <div
                        className="sentiment-workbench__component-bar-fill"
                        style={{
                          "--metric-tone": toneColor(item.tone),
                          width,
                        } as React.CSSProperties}
                      />
                    </div>
                    {item.rating ? <small>{item.rating}</small> : null}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      <section className="sentiment-workbench__evidence-details">
        <div className="sentiment-workbench__section-heading">
          <span>원본 / 상세 근거</span>
          <small>stored rows</small>
        </div>
        {payload.evidence.warnings.length ? (
          <div className="sentiment-workbench__evidence-warnings">
            {payload.evidence.warnings.map((warning) => (
              <span key={warning}>{warning}</span>
            ))}
          </div>
        ) : null}
        <div className="sentiment-workbench__evidence-grid">
          <EvidenceTable rows={payload.evidence.raw_rows} title="Sentiment rows" />
          <EvidenceTable rows={payload.evidence.component_rows} title="Component rows" />
          <EvidenceTable rows={payload.evidence.history_rows} title="History rows" />
        </div>
      </section>
    </section>
  );
}

export default withStreamlitConnection(SentimentWorkbench);
