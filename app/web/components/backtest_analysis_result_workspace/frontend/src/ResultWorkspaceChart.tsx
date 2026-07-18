import React, { useState } from "react"
import { CurvePoint, ResultWorkspace } from "./types"

type ChartModel = ResultWorkspace["chart"]

const WIDTH = 960
const HEIGHT = 360
const PADDING = { top: 32, right: 28, bottom: 58, left: 58 }

function pathFor(
  points: CurvePoint[],
  xForDate: (date: string) => number,
  y: (value: number) => number,
) {
  return points
    .map((point, index) => `${index === 0 ? "M" : "L"}${xForDate(point.date)},${y(point.value)}`)
    .join(" ")
}

export function ResultWorkspaceChart({ chart }: { chart: ChartModel }) {
  const [hoveredDate, setHoveredDate] = useState<string | null>(null)
  const combined = [...chart.strategy_series, ...chart.benchmark_series]
  if (!combined.length) {
    return (
      <section className="bt1r-section bt1r-chart-empty">
        <div className="bt1r-section-heading">
          <span>2</span>
          <div><h2>전략과 기준의 흐름</h2><p>표시 가능한 성과 곡선이 없습니다.</p></div>
        </div>
      </section>
    )
  }

  const values = combined.map((point) => point.value)
  const minimum = Math.min(...values)
  const maximum = Math.max(...values)
  const span = Math.max(maximum - minimum, 1)
  const timelineIndex = new Map(chart.timeline_dates.map((date, index) => [date, index]))
  const xForDate = (date: string) => {
    const index = timelineIndex.get(date) ?? 0
    return PADDING.left +
      (index / Math.max(chart.timeline_dates.length - 1, 1)) *
        (WIDTH - PADDING.left - PADDING.right)
  }
  const y = (value: number) =>
    PADDING.top +
    ((maximum - value) / span) * (HEIGHT - PADDING.top - PADDING.bottom)
  const strategyPath = pathFor(chart.strategy_series, xForDate, y)
  const benchmarkPath = pathFor(chart.benchmark_series, xForDate, y)
  const handlePointerMove = (event: React.PointerEvent<SVGSVGElement>) => {
    if (!chart.hover_rows.length) return
    const bounds = event.currentTarget.getBoundingClientRect()
    const pointer =
      ((event.clientX - bounds.left) / Math.max(bounds.width, 1)) * WIDTH
    const nearest = chart.hover_rows.reduce((best, row) =>
      Math.abs(xForDate(row.date) - pointer) <
      Math.abs(xForDate(best.date) - pointer) ? row : best,
    )
    setHoveredDate(nearest.date)
  }
  const hovered = chart.hover_rows.find((row) => row.date === hoveredDate) ?? null
  const hoveredX = hovered ? xForDate(hovered.date) : 0
  const tooltipLeft = `${Math.min(88, Math.max(12, (hoveredX / WIDTH) * 100))}%`

  const renderTicks = (
    ticks: ChartModel["desktop_x_ticks"],
    className: string,
  ) => (
    <g className={className} aria-hidden="true">
      {ticks.map((tick) => (
        <g key={tick.date}>
          <line
            className="bt1r-x-tick"
            x1={xForDate(tick.date)}
            x2={xForDate(tick.date)}
            y1={HEIGHT - PADDING.bottom}
            y2={HEIGHT - PADDING.bottom + 6}
          />
          <text
            className="bt1r-axis-label"
            x={xForDate(tick.date)}
            y={HEIGHT - PADDING.bottom + 24}
            textAnchor="middle"
          >
            {tick.label}
          </text>
        </g>
      ))}
    </g>
  )

  return (
    <section className="bt1r-section">
      <div className="bt1r-section-heading">
        <span>2</span>
        <div>
          <h2>전략과 기준의 흐름</h2>
          <p>{chart.normalized_explanation}</p>
        </div>
      </div>
      <div className="bt1r-chart-shell">
        <div className="bt1r-chart-legend" aria-label="차트 범례">
          <span className="is-strategy">{chart.strategy_label}</span>
          {chart.benchmark.available && (
            <span className="is-benchmark">
              {chart.benchmark.label}
              {chart.benchmark.contract_label && chart.benchmark.contract_label !== chart.benchmark.label && (
                <small>{chart.benchmark.contract_label}</small>
              )}
            </span>
          )}
        </div>
        <div className="bt1r-chart-stage">
          <svg
            viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
            role="img"
            aria-label="전략과 기준지수의 정규화 성과 차트"
            onPointerMove={handlePointerMove}
            onPointerLeave={() => setHoveredDate(null)}
          >
            <title>전략과 기준지수의 정규화 성과 차트</title>
            <desc>전략과 기준지수를 시작 지수 100으로 비교하며 실제 날짜와 누적 수익을 포인터 위치에서 확인합니다.</desc>
            <rect
              className="bt1r-pointer-capture"
              x={PADDING.left}
              y={PADDING.top}
              width={WIDTH - PADDING.left - PADDING.right}
              height={HEIGHT - PADDING.top - PADDING.bottom}
            />
            {[0, 1, 2, 3, 4].map((tick) => {
              const value = maximum - (span * tick) / 4
              const position = y(value)
              return (
                <g key={tick}>
                  <line className="bt1r-grid-line" x1={PADDING.left} x2={WIDTH - PADDING.right} y1={position} y2={position} />
                  <text className="bt1r-axis-label" x={PADDING.left - 10} y={position + 4} textAnchor="end">{value.toFixed(1)}</text>
                </g>
              )
            })}
            {renderTicks(chart.desktop_x_ticks, "bt1r-x-ticks is-desktop")}
            {renderTicks(chart.compact_x_ticks, "bt1r-x-ticks is-compact")}
            <path className="bt1r-line is-strategy" d={strategyPath} />
            {benchmarkPath && <path className="bt1r-line is-benchmark" d={benchmarkPath} />}
            {hovered && (
              <line
                className="bt1r-crosshair"
                x1={hoveredX}
                x2={hoveredX}
                y1={PADDING.top}
                y2={HEIGHT - PADDING.bottom}
              />
            )}
            {chart.strategy_series.map((point) => (
              <circle className="bt1r-point is-strategy" cx={xForDate(point.date)} cy={y(point.value)} r="4" key={`strategy-${point.date}`} tabIndex={0}>
                <title>{`${chart.strategy_label} ${point.date}: ${point.value_label}`}</title>
              </circle>
            ))}
            {chart.benchmark_series.map((point) => (
              <circle className="bt1r-point is-benchmark" cx={xForDate(point.date)} cy={y(point.value)} r="4" key={`benchmark-${point.date}`} tabIndex={0}>
                <title>{`${chart.benchmark.label} ${point.date}: ${point.value_label}`}</title>
              </circle>
            ))}
          </svg>
          {hovered && (
            <div
              className="bt1r-chart-tooltip"
              style={{ left: tooltipLeft }}
              role="status"
              aria-live="polite"
            >
              <strong>{hovered.date}</strong>
              <span>{chart.strategy_label} {hovered.strategy_value_label} · {hovered.strategy_return_label}</span>
              {chart.benchmark.available && (
                <span>{chart.benchmark.label} {hovered.benchmark_value_label} · {hovered.benchmark_return_label}</span>
              )}
            </div>
          )}
        </div>
        {chart.markers.length > 0 && (
          <div className="bt1r-marker-strip">
            {chart.markers.map((marker) => (
              <span key={marker.marker_id}><strong>{marker.label}</strong>{marker.date} · {marker.drawdown_label || marker.value_label}</span>
            ))}
          </div>
        )}
        {chart.benchmark.missing_reason && <p className="bt1r-inline-note">{chart.benchmark.missing_reason}</p>}
      </div>
    </section>
  )
}
