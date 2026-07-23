import { useMemo, useState } from "react";

import {
  buildChartSeries,
  buildDateTicks,
  buildPercentTicks,
  chartDomains,
  pointCoordinates,
} from "./presentation";
import type { CurveMetadata, PortfolioCurveRow, PortfolioLivePoint } from "./types";

type Props = {
  rows: PortfolioCurveRow[];
  metadata: CurveMetadata;
  livePoint: PortfolioLivePoint | null;
  viewportWidth: number;
};

const WIDTH = 960;
const HEIGHT = 310;
const BOX = { width: WIDTH, height: HEIGHT, left: 78, right: 28, top: 44, bottom: 44 };

function compactDate(value: string | null) {
  if (!value) return "-";
  const parts = value.slice(0, 10).split("-");
  return parts.length === 3 ? `${parts[1]}.${parts[2]}` : value;
}

function fullDate(value: string) {
  return value.slice(0, 10).split("-").join(".");
}

function percentText(value: number | null, digits = 1) {
  if (value == null || !Number.isFinite(value)) return "자료 없음";
  return `${value > 0 ? "+" : ""}${(value * 100).toFixed(digits)}%`;
}

function moneyText(value: number | null) {
  if (value == null || !Number.isFinite(value)) return "평가액 자료 없음";
  return `평가액 ${new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value)}`;
}

