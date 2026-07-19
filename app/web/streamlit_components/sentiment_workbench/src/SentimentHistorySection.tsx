import React, { useState } from "react";
import { displayValue } from "./SentimentWorkbench";
import type { ChartPanel, ChartPoint } from "./SentimentWorkbench";

type AaiiHistoryTab = "responses" | "spread";
type ChartMode = "cnn" | "aaii_responses" | "aaii_spread";

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

const chartWidth = 960;
const chartHeight = 360;
const chartMargin = { top: 28, right: 28, bottom: 46, left: 56 };
const plotWidth = chartWidth - chartMargin.left - chartMargin.right;
const plotHeight = chartHeight - chartMargin.top - chartMargin.bottom;
const spreadGuideValues = [-10, 0, 10];

function numericValue(value: ChartPoint["value"]) {
  if (value === undefined || value === null || value === "") return null;
  const parsed = typeof value === "number" ? value : Number.parseFloat(String(value));
  return Number.isFinite(parsed) ? parsed : null;
}

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

function chartSeriesColor(series: string, mode: ChartMode) {
  if (mode === "cnn") return "#9a6a44";
  const normalized = series.toLowerCase();
  if (normalized.includes("bullish")) return "#0f766e";
  if (normalized.includes("bearish")) return "#a14f61";
  if (normalized.includes("neutral")) return "#64748b";
  return "#0f766e";
}

function chartSeriesDash(series: string) {
  const normalized = series.toLowerCase();
  if (normalized.includes("neutral")) return "8 6";
  if (normalized.includes("bearish")) return "3 6";
  return undefined;
}

function chartValueSuffix(panel: ChartPanel) {
  if (panel.unit === "percent") return "%";
  if (panel.unit === "percentage_point") return "pp";
  return "";
}

function SentimentLineChart({ panel, mode }: { panel: ChartPanel; mode: ChartMode }) {
  const points = parsedChartPoints(panel);
  const extent = chartExtent(points);
  const domain = chartDomain(panel, points);
  const [hoveredChartPoint, setHoveredChartPoint] = useState<HoveredChartPoint | null>(null);
  const grouped = points.reduce<Record<string, ParsedChartPoint[]>>((result, point) => {
    (result[point.series] ||= []).push(point);
    return result;
  }, {});
  const uniqueDateCount = new Set(points.map((point) => point.timestamp)).size;
  const hasTrend = uniqueDateCount >= 2;
  const dateTicks = buildDateTicks(extent);
  const yTicks = panel.unit === "percentage_point"
    ? [domain.min, domain.min / 2, 0, domain.max / 2, domain.max]
    : [0, 25, 50, 75, 100];
  const guides = mode === "aaii_spread" ? spreadGuideValues : [];

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
    <article className="sentiment-workbench__line-chart">
      <header className="sentiment-workbench__chart-title">
        <div><strong>{panel.title}</strong><small>{panel.basis}</small></div>
        <div className="sentiment-workbench__chart-latest">
          {panel.latest ? <><span>{panel.latest.label}</span><b>{displayValue(panel.latest.value, chartValueSuffix(panel))}</b><small>{panel.latest.date}</small></> : null}
        </div>
      </header>
      {hasTrend ? (
        <div className="sentiment-workbench__line-chart-plot">
          <svg
            aria-label="심리 근거 그래프"
            onMouseLeave={() => setHoveredChartPoint(null)}
            onMouseMove={handleChartHover}
            role="img"
            viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          >
            <title>{panel.title} · {uniqueDateCount}개 시점</title>
            {mode === "cnn" ? (
              <g aria-hidden="true">
                <rect className="sentiment-workbench__chart-band sentiment-workbench__chart-band--fear" height={yForValue(25, domain) - yForValue(45, domain)} width={plotWidth} x={chartMargin.left} y={yForValue(45, domain)} />
                <rect className="sentiment-workbench__chart-band sentiment-workbench__chart-band--extreme-fear" height={yForValue(0, domain) - yForValue(25, domain)} width={plotWidth} x={chartMargin.left} y={yForValue(25, domain)} />
                <rect className="sentiment-workbench__chart-band sentiment-workbench__chart-band--greed" height={yForValue(55, domain) - yForValue(75, domain)} width={plotWidth} x={chartMargin.left} y={yForValue(75, domain)} />
                <rect className="sentiment-workbench__chart-band sentiment-workbench__chart-band--extreme-greed" height={yForValue(75, domain) - yForValue(100, domain)} width={plotWidth} x={chartMargin.left} y={yForValue(100, domain)} />
              </g>
            ) : null}
            {yTicks.map((tick) => {
              const y = yForValue(tick, domain);
              return <g key={`y-${tick}`}><line className="sentiment-workbench__chart-gridline" x1={chartMargin.left} x2={chartWidth - chartMargin.right} y1={y} y2={y} /><text className="sentiment-workbench__chart-y-label" textAnchor="end" x={chartMargin.left - 9} y={y + 4}>{tick}</text></g>;
            })}
            {guides.map((guide) => <line className={`sentiment-workbench__chart-guide${guide === 0 ? " sentiment-workbench__chart-guide--zero" : ""}`} key={`guide-${guide}`} x1={chartMargin.left} x2={chartWidth - chartMargin.right} y1={yForValue(guide, domain)} y2={yForValue(guide, domain)} />)}
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
                stroke={chartSeriesColor(series, mode)}
                strokeDasharray={chartSeriesDash(series)}
              />
            ))}
            {hoveredChartPoint ? (
              <g aria-hidden="true">
                <line className="sentiment-workbench__chart-hover-guide" x1={hoveredChartPoint.x} x2={hoveredChartPoint.x} y1={chartMargin.top} y2={chartHeight - chartMargin.bottom} />
                {hoveredChartPoint.values.map((point) => <circle className="sentiment-workbench__chart-focus-dot" cx={hoveredChartPoint.x} cy={yForValue(point.numericValue, domain)} fill={chartSeriesColor(point.series, mode)} key={`${point.series}-${point.timestamp}`} r={5} />)}
              </g>
            ) : null}
          </svg>
          {hoveredChartPoint ? (
            <div className="sentiment-workbench__chart-tooltip" style={{ left: `${(hoveredChartPoint.x / chartWidth) * 100}%` }}>
              <strong>{hoveredChartPoint.date}</strong>
              {hoveredChartPoint.values.map((point) => <span key={`${point.series}-tooltip`}><i style={{ background: chartSeriesColor(point.series, mode) }} />{point.series}<b>{displayValue(point.numericValue, chartValueSuffix(panel))}</b>{point.status_label ? <small>{point.status_label}</small> : null}</span>)}
            </div>
          ) : null}
        </div>
      ) : <p className="sentiment-workbench__empty">추이를 그리려면 서로 다른 두 시점 이상의 관측이 필요합니다.</p>}
      <div className="sentiment-workbench__chart-legend">
        {Object.keys(grouped).map((series) => <span key={series}><i style={{ background: chartSeriesColor(series, mode) }} />{series}</span>)}
        {mode === "aaii_spread" ? <small>기준선: -10 / 0 / +10pp · 0은 실선</small> : null}
      </div>
    </article>
  );
}

