import React, { useId } from "react"
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

function extent(values: number[]): [number, number] {
  if (values.length === 0) return [0, 1]
  const minimum = Math.min(...values)
  const maximum = Math.max(...values)
  if (minimum === maximum) return [minimum - 1, maximum + 1]
  const padding = Math.max((maximum - minimum) * 0.12, 0.5)
  return [minimum - padding, maximum + padding]
}

function linePath(points: SeriesPoint[], minY: number, maxY: number): string {
  if (points.length === 0) return ""
  return points
    .map((point, index) => {
      const x = points.length === 1 ? 50 : 8 + (index / (points.length - 1)) * 84
      const y = 88 - ((point.value - minY) / (maxY - minY)) * 72
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`
    })
    .join(" ")
}

function formatAxisValue(value: number): string {
  const magnitude = Math.abs(value)
  return magnitude >= 100 ? value.toFixed(0) : value.toFixed(magnitude >= 10 ? 1 : 2)
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
  description,
  series,
}: {
  title: string
  description: string
  series: LineSeries[]
}) {
  const chartId = useId()
  const values = series.flatMap((item) => item.points.map((point) => point.value))
  const [minY, maxY] = extent(values)
  const firstDate = series[0]?.points[0]?.date ?? "-"
  const lastDate = series[0]?.points.at(-1)?.date ?? "-"

  return (
    <div className="db-chart-shell">
      <div className="db-chart-heading">
        <div>
          <p className="db-kicker">Portfolio behavior</p>
          <h3>{title}</h3>
        </div>
        <div className="db-legend" aria-label="차트 범례">
          {series.map((item) => (
            <span key={item.label}><i style={{ background: item.color }} />{item.label}</span>
          ))}
        </div>
      </div>
      <svg
        className="db-line-chart"
        viewBox="0 0 100 100"
        role="img"
        aria-labelledby={`${chartId}-title ${chartId}-desc`}
        preserveAspectRatio="none"
      >
        <title id={`${chartId}-title`}>{title}</title>
        <desc id={`${chartId}-desc`}>{description}</desc>
        {[16, 34, 52, 70, 88].map((y) => (
          <line key={y} x1="8" x2="92" y1={y} y2={y} className="db-grid-line" />
        ))}
        {series.map((item) => (
          <path
            key={item.label}
            d={linePath(item.points, minY, maxY)}
            fill="none"
            stroke={item.color}
            strokeWidth="1.7"
            vectorEffect="non-scaling-stroke"
          />
        ))}
      </svg>
      <div className="db-chart-axis" aria-hidden="true">
        <span>{firstDate}</span>
        <span>{formatAxisValue(minY)} – {formatAxisValue(maxY)}</span>
        <span>{lastDate}</span>
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
      description="Python에서 같은 날짜로 정렬하고 100 기준으로 전달한 후보와 benchmark 누적 성과입니다."
      series={[
        { label: candidate.label, color: "#274764", points: candidate.points },
        { label: benchmark.label, color: "#269789", points: benchmark.points },
      ]}
    />
  )
}

export function UnderwaterChart({ series }: { series: DecisionBriefSeries }) {
  if (series.status !== "measured") {
    return <MissingChart title="Underwater drawdown" reason={series.missing_reason || "낙폭 curve가 없습니다."} />
  }
  return (
    <SvgLineChart
      title="Underwater drawdown"
      description="Python이 running peak 기준으로 계산해 전달한 drawdown과 recovery 경로입니다."
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
