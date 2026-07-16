import React, { useEffect, useId, useState } from "react"
import {
  DecisionBriefSeries,
  SeriesPoint,
  TraitAxis,
} from "./decisionBriefTypes"

type LineSeries = {
  label: string
  color: string
  points: SeriesPoint[]
}

type ChartUnit = "index" | "percent"

const CHART = { width: 720, height: 300, left: 58, right: 16, top: 20, bottom: 44 }
const plotWidth = CHART.width - CHART.left - CHART.right
const plotBottom = CHART.height - CHART.bottom
const plotHeight = plotBottom - CHART.top

function niceExtent(values: number[], unit: ChartUnit): [number, number] {
  if (!values.length) return unit === "percent" ? [-5, 0] : [0, 100]
  const rawMin = unit === "percent" ? Math.min(...values, 0) : Math.min(...values)
  const rawMax = unit === "percent" ? 0 : Math.max(...values)
  if (rawMin === rawMax) return unit === "percent" ? [rawMin - 1, 0] : [rawMin - 1, rawMax + 1]
  const roughStep = Math.max(.01, (rawMax - rawMin) / 4)
  const magnitude = 10 ** Math.floor(Math.log10(roughStep))
  const normalized = roughStep / magnitude
  const step = (normalized <= 1.5 ? 1 : normalized <= 3 ? 2 : normalized <= 7 ? 5 : 10) * magnitude
  return [
    Math.floor(rawMin / step) * step,
    unit === "percent" ? 0 : Math.ceil(rawMax / step) * step,
  ]
}

function buildTickIndices(count: number, maximumTicks = 6): number[] {
  if (count <= 0) return []
  const tickCount = Math.min(count, maximumTicks)
  return Array.from(new Set(Array.from({ length: tickCount }, (_, index) =>
    Math.round(index * (count - 1) / Math.max(1, tickCount - 1)),
  )))
}

function buildYTicks(minimum: number, maximum: number, count = 5): number[] {
  return Array.from({ length: count }, (_, index) =>
    maximum - index * (maximum - minimum) / Math.max(1, count - 1),
  )
}

function xAt(index: number, count: number): number {
  return count <= 1
    ? CHART.left + plotWidth / 2
    : CHART.left + index / (count - 1) * plotWidth
}

function yAt(value: number, minimum: number, maximum: number): number {
  return plotBottom - (value - minimum) / Math.max(.0001, maximum - minimum) * plotHeight
}

function linePath(points: SeriesPoint[], minimum: number, maximum: number): string {
  return points.map((point, index) =>
    `${index ? "L" : "M"} ${xAt(index, points.length).toFixed(2)} ${yAt(point.value, minimum, maximum).toFixed(2)}`,
  ).join(" ")
}

function pointerIndex(event: React.PointerEvent<SVGSVGElement>, count: number): number {
  if (count <= 1) return 0
  const rect = event.currentTarget.getBoundingClientRect()
  const cursor = (event.clientX - rect.left) / Math.max(1, rect.width) * CHART.width
  const ratio = Math.max(0, Math.min(1, (cursor - CHART.left) / plotWidth))
  return Math.round(ratio * (count - 1))
}

function formatChartValue(value: number | undefined, unit: ChartUnit): string {
  if (value == null || !Number.isFinite(value)) return "-"
  const formatted = Math.abs(value) >= 100 ? value.toFixed(0) : value.toFixed(2)
  return unit === "percent" ? `${formatted}%` : formatted
}

