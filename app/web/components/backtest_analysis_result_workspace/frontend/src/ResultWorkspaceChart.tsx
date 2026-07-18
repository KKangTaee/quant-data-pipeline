import React from "react"
import { CurvePoint, ResultWorkspace } from "./types"

type ChartModel = ResultWorkspace["chart"]

const WIDTH = 960
const HEIGHT = 360
const PADDING = { top: 32, right: 28, bottom: 48, left: 58 }

function pathFor(points: CurvePoint[], x: (index: number) => number, y: (value: number) => number) {
  return points
    .map((point, index) => `${index === 0 ? "M" : "L"}${x(index)},${y(point.value)}`)
    .join(" ")
}

export function ResultWorkspaceChart({ chart }: { chart: ChartModel }) {
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
  const pointCount = Math.max(chart.strategy_series.length, chart.benchmark_series.length)
  const x = (index: number) =>
    PADDING.left +
    (index / Math.max(pointCount - 1, 1)) * (WIDTH - PADDING.left - PADDING.right)
  const y = (value: number) =>
    PADDING.top +
    ((maximum - value) / span) * (HEIGHT - PADDING.top - PADDING.bottom)
  const strategyPath = pathFor(chart.strategy_series, x, y)
  const benchmarkPath = pathFor(chart.benchmark_series, x, y)

  return (
    <section className="bt1r-section">
      <div className="bt1r-section-heading">
        <span>2</span>
        <div>
          <h2>전략과 기준의 흐름</h2>
          <p>첫 공통 시점을 100으로 맞춘 비용 반영 성과 흐름입니다.</p>
        </div>
      </div>
      <div className="bt1r-chart-shell">
        <div className="bt1r-chart-legend" aria-label="차트 범례">
          <span className="is-strategy">전략</span>
          {chart.benchmark_series.length > 0 && <span className="is-benchmark">기준지수</span>}
        </div>
        <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label="전략과 기준지수의 정규화 성과 차트">
          <title id="bt1r-chart-title">전략과 기준지수의 정규화 성과 차트</title>
          <desc>전략과 기준지수를 첫 공통 시점 100으로 비교하고 최고, 최저, 최대 낙폭 지점을 표시합니다.</desc>
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
          <path className="bt1r-line is-strategy" d={strategyPath} />
          {benchmarkPath && <path className="bt1r-line is-benchmark" d={benchmarkPath} />}
          {chart.strategy_series.map((point, index) => (
            <circle className="bt1r-point is-strategy" cx={x(index)} cy={y(point.value)} r="4" key={`strategy-${point.date}`} tabIndex={0}>
              <title>{`전략 ${point.date}: ${point.value_label}`}</title>
            </circle>
          ))}
          {chart.benchmark_series.map((point, index) => (
            <circle className="bt1r-point is-benchmark" cx={x(index)} cy={y(point.value)} r="4" key={`benchmark-${point.date}`} tabIndex={0}>
              <title>{`기준지수 ${point.date}: ${point.value_label}`}</title>
            </circle>
          ))}
        </svg>
        {chart.markers.length > 0 && (
          <div className="bt1r-marker-strip">
            {chart.markers.map((marker) => (
              <span key={marker.marker_id}><strong>{marker.label}</strong>{marker.date} · {marker.drawdown_label || marker.value_label}</span>
            ))}
          </div>
        )}
        {chart.benchmark_missing_reason && <p className="bt1r-inline-note">{chart.benchmark_missing_reason}</p>}
      </div>
    </section>
  )
}