export default function TodayPortfolioChart({ rows, metadata, livePoint, viewportWidth }: Props) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const series = useMemo(() => buildChartSeries(rows), [rows]);
  const liveSeriesPoint = useMemo(() => {
    if (!livePoint) return null;
    const timestamp = Date.parse(livePoint.timestamp_utc);
    return Number.isFinite(timestamp) ? { ...livePoint, timestamp } : null;
  }, [livePoint]);
  const domain = useMemo(
    () => chartDomains(liveSeriesPoint ? [...series, liveSeriesPoint] : series),
    [series, liveSeriesPoint],
  );
  const percentTicks = useMemo(() => buildPercentTicks(domain, 5), [domain]);
  const dateTicks = useMemo(
    () => buildDateTicks(series, viewportWidth <= 520 ? 3 : 5),
    [series, viewportWidth],
  );
  const points = useMemo(
    () => series.map((row) => ({ row, ...pointCoordinates(row, domain, BOX) })),
    [series, domain],
  );
  const liveCoordinates = useMemo(
    () => liveSeriesPoint ? pointCoordinates(liveSeriesPoint, domain, BOX) : null,
    [liveSeriesPoint, domain],
  );

  if (series.length < 2) {
    return (
      <section className="today-chart-panel" aria-label="포트폴리오 성과 추이">
        <ChartHeader metadata={metadata} hasLive={liveCoordinates != null} />
        <div className="today-chart-empty">
          <strong>성과 추이를 표시할 관측치가 부족합니다.</strong>
          <span>현재 {metadata.observation_count}개 관측 · 일별 저장 종가 기준</span>
        </div>
      </section>
    );
  }

  const linePath = points.map((point, index) => (
    `${index === 0 ? "M" : "L"}${point.x.toFixed(2)},${point.y.toFixed(2)}`
  )).join(" ");
  const plotBottom = HEIGHT - BOX.bottom;
  const areaPath = `${linePath} L${points[points.length - 1].x.toFixed(2)},${plotBottom} L${points[0].x.toFixed(2)},${plotBottom} Z`;
  const active = activeIndex == null ? null : points[activeIndex] ?? null;
  const tooltipWidth = 190;
  const tooltipHeight = 70;
  const tooltipX = active == null
    ? 0
    : Math.min(Math.max(active.x + 14, BOX.left), WIDTH - BOX.right - tooltipWidth);
  const tooltipY = active == null
    ? 0
    : Math.min(Math.max(active.y - tooltipHeight - 12, BOX.top), plotBottom - tooltipHeight);

  const updateActive = (event: React.PointerEvent<SVGRectElement>) => {
    const svg = event.currentTarget.ownerSVGElement;
    if (!svg) return;
    const bounds = svg.getBoundingClientRect();
    if (!bounds.width) return;
    const pointerX = ((event.clientX - bounds.left) / bounds.width) * WIDTH;
    const targetTime = domain.minTime
      + ((pointerX - BOX.left) / Math.max(WIDTH - BOX.left - BOX.right, 1))
      * (domain.maxTime - domain.minTime);
    const nearest = series.reduce((selected, row, index) => (
      Math.abs(row.timestamp - targetTime) < Math.abs(series[selected].timestamp - targetTime)
        ? index
        : selected
    ), 0);
    setActiveIndex(nearest);
  };

  const zeroY = domain.low <= 0 && domain.high >= 0
    ? pointCoordinates({ ...series[0], cumulative_return: 0 }, domain, BOX).y
    : null;

  return (
    <section className="today-chart-panel" aria-label="포트폴리오 성과 추이">
      <ChartHeader metadata={metadata} hasLive={liveCoordinates != null} />
      <div className="today-chart-shell">
        <svg
          viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
          role="img"
          aria-label={`${metadata.start_date ?? "-"}부터 ${metadata.end_date ?? "-"}까지 일별 종가 기반 누적 수익률`}
        >
          <defs>
            <linearGradient id="todayChartArea" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#72aee6" stopOpacity="0.28" />
              <stop offset="100%" stopColor="#72aee6" stopOpacity="0" />
            </linearGradient>
          </defs>
          <text x={14} y={25} className="today-axis-title">Y축 · 누적 수익률 (%)</text>
          {percentTicks.map((value) => {
            const y = BOX.top + ((domain.high - value) / (domain.high - domain.low)) * (HEIGHT - BOX.top - BOX.bottom);
            return (
              <g key={value}>
                <line x1={BOX.left} x2={WIDTH - BOX.right} y1={y} y2={y} className="today-chart-grid" />
                <text x={BOX.left - 11} y={y + 4} textAnchor="end" className="today-axis-label">{percentText(value)}</text>
              </g>
            );
          })}
          {zeroY != null && <line x1={BOX.left} x2={WIDTH - BOX.right} y1={zeroY} y2={zeroY} className="today-zero-line" />}
          <path d={areaPath} className="today-chart-area" />
          <path d={linePath} className="today-chart-line" />
          {liveCoordinates && points.length > 0 && (
            <g className="today-chart-live">
              <path d={`M${points[points.length - 1].x},${points[points.length - 1].y} L${liveCoordinates.x},${liveCoordinates.y}`} />
              <circle cx={liveCoordinates.x} cy={liveCoordinates.y} r={6} />
              <text x={liveCoordinates.x - 8} y={liveCoordinates.y - 12} textAnchor="end">장중 임시</text>
              <title>{`장중 임시 · ${percentText(livePoint?.cumulative_return ?? null, 2)} · ${moneyText(livePoint?.total_value ?? null)}`}</title>
            </g>
          )}
          {points.map((point, index) => (
            <g
              key={`${point.row.date}-${index}`}
              className="today-chart-point"
              tabIndex={0}
              onFocus={() => setActiveIndex(index)}
              onBlur={() => setActiveIndex(null)}
            >
              <circle cx={point.x} cy={point.y} r={3.5} />
              <title>{`${fullDate(point.row.date)} · ${percentText(point.row.cumulative_return, 2)} · ${moneyText(point.row.total_value)}`}</title>
            </g>
          ))}
          <rect
            x={BOX.left}
            y={BOX.top}
            width={WIDTH - BOX.left - BOX.right}
            height={HEIGHT - BOX.top - BOX.bottom}
            className="today-chart-hit-area"
            onPointerMove={updateActive}
            onPointerLeave={() => setActiveIndex(null)}
          />
          {active && (
            <g className="today-chart-hover" pointerEvents="none">
              <line x1={active.x} x2={active.x} y1={BOX.top} y2={plotBottom} />
              <circle cx={active.x} cy={active.y} r={6} />
              <g transform={`translate(${tooltipX} ${tooltipY})`} className="today-chart-tooltip">
                <rect width={tooltipWidth} height={tooltipHeight} rx={10} />
                <text x={12} y={19} className="today-tooltip-date">{fullDate(active.row.date)} · 저장 종가</text>
                <text x={12} y={41} className="today-tooltip-value">누적 {percentText(active.row.cumulative_return, 2)}</text>
                <text x={12} y={59} className="today-tooltip-sub">{moneyText(active.row.total_value)}</text>
              </g>
            </g>
          )}
          {dateTicks.map((tick, index) => {
            const { x } = pointCoordinates(tick, domain, BOX);
            return (
              <text
                key={tick.date}
                x={x}
                y={HEIGHT - 18}
                textAnchor={index === 0 ? "start" : index === dateTicks.length - 1 ? "end" : "middle"}
                className="today-axis-label"
              >{compactDate(tick.date)}</text>
            );
          })}
          <text x={WIDTH / 2} y={HEIGHT - 3} textAnchor="middle" className="today-axis-title">X축 · 저장 관측일</text>
        </svg>
      </div>
      <footer className="today-chart-footer">
        <span><strong>기간</strong> {metadata.start_date?.split("-").join(".") ?? "-"}–{metadata.end_date?.split("-").join(".") ?? "-"}</span>
        <span><strong>정의</strong> 확정 종가 곡선{liveCoordinates ? " + 장중 임시 점" : " · 장중 데이터 없음"}</span>
      </footer>
    </section>
  );
}

function ChartHeader({ metadata, hasLive }: { metadata: CurveMetadata; hasLive: boolean }) {
  return (
    <header className="today-chart-header">
      <div>
        <span>PERFORMANCE TREND</span>
        <h3>일별 종가 기반 누적 수익률</h3>
        <p>입출금 영향을 조정한 포트폴리오 단위가치의 변화{hasLive ? "와 장중 임시 값" : ""}입니다.</p>
      </div>
      <div className="today-chart-chips">
        <b>주기 · 일별</b>
        <b>최근 {metadata.observation_count}관측</b>
        <b className={hasLive ? "is-live" : "is-limit"}>{hasLive ? "장중 임시" : "장중 아님"}</b>
      </div>
    </header>
  );
}