function EvidenceTable({ series }: { series: LineSeries[] }) {
  const dates = series[0]?.points.map((point) => point.date) ?? []
  return (
    <details className="db-chart-table">
      <summary>수치 표로 보기</summary>
      <div className="db-table-scroll">
        <table>
          <thead>
            <tr>
              <th>기준일</th>
              {series.map((item) => <th key={item.label}>{item.label}</th>)}
            </tr>
          </thead>
          <tbody>
            {dates.map((date, index) => (
              <tr key={`${date}-${index}`}>
                <td>{date}</td>
                {series.map((item) => (
                  <td key={item.label}>{item.points[index]?.value?.toFixed(2) ?? "-"}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  )
}

function SvgLineChart({
  title,
  subtitle,
  description,
  unit,
  series,
}: {
  title: string
  subtitle: string
  description: string
  unit: ChartUnit
  series: LineSeries[]
}) {
  const chartId = useId()
  const pointCount = series[0]?.points.length ?? 0
  const [activeIndex, setActiveIndex] = useState(Math.max(0, pointCount - 1))
  useEffect(() => setActiveIndex(Math.max(0, pointCount - 1)), [pointCount])
  const safeIndex = Math.min(activeIndex, Math.max(0, pointCount - 1))
  const values = series.flatMap((item) => item.points.map((point) => point.value))
  const [minY, maxY] = niceExtent(values, unit)
  const yTicks = buildYTicks(minY, maxY)
  const xTickIndices = buildTickIndices(pointCount)
  const activeX = xAt(safeIndex, pointCount)
  const activeDate = series[0]?.points[safeIndex]?.date ?? "-"
  const tooltipRight = activeX > CHART.width * .68
  const tooltipStyle = { left: `${activeX / CHART.width * 100}%` }

  return (
    <div className="db-chart-shell">
      <div className="db-chart-heading">
        <div>
          <p className="db-kicker">Portfolio behavior</p>
          <h3>{title}</h3>
          <p className="db-chart-subtitle">{subtitle}</p>
        </div>
        <div className="db-legend" aria-label="차트 범례">
          {series.map((item) => (
            <span key={item.label}><i style={{ background: item.color }} />{item.label}</span>
          ))}
        </div>
      </div>
      <div className="db-chart-plot">
        <svg
          className="db-line-chart"
          viewBox={`0 0 ${CHART.width} ${CHART.height}`}
          role="img"
          aria-labelledby={`${chartId}-title ${chartId}-desc`}
          onPointerMove={(event) => setActiveIndex(pointerIndex(event, pointCount))}
          onPointerLeave={() => setActiveIndex(Math.max(0, pointCount - 1))}
        >
          <title id={`${chartId}-title`}>{title}</title>
          <desc id={`${chartId}-desc`}>{description}</desc>
          {yTicks.map((value) => {
            const y = yAt(value, minY, maxY)
            return (
              <g key={value}>
                <line x1={CHART.left} x2={CHART.width - CHART.right} y1={y} y2={y} className="db-grid-line" />
                <text x={CHART.left - 10} y={y + 4} textAnchor="end" className="db-chart-y-label">
                  {formatChartValue(value, unit)}
                </text>
              </g>
            )
          })}
          {xTickIndices.map((index) => (
            <text key={index} x={xAt(index, pointCount)} y={CHART.height - 12} textAnchor="middle" className="db-chart-x-label">
              {series[0]?.points[index]?.date ?? "-"}
            </text>
          ))}
          {series.map((item) => (
            <path
              key={item.label}
              d={linePath(item.points, minY, maxY)}
              fill="none"
              stroke={item.color}
              strokeWidth="2"
              vectorEffect="non-scaling-stroke"
            />
          ))}
          <line className="db-chart-hover-rule" x1={activeX} x2={activeX} y1={CHART.top} y2={plotBottom} />
          {series.map((item) => {
            const point = item.points[safeIndex]
            return point ? (
              <circle
                key={item.label}
                className="db-chart-focus-dot"
                cx={activeX}
                cy={yAt(point.value, minY, maxY)}
                r="4"
                style={{ fill: item.color }}
              />
            ) : null
          })}
        </svg>
        <div className={`db-chart-tooltip ${tooltipRight ? "is-right" : ""}`} style={tooltipStyle}>
          <span>{activeDate}</span>
          {series.map((item) => (
            <div key={item.label}>
              <i style={{ background: item.color }} />
              <small>{item.label}</small>
              <strong>{formatChartValue(item.points[safeIndex]?.value, unit)}</strong>
            </div>
          ))}
        </div>
      </div>
      <EvidenceTable series={series} />
    </div>
  )
}

function MissingChart({ title, reason }: { title: string; reason: string }) {
  return (
    <div className="db-chart-shell db-chart-shell--missing" role="status">
      <p className="db-kicker">미측정</p>
      <h3>{title}</h3>
      <p>{reason}</p>
    </div>
  )
}

export function CumulativeComparisonChart({
  candidate,
  benchmark,
}: {
  candidate: DecisionBriefSeries
  benchmark: DecisionBriefSeries
}) {
  if (candidate.status !== "measured" || benchmark.status !== "measured") {
    return (
      <MissingChart
        title="누적 성과와 Benchmark"
        reason={candidate.missing_reason || benchmark.missing_reason || "공통 기간 curve가 없습니다."}
      />
    )
  }
  return (
    <SvgLineChart
      title="누적 성과와 Benchmark"
      subtitle="100은 관측 시작일의 기준값입니다. 같은 날짜의 후보와 Benchmark 경로를 비교합니다."
      description="Python에서 같은 날짜로 정렬하고 100 기준으로 전달한 후보와 benchmark 누적 성과입니다."
      unit="index"
      series={[
        { label: candidate.label, color: "#274764", points: candidate.points },
        { label: benchmark.label, color: "#269789", points: benchmark.points },
      ]}
    />
  )
}

export function UnderwaterChart({ series }: { series: DecisionBriefSeries }) {
  if (series.status !== "measured") {
    return <MissingChart title="고점 대비 낙폭 (Underwater)" reason={series.missing_reason || "낙폭 curve가 없습니다."} />
  }
  return (
    <SvgLineChart
      title="고점 대비 낙폭 (Underwater)"
      subtitle="0%는 이전 최고점 회복, 음수는 최고점 대비 하락률입니다."
      description="Python이 running peak 기준으로 계산해 전달한 drawdown과 recovery 경로입니다."
      unit="percent"
      series={[{ label: series.label, color: "#e2763b", points: series.points }]}
    />
  )
}

export function splitMeasuredSegments(axes: TraitAxis[]): TraitAxis[][] {
  const segments: TraitAxis[][] = []
  let current: TraitAxis[] = []
  axes.forEach((axis) => {
    const measured = axis.status === "measured" && axis.normalized_value !== null
    if (measured) {
      current.push(axis)
    } else {
      if (current.length >= 2) segments.push(current)
      current = []
    }
  })
  if (current.length >= 2) segments.push(current)
  const allMeasured = axes.length > 2 && axes.every(
    (axis) => axis.status === "measured" && axis.normalized_value !== null,
  )
  if (allMeasured) return [[...axes, axes[0]]]
  const first = axes[0]
  const last = axes.at(-1)
  if (
    first && last
    && first.status === "measured" && first.normalized_value !== null
    && last.status === "measured" && last.normalized_value !== null
  ) {
    segments.push([last, first])
  }
  return segments
}

function traitPoint(axis: TraitAxis, index: number, count: number, radius = 82) {
  if (axis.normalized_value === null) return null
  const angle = -Math.PI / 2 + (index / count) * Math.PI * 2
  const distance = (axis.normalized_value / 100) * radius
  return {
    x: 120 + Math.cos(angle) * distance,
    y: 120 + Math.sin(angle) * distance,
  }
}

function traitLabelPoint(index: number, count: number) {
  const angle = -Math.PI / 2 + (index / count) * Math.PI * 2
  return {
    x: 120 + Math.cos(angle) * 104,
    y: 120 + Math.sin(angle) * 104,
  }
}

export function PortfolioTraitMap({ axes }: { axes: TraitAxis[] }) {
  const segments = splitMeasuredSegments(axes)
  const indexForAxis = (axis: TraitAxis) => axes.findIndex((candidate) => candidate.axis_id === axis.axis_id)

  return (
    <div className="db-trait-layout">
      <div className="db-trait-copy">
        <p className="db-kicker">Pressure / exposure</p>
        <h3>Portfolio trait map</h3>
        <p>바깥쪽은 더 좋다는 뜻이 아닙니다. 저장된 review 기준 대비 부담이 커지는 방향입니다.</p>
      </div>
      <svg className="db-trait-chart" viewBox="0 0 240 240" role="img" aria-label="측정된 pressure와 미측정 axis를 구분한 포트폴리오 성격 지도">
        {[0.25, 0.5, 0.75, 1].map((ratio) => (
          <circle key={ratio} cx="120" cy="120" r={82 * ratio} className="db-trait-grid" />
        ))}
        {axes.map((axis, index) => {
          const label = traitLabelPoint(index, axes.length)
          return (
            <g key={axis.axis_id}>
              <line x1="120" y1="120" x2={label.x} y2={label.y} className="db-trait-axis" />
              <text x={label.x} y={label.y} className="db-trait-label" textAnchor={label.x < 110 ? "end" : label.x > 130 ? "start" : "middle"}>
                {axis.label}
              </text>
              {axis.status === "unmeasured" && (
                <text x={label.x} y={label.y + 12} className="db-trait-missing" textAnchor={label.x < 110 ? "end" : label.x > 130 ? "start" : "middle"}>
                  미측정
                </text>
              )}
            </g>
          )
        })}
        {segments.map((segment, segmentIndex) => {
          const path = segment
            .map((axis, itemIndex) => {
              const point = traitPoint(axis, indexForAxis(axis), axes.length)
              return point ? `${itemIndex === 0 ? "M" : "L"} ${point.x.toFixed(2)} ${point.y.toFixed(2)}` : ""
            })
            .filter(Boolean)
            .join(" ")
          return <path key={`${segmentIndex}-${path}`} d={path} className="db-trait-segment" />
        })}
      </svg>
      <ul className="db-trait-list">
        {axes.map((axis) => (
          <li key={axis.axis_id}>
            <span>{axis.label}</span>
            <strong>{axis.status === "measured" ? `${axis.normalized_value?.toFixed(1)} / 100` : "미측정"}</strong>
          </li>
        ))}
      </ul>
    </div>
  )
}