type Props = {
  charts: {
    cnn: ChartPanel;
    aaii_responses: ChartPanel;
    aaii_spread: ChartPanel;
  };
};

function SentimentHistorySection({ charts }: Props) {
  const [aaiiTab, setAaiiTab] = useState<AaiiHistoryTab>("responses");
  const tabs: AaiiHistoryTab[] = ["responses", "spread"];
  const handleAaiiTabKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
    event.preventDefault();
    const offset = event.key === "ArrowRight" ? 1 : -1;
    const nextIndex = (tabs.indexOf(aaiiTab) + offset + tabs.length) % tabs.length;
    setAaiiTab(tabs[nextIndex]);
  };
  const activeAaiiChart = aaiiTab === "responses" ? charts.aaii_responses : charts.aaii_spread;
  const activeAaiiMode = aaiiTab === "responses" ? "aaii_responses" : "aaii_spread";

  return (
    <section className="sentiment-workbench__chart-section" aria-labelledby="sentiment-history-title">
      <div className="sentiment-workbench__section-heading"><div><span>History</span><h3 id="sentiment-history-title">두 소스의 변화 경로</h3></div><small>곡선 보정 없이 관측점을 직선으로 연결</small></div>
      <div className="sentiment-workbench__history-grid">
        <div aria-label="CNN 시장 행동 그래프">
          <SentimentLineChart mode="cnn" panel={charts.cnn} />
        </div>
        <div className="sentiment-workbench__aaii-history">
          <div className="sentiment-workbench__chart-tabs" role="tablist" aria-label="AAII 그래프 보기">
            {tabs.map((key) => (
              <button
                aria-controls="sentiment-aaii-chart-panel"
                aria-selected={aaiiTab === key}
                className={aaiiTab === key ? "is-active" : ""}
                id={`sentiment-aaii-chart-tab-${key}`}
                key={key}
                onClick={() => setAaiiTab(key)}
                onKeyDown={handleAaiiTabKeyDown}
                role="tab"
                tabIndex={aaiiTab === key ? 0 : -1}
                type="button"
              >
                {key === "responses" ? "AAII 응답" : "AAII Spread"}
              </button>
            ))}
          </div>
          <div aria-labelledby={`sentiment-aaii-chart-tab-${aaiiTab}`} id="sentiment-aaii-chart-panel" role="tabpanel">
            <SentimentLineChart mode={activeAaiiMode} panel={activeAaiiChart} />
          </div>
        </div>
      </div>
    </section>
  );
}

export default SentimentHistorySection;
